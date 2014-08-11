from django.db import models

class User(models.Model):
	secret = models.CharField(max_length=30)
	is_admin = models.BooleanField(default=False)
	is_researcher = models.BooleanField(default=False)
	is_activated = models.BooleanField(default=False)
	date_created = models.DateTimeField(auto_now_add=True)

	def __unicode__(self):
		return u'%s'%(secret) if secret is not None else u'None'

class Project(models.Model):
	owner = models.ForeignKey(User)
	subject = models.CharField(default='', max_length=100)
	researchers = models.ManyToManyField(User)
	testees = models.ManyToManyField(User)
	date_created = models.DateTimeField(auto_now=True)

	def __unicode__(self):
		return u'%s by %s'%(subject, owner)

class Survey(models.Model):
	creater = models.ForeignKey(User)
	project = models.ForeignKey(Project)
	content = models.TextField(default='')
	date_created = models.DateTimeField(auto_now=True)

	def __unicode__(self):
		return u'%s @ %s'%(creater, date_created)

class Record(models.Model):
	testee = models.ForeignKey(User)
	date_created = models.DateTimeField(auto_now=True)
	survey = models.ForeignKey(Survey)
	reply = models.TextField(default='')
	
	def __unicode__(self):
		return u'%s @ %s'%(testee, date_created)

class Plan(models.Model):
	survey = models.ForeignKey(Survey)
	owner = models.ForeignKey(User)
	testee = models.ForeignKey(User)
	is_sent = models.BooleanField(default=False)
	is_done = models.BooleanField(default=False)
	schedule = models.TextField(default='')
	date_created = models.DateTimeField(auto_now=True)
	
	def __unicode__(self):
		return u'%s to %s @ %s'%(owner, testee, date_created)