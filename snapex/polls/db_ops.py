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
	'''
		user: string or list of string
	'''
	if type(user) == type(str()):
		user = [user]
	if type(user) == type(list()):
		ret = []
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
				ret.append(u)
		return 0, ret
	return 1, 'invalid input, string or list of string required'
	

def create_testee(user):
	'''
		user: string or list of string
	'''
	if type(user) == type(str()):
		user = [user]
	if type(user) == type(list()):
		ret = []
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
				ret.append(u)
		return 0, ret
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


def get_projects_from_researcher(rs):
	return rs.owner_projects


def get_testees_from_project(project):
	return project.testees_projects


def get_surveys_from_project(project):
	return project.project_surveys


def get_plans_from_project(project):
	return project.project_plans


def activate_user(secret):
	user = get_user_from_secret(secret)
	if user:
		user.is_active = True
		user.save()
		return 0
	else:
		return 1


# project
def create_project(owner, name, subject='', init=0, researchers=[]):
	# create new testees
	user_names = generate_uids(init)
	new_testees = None
	for i in range(3):
		st, new_testees = create_testee(user_names)
		if st==0:
			break
		else:
			user_names = generate_uids(init)
		if i==3:
			return 1, 'create project failed due to lack of available usernames'

	if not type(new_testees) == type(list()):
		return 1, 'create_testee failed'

	p = Project(owner=owner, name=name, subject=subject)
	p.save()
	for testee in new_testees:
		ptm = ProjectTesteeMembership(project=p, testee=testee, alias='')
		ptm.save()

	return 0, p


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
	