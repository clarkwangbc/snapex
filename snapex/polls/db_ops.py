from models import *

# user
def create_user(secret, is_admin=False, is_researcher=False, is_activated=False):
	user = User(secret=secret, 
					is_admin=is_admin, 
					is_researcher=is_researcher,
					is_activated=is_activated)
	user.save()
	

def create_admin():
	create_user(secret=u'19770707',
					is_admin=True,
					is_researcher=True,
					is_activated=True)


def create_researcher():
	import uuid
	secret = unicode(uuid.uuid1()
	create_user(secret=secret,
					is_researcher=True)
	return secret


def create_testees(number=10):
	import uuid
	if number<0:
		return
	secrets = [unicode(uuid.uuid1() for i in range(number)]
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


def add_testees_to_project(owner, subject, testees):
	'''
	testee: iterable of strings, secret of the new testees
	return: 0 if success; (1,msg) if failed
	'''
	pass


# survey
def create_survey(creater, project, content):
	'''
	creater: string, secret of a researcher
	project: string, subject of the project
	content: string, formatted survey content
	return: (0,survey_id) if success; (1,msg) if failed
	'''
	pass


# record
def create_record(testee, survey, reply):
	'''
	testee: string, secret of a testee
	survey: int, survey_id
	reply: string, formatted survey reply to the survey
	return: (0,record_id) if success; (1,msg) if failed
	'''
	pass


# plan
def create_plan(survey, owner, testee, is_sent=False, is_done=False, schedule):
	'''
	survey: int, survey_id
	owner: string, secret of the owner researcher
	testee: string, secret of the testee
	schedule: string, formatted schedule string
	return: (0,plan_id) if success; (1,msg) if failed
	'''
	pass