from models import *
from django.conf import settings
import uuid
from django.contrib.auth.models import User


def generate_uid():
	return str(uuid.uuid4())[:30]


def generate_uids(number):
	return [generate_uid() for x in range(number)]


def create_admin(username, password, device_id):
	u = User.objects.filter(username=username).exists()
	if u:
		return 1, 'username already exist'
	else:
		u = User(username=username, is_active=True, is_staff=True, is_superuser=True)
		u.set_password(password)
		u.save()
		up = UserProfile(user=u, is_admin=True, is_researcher=True, device_id=device_id)
		up.save()
		return 0, 'success'


def create_researcher(user):
	if type(user) == type(str()):
		user = [user]
	if type(user) == type(list()):
		for one_user in user:
			if type(one_user) != type(str()):
				return 1, 'invalid input'
			if User.objects.filter(username=one_user).exists():
				return 1, 'username already exists'
			else:
				u = User(username=one_user, is_active=False, is_staff=False, is_superuser=False)
				u.set_password(settings.DEFAULT_PASSWORD)
				u.save()
				up = UserProfile(user=u, is_admin=False, is_researcher=True, device_id='')
				up.save()
		return 0
	return 1, 'invalid input, string or list of string required'
	

def create_testee(user):
	if type(user) == type(str()):
		user = [user]
	if type(user) == type(list()):
		for one_user in user:
			if type(one_user) != type(str()):
				return 1, 'invalid input'
			if User.objects.filter(username=one_user).exists():
				return 1, 'username already exists'
			else:
				u = User(username=one_user, is_active=False, is_staff=False, is_superuser=False)
				u.set_password(settings.DEFAULT_PASSWORD)
				u.save()
				up = UserProfile(user=u, is_admin=False, is_researcher=False, device_id='')
				up.save()
		return 0
	return 1, 'invalid input, string or list of string required'


def get_user_from_secret(secret):
	objs = User.objects.filter(secret=secret)
	if objs.exists():
		return objs[0]
	else:
		return None
			

def get_plans_from_user(user):
	return user.testee_plans


def get_schedule_from_plan(plan):
	return plan.schedule


def get_project_from_plan(plan):
	return plan.project


def get_survey_from_plan(plan):
	return plan.survey


def activate_user(secret):
	user = get_user_from_secret(secret)
	if user:
		user.is_active = True
		user.save()
		return 0
	else:
		return 1


# project
def create_project(owner='', subject='', researchers=[], testees=[]):
	'''
	owner: string, secret of a owner user
	subject: string, subject of the project
	researchers: iterable of strings, secret of the researcher users
	testees: iterable of stirngs, secret of the testee users
	return: (0,project_id) if success; (1,msg) if failed
	'''
	# validate owner
	if owner=='':
		owner = create_researcher()
	else:
		if not User.objects.filter(secret=unicode(owner)).exists():
			return 1, 'owner user not exist'

	# validate researchers
	for r in researchers:
		if not User.objects.filter(secret=unicode(r)).exists():
			return 1, 'some researchers not exist'

	# validate testees
	for t in testees:
		if not User.objects.filter(secret=unicode(t)).exists():
			return 1, 'some testees not exist'

	owner_user = User.objects.get(secret=owner)
	project = Project(owner=owner_user, subject=subject)
	project.save()
	project.researchers.add(*User.objects.filter(secret__in=researchers))
	project.testees.add(*User.objects.filter(secret__in=testees))
	return 0, project.id


def add_testees_to_project(owner, project, testees):
	'''
	owner: string, secret of owner
	project: int, project_id 
	testee: iterable of strings, secret of the new testees
	return: 0 if success; (1,msg) if failed
	'''
	if not User.objects.filter(secret=unicode(owner)).exists():
		return 1, 'owner user not exist'

	if not Project.objects.filter(id=project).exists():
		return 1, 'project not exist'

	for t in testees:
		if not User.objects.filter(secret=unicode(t)).exists():
			return 1, 'some testees not exist'

	p = Project.objects.get(pk=project)
	p.testees.add(*testees)
	return 0

# survey
def create_survey(creater, project, content=''):
	'''
	creater: string, secret of a researcher
	project: string, subject of the project
	content: string, formatted survey content
	return: (0,survey_id) if success; (1,msg) if failed
	'''
	if not User.objects.filter(secret=unicode(creater)).exists():
		return 1, 'creater user not exist'

	if not Project.objects.filter(id=project).exists():
		return 1, 'project not exist'		

	s = Survey(creater=User.objects.get(secret=creater),
				project=Project.objects.get(pk=project),
				content=content)
	s.save()
	return 0, s.id


# record
def create_record(testee, survey, reply=''):
	'''
	testee: string, secret of a testee
	survey: int, survey_id
	reply: string, formatted survey reply to the survey
	return: (0,record_id) if success; (1,msg) if failed
	'''
	if not User.objects.filter(secret=unicode(testee)).exists():
		return 1, 'testee user not exist'

	if not Survey.objects.filter(id=survey).exists():
		return 1, 'survey not exist'

	r = Record(testee=User.objects.get(secret=testee),
				survey=Survey.objects.get(pk=survey),
				reply=reply)
	r.save()
	return 0, r.id


# plan
def create_plan(survey, owner, testee, is_sent=False, is_done=False, schedule=''):
	'''
	survey: int, survey_id
	owner: string, secret of the owner researcher
	testee: string, secret of the testee
	schedule: string, formatted schedule string
	return: (0,plan_id) if success; (1,msg) if failed
	'''
	if not User.objects.filter(secret=unicode(testee)).exists():
		return 1, 'testee user not exist'

	if not User.objects.filter(secret=unicode(owner)).exists():
		return 1, 'owner user not exist'

	if not Survey.objects.filter(id=survey).exists():
		return 1, 'survey not exist'

	p = Plan(survey=Survey.objects.get(pk=survey),
			owner=User.objects.get(secret=owner),
			testee=User.objects.get(secret=testee),
			is_sent=is_sent,
			is_done=is_done,
			schedule=schedule)
	p.save()
	return 0, p.id
	