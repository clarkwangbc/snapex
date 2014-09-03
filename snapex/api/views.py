from django.http import HttpResponse
import polls.utility as utility
from django.contrib.auth.models import User
from polls.models import *
from django.contrib.auth import authenticate, login, logout
from django.views.decorators.csrf import csrf_exempt
from django.conf import settings
from django.contrib.auth.decorators import login_required
import polls.db_ops as db_ops
import simplejson


@csrf_exempt
@utility.expose(rest=True)
def signin(req):
	if req.method == 'POST':
		if 'device_id' in req.POST:
			user = req.POST['device_id']
			secret = req.POST['secret']
			if User.objects.filter(username=secret).exists():
				u = User.objects.get(username=secret)
				# authenticate admin
				if u.is_superuser and 'device_id' in req.POST:
					user = authenticate(username=user, password=secret)
				# authenticate researcher and testee
				elif u.is_staff:
                    user = authenticate(username=user, password=secret)
                else:			
                    user = authenticate(username=user, password=settings.DEFAULT_PASSWORD)

			if user is not None and user.is_active:
				login(req, user)
				return 200, dict(msg='singin success')
		else:
			return 400, dict(msg='no secret in req.POST')
	return 400, dict(msg='invalid signin')


@csrf_exempt
@utility.expose(rest=True)
def signout(req):
	logout(req)
	return 200, dict(msg='signout success')


@csrf_exempt
@login_required
@utility.expose(rest=True)
def create_survey(req):
	if req.method=='POST':
		try:
			json_data = simplejson.loads(req.body)
			data = json_data['data']
			project_id = int(data['project_id'])
			survey_name = data['survey_name']
			surveys = data['fields']

			# only ownner of the project have permission to create survey
			user = req.user
			if not Project.objects.filter(owner=user, pk=project_id).exists():
				return 400, dict(msg='permission denied')

			project = db_ops.get_project_from_pk(project_id)
			# create survey
			survey = Survey(project=project, name=survey_name, raw_content=req.body)
			survey.save()
			# create question entries
			for rank, s in enumerate(surveys):
				qe = QuestionEntry(qtype=s['field_type'], content=simplejson.dumps(s))
				qe.save()
				sm = SurveyMembership(qentry=qe, survey=survey, entry_order=rank)
				sm.save()

			return 200, dict(msg='ok')
		except Exception as e:
			return 1001, dict(msg='json format error', verbose=str(e))


@csrf_exempt
@login_required
@utility.expose(rest=True)
def create_schedule(req):
	if req.method=='POST':
		try:
			json_data = simplejson.loads(req.body)
			events = json_data['data']
			schedule_name = json_data['schedule_name']
			user = req.user
			schedule = Schedule(name=schedule_name, content=simplejson.dumps(events), owner=user)
			schedule.save()

			return 200, dict(msg='ok')
		except Exception as e:
			return 1001, dict(msg='json format error', verbose=str(e))


@csrf_exempt
@utility.expose(rest=True)
def auth(req):
	'''
		Auth a testee and activate it
		input:
		{
			testee: 'testee_secret',
			device_id: 'unique device id'
		}
		output:
		{status: status, msg: 'msg'}
		200: ok
		1000: json format error
		1001: secret has been used
		1002: secret invalid
		test:
		curl "http://snapex.duapp.com/api/v0/auth" -d @body.txt
	'''
	if req.method=='POST':
		try:
			json_data = simplejson.loads(req.body)
			secret = json_data['testee']
			device_id = json_data['device_id']
			user = db_ops.get_user_from_secret(secret)
			if user is None:
				return 1002, dict(msg='secret invalid')
			if user.is_active:
				return 1001, dict(msg='secret has been used')

			user.is_active = True
			if device_id != '':
				user.user_profile.device_id = device_id
			user.save()
			return 200, dict(msg='ok')
		except Exception as e:
			return 1000, dict(msg='json format error')


@csrf_exempt
@utility.expose(rest=True)
def pull_plans(req):
	'''
		Pull all plans of a testee
		input:
		{
			testee: 'testee_secret'
		}
		output:
		{
			status: status,
			plans: [
				{
					id: plan_id,
					project_name: 'name of the project this plan belongs to',					
					survey: {
						survey_name: 'name of the survey'
						fields: [
							{
								label: 'the question',
								required: true or false // without quote, wheather media is required
								field_type: 'simple_question or hard_question or date', // three types
								field_options: { // always exists
									description: 'detailed description of the question' // may not exists
								}
							}, // different types of question
							{
								... // same
								field_type: 'single_choice or multi_choice', // two types
								field_options: {
									include_other_option: true or false,
									options: [ // order counts!
										{
											label: 'content of the option'
										}, // one option
									]
								}
							},
							{
								... // same
								field_type: 'l5 or l7', // two types
								field_options: {
									options: [ // order counts!
										{
											label: 'strongly disagree text'
										},
										{
											label: 'strongly agree text'
										} // only the first 2 options take effect here
									]
								}
							},

						]
					},
					schedule: [
						{
							msg: 'the msg for testee when alerted',
							start: '2014-08-17T12:00:00' // app shall alert randomly in [start, end]
							end: '2014-08-17T14:00:00' // time format: datetime isoformat
						}, // one alert
					]
				}, // a plan
			]
		}
		200: ok, with plans
		else: error, without plans
		test:
		curl "http://snapex.duapp.com/api/v0/pull_plans" -d @body.txt
	'''
	if req.method=='POST':
		try:			
			json_data = simplejson.loads(req.body)
			secret = json_data['testee']
			user = db_ops.get_user_from_secret(secret)
			if user is None:
				return 1002, dict(msg='secret invalid')
			if not user.is_active:
				return 1001, dict(msg='secret has not been activated')

			plans = []
			pls = user.testee_plans
			for pl in pls.all():
				ret = {}
				ret['id']=  pl.id
				ret['project_name'] = pl.project.name
				survey = simplejson.loads(pl.survey.raw_content)['data']
				ret['survey'] = survey
				ret['schedule'] = simplejson.loads(pl.schedule.content)
				pl.is_sent = True
				plans.append(ret)

			return 200, dict(msg='ok', plans=plans)
		except Exception as e:
			return 1000, dict(msg='json format error')


@csrf_exempt
@utility.expose(rest=True)
def report_media(req):
	'''
		Report a media url to server
		input:
		{
			uid: 'unique media id with max length of 100, may use device_id as a prefix',
			content: [
				{
					type: 'image' or 'sound or 'video',
					url: 'url of the media'
				}, // one media
			]
		}
		output:
		{status: status, msg: 'msg'}
		200: ok
		else: error
		test:
		curl "http://snapex.duapp.com/api/v0/report_media" -d @body.txt
	'''
	if req.method=='POST':
		try:
			json_data = simplejson.loads(req.body)
			uid = json_data['uid']
			if MediaEntry.objects.filter(uid=uid).exists():
				return 1001, dict(msg='uid already used')
			content = json_data['content']
			me = MediaEntry(uid=uid, content=simplejson.dumps(content))
			me.save()
			return 200, dict(msg='ok')
		except Exception as e:
			return 1000, dict(msg='json format error', verbose=str(e))

@csrf_exempt
@utility.expose(rest=True)
def report_record(req):
	'''
		Report a survey record
		input:
		{	
			pid: plan_id, 
			testee: 'testee_secret',
			data: {
				fields: [ // order counts!
					{
						field_type: 'field_type',
						reply: 'reply' // a string
						// simple/hard question: just the reply, e.g. 'text'
						// single/multi choice: number with spaces, e.g. '2 4 7'
						// l5/l7: the number choosed, e.g. '3' for l5; '7' for l7
						// if media included then: 'reply@@media:uid'
					},
				]
			}
		}
		output:
		{status: status, msg: 'msg'}
		200: ok
		else: error
		test:
		curl "http://snapex.duapp.com/api/v0/report" -d @body.txt
	'''
	if req.method=='POST':
		try:
			json_data = simplejson.loads(req.body)
			pid = json_data['pid']
			user_secret = json_data['testee']

			plan = db_ops.get_plan_from_pk(int(pid))
			user = db_ops.get_user_from_secret(user_secret)

			if not plan.testee==user:
				return 1002, dict(msg='permission denied')

			reply_entries = json_data['data']['fields']
			qms = plan.survey.survey_memberships.order_by('entry_order')

			if len(reply_entries) != len(qms):
				return 1003, dict(msg='record not matching survey')
			for re, qm in zip(reply_entries, qms):
				# check if their types
				if re['field_type'] != qm.qentry.qtype:
					return 1003, dict(msg='record not matching survey')

			record = Record(testee=user, plan=plan)
			record.save()

			for re, qm in zip(reply_entries, qms):
				ae = AnswerEntry(qentry=qm.qentry, record=record, content=simplejson.dumps(re))
				ae.save()

			plan.is_done = True

			return 200, dict(msg='ok')

		except Exception as e:
			return 1000, dict(msg='json format error', verbose=str(e))