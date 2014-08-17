from django.http import HttpResponse
from django.shortcuts import render
from django.contrib.auth.decorators import login_required
from django.contrib.auth.models import User
import polls.db_ops as db_ops
from django.shortcuts import redirect


@login_required
def mypage(req):
	# for researchers, display a default page
	if req.user.user_profile.is_researcher:
		return render(req, 'mypage/index.html', {'user_name': req.user.username})
	else:
		# for testees, direct them to their user page
		return HttpResponse('hi you testees')


@login_required
def myproject(req):
	if not req.user.user_profile.is_researcher:
		return redirect('mypage')

	q = req.GET
	action = q.get('action', None)
	if action is None:
		# view project
		return HttpResponse('view projects')
	elif action == 'create':
		# create project
		return HttpResponse('create projects')
	else:
		return HttpResponse('nothing projects')
		
	
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
	
