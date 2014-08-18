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
		# for researchers, display a default page
		if req.user.user_profile.is_researcher:
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
			return HttpResponse('hi you testees')
	
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
		return redirect('/mypage')

	q = req.GET
	pid = q.get('pid', None)
	if pid is None:
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

		elif action_type == 'new_schedule':
			pass
		elif action_type == 'new_survey':
			pass
		else:
			pass

		return redirect('/mypage/project?pid=%s'%(pid))		
	
@login_required
def q_user(req):
	user = req.user
	ret = {'user_name': user.username, 'user_plans':[]}
	if 'secret' in req.GET:
		user = db_ops.get_user_from_secret(req.GET['secret'])
		if user:
			ret['user_name'] = secret
		else:
			return render(req, 'mypage/user.html', {'user_name':secret, 'user_plans':[]})

	plans = db_ops.get_plans_from_user(user)
	for plan in plans:
		project = db_ops.get_project_from_plan(plan)
		survey = db_ops.get_survey_from_plan(plan)
		schedule = db_ops.get_schedule_from_plan(plan)
		d = dict(survey_name=survey.name, project_name=project.name, schedule_name=schedule.name)
		ret['user_plans'].append(d)

	return render(req, 'mypage/user.html', ret)
	
