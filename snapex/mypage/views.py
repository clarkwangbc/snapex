from django.http import HttpResponse
from django.shortcuts import render
from django.contrib.auth.decorators import login_required
from django.contrib.auth.models import User
import polls.db_ops as db_ops
from django.shortcuts import redirect
from django.views.decorators.csrf import csrf_exempt
from polls.models import *


@csrf_exempt
@login_required
def mypage(req):
	if req.method == 'GET':	
		# TODO: direct admins to an all plan page?
		if req.user.is_superuser:
			return redirect('/mypage/project')
		# for researchers, display a default page
		elif req.user.user_profile.is_researcher:
			ret = {'user_name': req.user.username}
			projects = db_ops.get_projects_from_researcher(req.user)
			p = []
			for project in projects:
				pinfo = {}
				testees = db_ops.get_testees_from_project(project)
				surveys = db_ops.get_surveys_from_project(project)
				plans = db_ops.get_plans_from_project(project)

				pinfo['name'] = project.name
				# TODO: using django model filtering
				pinfo['all_user'] = len(testees)
				pinfo['active_user'] = sum(x.is_active==True for x in testees)
				pinfo['surveys'] = len(surveys)
				pinfo['plans'] = len(plans)
				pinfo['url'] = '/mypage/project?pid=%s'%(project.id)

				p.append(pinfo)

			ret['projects'] = p
			return render(req, 'mypage/index.html', ret)
		else:
			# for testees, direct them to their user page
			# return HttpResponse('hi you testees')
			return redirect('/mypage/project')
	
	elif req.method == 'POST':
		if req.user.user_profile.is_researcher:
			project_name = req.POST.get('project_name', None)
			project_subject = req.POST.get('project_subject', None)
			init_testees = req.POST.get('init_testees', None)
			init_testees = int(init_testees) if init_testees else None
			if project_name and project_subject and (init_testees is not None):
				db_ops.create_project(owner=req.user, 
										subject=project_subject,
										name=project_name, 
										init=init_testees)
		return redirect('/mypage')


@csrf_exempt
@login_required
def myproject(req):
	if not req.user.user_profile.is_researcher:
		if req.method=='GET':
			user = req.user
			plans = Plan.objects.filter(testee=user).all()
			return render(req, 'mypage/testee.html', {'plans':plans})
		else:
			return HttpResponse('invalid method')

	if req.user.is_superuser:
		if req.method=='GET':
			plans = Plan.objects.all()
			return render(req, 'mypage/testee.html', {'plans':plans})
		else:
			return HttpResponse('invalid method')		

	q = req.GET
	pid = q.get('pid', None)
	if pid is None or pid=='':
		return HttpResponse('need a pid')

	if req.method=='GET':
		action = q.get('action', None)	

		# default: view project
		if action is None:
			ret = {}
			project = Project.objects.get(pk=int(pid))
			ret['project'] = project

			t = []
			testees = db_ops.get_testees_from_project(project)
			for testee in testees:
				tinfo = {}
				tinfo['name'] = testee.username
				tinfo['is_active'] = testee.is_active
				pls = Plan.objects.filter(testee=testee, project=project)
				tinfo['plan_count'] = pls.count()
				tinfo['record_count'] = Record.objects.filter(plan__in=pls).count()
				t.append(tinfo)
			ret['testees'] = t
			ret['surveys'] = Survey.objects.filter(project=project).all()
			ret['schedules'] = Schedule.objects.filter(owner=req.user).all()
			ret['plans'] = Plan.objects.filter(project=project).all()
			return render(req, 'mypage/project.html', ret)
		elif action == 'push_plan':
			# push plan
			return HttpResponse('create projects')
		else:
			return HttpResponse('nothing projects')

	elif req.method=='POST':
		action_type = req.POST.get('action_type', None)
		if action_type == 'new_user':
			user_secret = req.POST.get('user_secret', None)
			user_number = req.POST.get('user_number', None)
			if user_secret is not None and user_number is not None:
				p = Project.objects.get(pk=int(pid))
				if user_secret != '':
					u = db_ops.get_user_from_secret(user_secret)
					if u and p:
						db_ops.add_testee_to_project(u, p)
				else:
					user_number = int(user_number)
					st, new_testees = db_ops.create_new_testees(user_number)
					if st == 0:
						for testee in new_testees:
							db_ops.add_testee_to_project(testee, p)

		elif action_type == 'new_plan':
			plan_testee = req.POST.get('plan_testee', None)
			plan_survey = req.POST.get('plan_survey', None)
			plan_schedule = req.POST.get('plan_schedule', None)
			if plan_testee is not None and plan_survey is not None and plan_schedule is not None:
				user = req.user
				testee = db_ops.get_user_from_secret(plan_testee)
				survey = db_ops.get_survey_from_pk(int(plan_survey))
				schedule = db_ops.get_schedule_from_pk(int(plan_schedule))
				project = Project.objects.get(pk=int(pid))

				if not project.owner==user:
					return HttpResponse('permission denied')

				if testee and survey and schedule and project:
					plan = Plan(survey=survey, owner=user, 
						testee=testee, project=project, schedule=schedule)
					plan.save()
					from django.conf import settings
					if settings.PUSH_ON_TIME:
						db_ops.send_plan(plan)

		return redirect('/mypage/project?pid=%s'%(pid))		
	

@login_required
def mysurvey(req):
	action = req.GET.get('action', None)
	pid = req.GET.get('pid', None)
	sid = req.GET.get('sid', None)

	if action is None:
		return HttpResponse("action can't be blank")

	user = req.user
	
	if req.method == 'GET':
		if pid is None or pid == '':
			return HttpResponse("pid can't be blank")
		project = db_ops.get_project_from_pk(int(pid))
		if project is None:
			return HttpResponse('invalid pid')
		
		if action == 'create': # a survey creating page
			return render(req, 'mypage/survey_create.html', 
				{'project': project, 'create_survey': 1, 'raw_survey': []})
					
		elif action == 'view': # a survey displaying page
			if sid is None or sid=='':
				return HttpResponse("sid can't be blank")
			survey = db_ops.get_survey_from_pk(int(sid))
			if survey is None:
				return HttpResponse('invalid sid')
			import simplejson
			survey_content = simplejson.dumps(simplejson.loads(survey.raw_content)['data']['fields'])
			from django.utils.safestring import mark_safe
			return render(req, 'mypage/survey_create.html',
				{'project': project, 'create_survey': 0, 
				'survey_name': survey.name,
				'raw_survey': mark_safe(survey_content)})	

	elif req.method == 'POST':
		# post a survey creating form?
		return HttpResponse('post test')


def myschedule(req):
	action = req.GET.get('action', None)
	pid = req.GET.get('pid', None)
	sid = req.GET.get('sid', None)

	if action is None:
		return HttpResponse("action can't be blank")

	user = req.user

	if req.method == 'GET':
		if action == 'create': # a schedule creating page
			if pid is None or pid=='':
				return HttpResponse("pid can't be blank")
			project = db_ops.get_project_from_pk(int(pid))
			if project is None:
				return HttpResponse('invalid pid')
			import datetime
			return render(req, 'mypage/schedule_create.html', 
				{'project': project, 'create_schedule': 1, 
				'events': [], 'schedule_start': datetime.date.today().isoformat()})
					
		elif action == 'view': # a schedule displaying page
			if sid is None or sid=='':
				return HttpResponse("sid can't be blank")
			schedule = db_ops.get_schedule_from_pk(int(sid))
			if schedule is None:
				return HttpResponse('invalid sid')
			import simplejson
			import dateutil.parser
			schedule_content = simplejson.loads(schedule.content)
			from django.utils.safestring import mark_safe
			return render(req, 'mypage/schedule_create.html',
				{'create_schedule': 0, 
				'schedule_name': mark_safe(schedule.name),
				'events': mark_safe(schedule.content),
				'schedule_start': min([dateutil.parser.parse(x['start']) for x in schedule_content]).date().isoformat()})	

	elif req.method == 'POST':
		# post a schedule creating form?
		return HttpResponse('post test')


@login_required
def myrecord(req):
	rid = req.GET.get('rid', None)
	if rid is None or rid=='':
		return HttpResponse("rid can't be blank")

	# permission: for everyone logged in

	record = db_ops.get_record_from_pk(int(rid))
	if not record:
		return HttpResponse('invalid rid')

	# simple_question
	template_simple_question = '<div>question: %s</div><div>description: %s</div><div>answer: %s</div>'
	template_hard_question = '<div>question: %s</div><div>description: %s</div><div>answer: %s</div>'
	template_single_choice = '<div>question: %s</div><div>description: %s</div><div>answer: %s</div>'
	template_multi_choice = '<div>question: %s</div><div>description: %s</div><div>answer: %s</div>'
	template_l5 = '<div>question: %s</div><div>description: %s</div><div>answer: %s</div>'
	template_l7 = '<div>question: %s</div><div>description: %s</div><div>answer: %s</div>'
	template_date = '<div>question: %s</div><div>description: %s</div><div>answer: %s</div>'

	i_html = ''

	for ae in record.record_aentries.all():
		entry_type = ae.qentry.qtype
		import simplejson
		data = simplejson.loads(ae.qentry.content)
		question = data['label']
		description = data['field_options']#.get('description', '')
		media = data['required']
		reply_data = simplejson.loads(ae.content)
		reply = reply_data['reply']
		
		if entry_type=='simple_question':
			i_html += template_simple_question%(question, description, reply) + '<br>'
		elif entry_type=='hard_question':
			i_html += template_hard_question%(question, description, reply) + '<br>'
		elif entry_type=='single_choice':
			i_html += template_single_choice%(question, description, reply) + '<br>'
		elif entry_type=='multi_choice':
			i_html += template_multi_choice%(question, description, reply) + '<br>'
		elif entry_type=='l5':
			i_html += template_l5%(question, description, reply) + '<br>'
		elif entry_type=='l7':
			i_html += template_l7%(question, description, reply) + '<br>'
		elif entry_type=='date':
			i_html += template_date%(question, description, reply) + '<br>'

	from django.utils.safestring import mark_safe
	return render(req, 'mypage/record.html', {'record': mark_safe(i_html)})
	