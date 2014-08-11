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
	create_user(secret=unicode(uuid.uuid1()),
					is_researcher=True)

def create_testees(number=10):
	import uuid
	for i in range(number):
		create_user(secret=unicode(uuid.uuid1()))

# project
def create_project(owner, subject, 	researchers, testees):
	pass
