from django.db import models
from django.contrib.auth.models import User


# class Config(models.Model):
# use settings.PUSH_ON_TIME instead
#     push_on_time = models.BooleanField(default=True)


class UserProfile(models.Model):
    user = models.OneToOneField(User, related_name='user_profile')
    device_id = models.CharField(max_length=100) # 'user_id, channel_id'
    qr_code = models.CharField(max_length=200)
    is_admin = models.BooleanField(default=False)
    is_researcher = models.BooleanField(default=False)
    
    telephone = models.CharField(max_length=15)
    organization = models.CharField(max_length=100)
    others = models.TextField()
    remarks = models.CharField(max_length=100) # Remarks
    
    def __unicode__(self):
#        return u'%s'%(secret) if secret is not None else u'None'
        return u"%s's profile" % self.user

    def __str__(self):
        return "%s's profile" % self.user


class Project(models.Model):
    owner = models.ForeignKey(User, related_name='owner_projects')
    testees = models.ManyToManyField(User, 
                    through='ProjectTesteeMembership',
                    related_name='testees_projects')
    name = models.CharField(max_length=50)
    code = models.CharField(max_length=4)
    subject = models.CharField(default='', max_length=100)
    date_created = models.DateTimeField(auto_now=True)
    others = models.TextField() # other information or extensions
    md5 = models.CharField(max_length=128) # support maximum MD5 128
    
    def __unicode__(self):
        return u'%s by %s'%(subject, owner)


class Survey(models.Model):
    sid = models.CharField(max_length=20)
    project = models.ForeignKey(Project, related_namQuee='project_surveys')
    code = models.CharField(max_length=4)
    logo = models.CharField(max_length=100)
    questions = models.ManyToManyField(QuestionEntry, 
                    through='SurveyMembership', 
                    related_name='questions_surveys')

    name = models.CharField(max_length=50)
    raw_content = models.TextField() # stored raw json of all the survey
    date_created = models.DateTimeField(auto_now=True)
    others = models.TextField()
    md5 = models.CharField(max_length=128) # support maximu MD5 128
    
    def __unicode__(self):
        return u'%s @ %s'%(creater, date_created)


class QuestionEntry(models.Model):
    qtype = models.CharField(max_length=20)
    required = models.BooleanField(default=False)
    description = models.CharField(max_length=100)
    options = models.CharField(max_length=200)
    question = models.CharField(max_length=50)
    code = models.CharField(max_length=4)
    content = models.TextField() # json
    others = models.TextField() # other information


class ProjectTesteeMembership(models.Model):
    project = models.ForeignKey(Project, related_name='project_testee_memberships')
    testee = models.ForeignKey(User, related_name='testee_project_memberships')

    alias = models.CharField(max_length=50) # testee alias in each project
    

class SurveyMembership(models.Model):
    qentry = models.ForeignKey(QuestionEntry, related_name='question_memberships')
    survey = models.ForeignKey(Survey, related_name='survey_memberships')
    
    entry_order = models.IntegerField(default=0) # used to store qentry order in each survey
    
    class Meta:
        ordering = ('entry_order',)


class Schedule(models.Model):
    owner = models.ForeignKey(User, related_name='owner_schedules')

    name = models.CharField(max_length=50)
    content = models.TextField(default='') # json
    date_created = models.DateTimeField(auto_now=True)
    md5 = models.CharField(max_length=128)


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
    
    date_created = models.DateTimeField()
    date_uploaded = models.DateTimeField(auto_now=True)

    def __unicode__(self):
        return u'%s @ %s'%(testee, date_created)


class AnswerEntry(models.Model):
    qentry = models.ForeignKey(QuestionEntry, related_name='question_aentries')
    record = models.ForeignKey(Record, related_name='record_aentries')
    
    content = models.TextField() # raw content


class MediaEntry(models.Model):
    uid = models.CharField(max_length=100)
    content = models.TextField() # json