from django.db import models

class User(models.Model):
	secret = models.CharField(max_length=40)
	device_id = models.CharField(max_length=100)
	is_admin = models.BooleanField(default=False)
	is_researcher = models.BooleanField(default=False)
	is_activated = models.BooleanField(default=False)
	date_created = models.DateTimeField(auto_now_add=True)

	def __unicode__(self):
		return u'%s'%(secret) if secret is not None else u'None'

class Project(models.Model):
	owner = models.ForeignKey(User, related_name='project_owner')
	subject = models.CharField(default='', max_length=100)
	researchers = models.ManyToManyField(User, related_name='project_researchers')
	testees = models.ManyToManyField(User, related_name='project_testees')
	date_created = models.DateTimeField(auto_now=True)

	def __unicode__(self):
		return u'%s by %s'%(subject, owner)

class Survey(models.Model):
	creater = models.ForeignKey(User, related_name='survey_creater')
	project = models.ForeignKey(Project, related_name='survey_project')
	content = models.TextField(default='')
	date_created = models.DateTimeField(auto_now=True)

	def __unicode__(self):
		return u'%s @ %s'%(creater, date_created)

class Record(models.Model):
	testee = models.ForeignKey(User, related_name='record_testee')
	date_created = models.DateTimeField(auto_now=True)
	survey = models.ForeignKey(Survey, related_name='record_survey')
	reply = models.TextField(default='')
	
	def __unicode__(self):
		return u'%s @ %s'%(testee, date_created)

class Plan(models.Model):
	survey = models.ForeignKey(Survey, related_name='plan_survey')
	owner = models.ForeignKey(User, related_name='plan_owner')
	testee = models.ForeignKey(User, related_name='plan_testee')
	is_sent = models.BooleanField(default=False)
	is_done = models.BooleanField(default=False)
	schedule = models.TextField(default='')
	date_created = models.DateTimeField(auto_now=True)
	
	def __unicode__(self):
		return u'%s to %s @ %s'%(owner, testee, date_created)