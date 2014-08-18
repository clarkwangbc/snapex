from django.db import models
from django.contrib.auth.models import User


class UserProfile(models.Model):
	device_id = models.CharField(max_length=100)
	is_admin = models.BooleanField(default=False)
	is_researcher = models.BooleanField(default=False)
	
	user = models.OneToOneField(User, related_name='user_profile')

	def __unicode__(self):
		return u'%s'%(secret) if secret is not None else u'None'

	def __str__(self):
		return "%s's profile" % self.user  


class Project(models.Model):
	owner = models.ForeignKey(User, related_name='owner_projects')
	# researchers = models.ManyToManyField(User, related_name='researchers_projects')
	testees = models.ManyToManyField(User, 
					through='ProjectTesteeMembership',
					related_name='testees_projects')
	
	name = models.CharField(max_length=50)
	subject = models.CharField(default='', max_length=100)
	date_created = models.DateTimeField(auto_now=True)

	def __unicode__(self):
		return u'%s by %s'%(subject, owner)


class ProjectTesteeMembership(models.Model):
	project = models.ForeignKey(Project, related_name='project_testee_memberships')
	testee = models.ForeignKey(User, related_name='testee_project_memberships')

	alias = models.CharField(max_length=50) # testee alias in each project


class QuestionEntry(models.Model):
	qtype = models.CharField(max_length=20)
	content = models.TextField() # json


class Survey(models.Model):
	# creater = models.ForeignKey(User, related_name='creater_surveys')
	project = models.ForeignKey(Project, related_name='project_surveys')
	questions = models.ManyToManyField(QuestionEntry, 
					through='SurveyMembership', 
					related_name='questions_surveys')

	name = models.CharField(max_length=50)
	raw_content = models.TextField() # stored raw json of all the survey
	date_created = models.DateTimeField(auto_now=True)
	
	def __unicode__(self):
		return u'%s @ %s'%(creater, date_created)


class SurveyMembership(models.Model):
	qentry = models.ForeignKey(QuestionEntry, related_name='question_memberships')
	survey = models.ForeignKey(Survey, related_name='survey_memberships')

	entry_order = models.IntegerField(default=0) # used to store qentry order in each survey


class Schedule(models.Model):
	owner = models.ForeignKey(User, related_name='owner_schedules')

	name = models.CharField(max_length=50)
	content = models.TextField(default='') # json
	date_created = models.DateTimeField(auto_now=True)


class Plan(models.Model):
	survey = models.ForeignKey(Survey, related_name='survey_plans')
	owner = models.ForeignKey(User, related_name='owner_plans')
	testee = models.ForeignKey(User, related_name='testee_plans')
	project = models.ForeignKey(Project, related_name='project_plans')
	schedule = models.ForeignKey(Schedule, related_name='schedule_plans')

	is_sent = models.BooleanField(default=False)
	is_done = models.BooleanField(default=False)
	date_created = models.DateTimeField(auto_now=True)
	
	def __unicode__(self):
		return u'%s to %s @ %s'%(owner, testee, date_created)


class Record(models.Model):
	testee = models.ForeignKey(User, related_name='testee_records')
	plan = models.ForeignKey(Plan, related_name='plan_records')
	
	date_created = models.DateTimeField(auto_now=True)

	def __unicode__(self):
		return u'%s @ %s'%(testee, date_created)


class AnswerEntry(models.Model):
	qentry = models.ForeignKey(QuestionEntry, related_name='question_aentries')
	record = models.ForeignKey(Record, related_name='record_aentries')
	
	content = models.TextField() # json
