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
		if 'secret' in req.POST:
			user = None
			secret = req.POST['secret']
			if User.objects.filter(username=secret).exists():
				u = User.objects.get(username=secret)
				# authenticate admin
				if u.is_superuser and 'device_id' in req.POST:
					user = authenticate(username=secret, password=req.POST['device_id'])
				# authenticate researcher and testee
				else:
					user = authenticate(username=secret, password=settings.DEFAULT_PASSWORD)

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

