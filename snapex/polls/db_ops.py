from models import *

def create_uid():
	import uuid
	return str(uuid.uuid4())[:30]

# user
def create_user(secret, device_id='0', is_admin=False, is_researcher=False, is_activated=False):
	user = User(secret=secret,
					device_id=device_id,
					is_admin=is_admin, 
					is_researcher=is_researcher,
					is_activated=is_activated)
	user.save()
	

def create_admin():
	create_user(secret=u'19770707',
					device_id='19770707',
					is_admin=True,
					is_researcher=True,
					is_activated=True)


def create_researcher():
	import uuid
	secret = unicode(uuid.uuid1())
	create_user(secret=secret,
					is_researcher=True)
	return secret


def create_testees(number=10):
	import uuid
	if number<0:
		return
	secrets = [unicode(uuid.uuid1()) for i in range(number)]
	for s in secrets:
		create_user(secret=s)
	return secrets


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
	