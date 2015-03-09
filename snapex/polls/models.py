from django.db import models
from django.contrib.auth.models import User
from store import BAEStorage
from snapex.settings import BCS_SETTINGS
import simplejson

# class Config(models.Model):
# use settings.PUSH_ON_TIME instead
#     push_on_time = models.BooleanField(default=True)

GENDER_TYPES=(
    ("M", "Male"),
    ("F", "Female"),
)

PAGE_TYPES=(
    ("TextField", "Text Field Input Page"), # Page contains one textfield for maximum
    ("LikertScale", "Likert-Scale Questions Page"), # Page contains 3 likerscale questions for maximum
    ("SimpleText", "Simple Text Input Page"), # Support for multiple choices, date/time pickers, simple textbox, etc. 3/page maximum
    ("PhotoInput", "Photo Input Page"), # You can take a photo. 1/page
    ("AudioInput", "Audio Input Page"), # You can take an audio clip. 1/page
)

QUESTION_TYPES=(
    # Text Field Input Page Held Question Type
    ("TextField", "Text Field Input"), # Textfield
    
    # Likert Scale Page Held Question Type
    ("7LikertScale", "7 Likert-Scale Question"),
    ("5LikertScale", "5 Likert-Scale Question"),
    ("LikertScale", "Likert-Scale Question"), # User can specify the number of choices with NUMBER_OF_SCALES=10 for example in others
    
    # Simple Text Page Held Question Type
    ("SimpleText", "Simple Text Input"), # A simple Textbox input
    ("MultipleChoice", "Multiple Choice Input for Single Selection"), # Select one
    ("MultipleSelect", "Multiple Choice Input for Mulitple Selection"), # Select one or more
    ("DateInput", "Date Input"),
    ("TimeInput", "Time Input"),
    ("DateTimeInput", "Date Time Input"), # Date + Time
    
    # Photo Input Page Held
    ("PhotoInput", "Photo Input"),
    
    # Audio Input Page Held
    ("AudioInput", "Audio Input"),
)

class UserProfile(models.Model):
    uid = models.CharField(max_length=30, 
                    unique=True,
                    editable=False
                    ) # 30 digit id (different from pk)
    user = models.OneToOneField(User, related_name='user_profile')
    device_id = models.CharField(max_length=100,
                    blank=True
                    ) # 'user_id, channel_id'
    qr_code = models.CharField(max_length=200) # generated string for QR code scanning
    is_admin = models.BooleanField(default=False) # if a certain user is admin
    is_researcher = models.BooleanField(default=False) # @depreciated
    telephone = models.CharField(max_length=15,
                    blank=True
                    ) # Telephone number with country code
    others = models.TextField(
                    blank=True,
                    help_text="Other Settings of the project: Keys and its values"
                    ) # For extension uses
    remarks = models.CharField(
                    max_length=100,
                    blank=True
                    ) # Remarks
    
    def __unicode__(self):
#        return u'%s'%(secret) if secret is not None else u'None'
        return u"%s's profile" % (self.user)

    def __str__(self):
        return "%s's profile" % (self.user)

class Testee(User):
    # Extra fields for geografical information
    gender = models.CharField(max_length=1, blank=True, null=True,
        choices=GENDER_TYPES, default=None) # "M" for male or "F" for Female
    age = models.PositiveSmallIntegerField(blank=True, null=True) # Age of the participants
    occupation = models.CharField(max_length=40, blank=True, null=True) # Maximum 40 Characters
    education = models.CharField(max_length=40, blank=True, null=True, 
        verbose_name='Level of Education') # Level of Education for example High School, Bachelor, Master, Doctor, etc
    qr_image = models.ImageField(upload_to="/qr_code", storage=BAEStorage(bucket=BCS_SETTINGS["BUCKET_LIST"]["image"]))

    def __unicode__(self):
        return u"Testee: %s" % self.username

    def profileAttrSetter(attr):
        def set_any(self, value):
            return setattr(self.user_profile, attr, value)
        return set_any

    def profileAttrGetter(attr):
        def get_any(self):
            return getattr(self.user_profile, attr)
        return get_any

    uid = property(fget=profileAttrGetter('uid'), fset=profileAttrSetter('uid'))
    device_id = property(fget=profileAttrGetter('device_id'), fset=profileAttrSetter('device_id'))
    qr_code = property(fget=profileAttrGetter('qr_code'), fset=profileAttrSetter('qr_code'))
    telephone = property(fget=profileAttrGetter('telephone'), fset=profileAttrSetter('telephone'))
    others = property(fget=profileAttrGetter('others'), fset=profileAttrSetter('others'))
    remarks = property(fget=profileAttrGetter('remarks'), fset=profileAttrSetter('remarks'))

    def save(self, *args, **kwargs):
        super(Testee, self).save(*args, **kwargs)
        if hasattr(self, "user_profile") and self.user_profile is not None:
            self.user_profile.save()



class Researcher(User):
    # Researcher extra information
    organiztion = models.CharField(max_length=80, blank=True, null=True) # Organization of the researcher

    def profileAttrSetter(attr):
        def set_any(self, value):
            return setattr(self.user_profile, attr, value)
        return set_any

    def profileAttrGetter(attr):
        def get_any(self):
            return getattr(self.user_profile, attr)
        return get_any

    uid = property(fget=profileAttrGetter('uid'), fset=profileAttrSetter('uid'))
    device_id = property(fget=profileAttrGetter('device_id'), fset=profileAttrSetter('device_id'))
    qr_code = property(fget=profileAttrGetter('qr_code'), fset=profileAttrSetter('qr_code'))
    telephone = property(fget=profileAttrGetter('telephone'), fset=profileAttrSetter('telephone'))
    others = property(fget=profileAttrGetter('others'), fset=profileAttrSetter('others'))
    remarks = property(fget=profileAttrGetter('remarks'), fset=profileAttrSetter('remarks'))
    is_admin = property(fget=profileAttrGetter('is_admin'), fset=profileAttrSetter('is_admin'))
    is_researcher = property(fget=profileAttrGetter('is_researcher'), fset=profileAttrSetter('is_researcher'))
    
    def save(self, *args, **kwargs):
        super(Testee, self).save(*args, **kwargs)
        if hasattr(self, "user_profile") and self.user_profile is not None:
            self.user_profile.save()
    
    def __unicode__(self):
        return u"%s" % (self.username)

class Project(models.Model):
    pid = models.CharField(max_length=30, 
                    unique=True,
                    editable=False
                    ) # 30 digit id (different from pk)
    owner = models.ForeignKey(Researcher, related_name='owner_projects')
    coordinator = models.ManyToManyField(Researcher, 
                    through='ProjectResearcherMembership',
                    related_name='participated_projects',
                    verbose_name='Coordinate Researchers'
                    ) # Coordinate researchers of the project
    testees = models.ManyToManyField(Testee, 
                    through='ProjectTesteeMembership',
                    related_name='testees_projects'
                    ) # testees of the projects
    name = models.CharField(max_length=50,
                    help_text='Better no longer than 30 characters'
                    ) # Project name
    code = models.CharField(max_length=4,
                    help_text='Please specify a 4 digit project code'
                    ) # 4 digit user specified project code, for example TS01
    subject = models.CharField(default='', 
                    max_length=100,
                    help_text='Subject of the text should be no longer than 100 characters'
                    ) # subject fo the project
    organization = models.CharField(default='',
                    max_length=100,
                    help_text='Please speicify the organization responsible for the project'
                    ) # orgnization
    date_created = models.DateTimeField(auto_now=True) # creation date and time
    date_start = models.DateField(
                    blank=True,
                    help_text='Start date of the project'
                    ) # date in which the project starts
    date_end = models.DateField(
                    blank=True,
                    help_text='End date of the project'
                    ) # date in which the project ends
    others = models.TextField(
                    blank=True,
                    verbose_name='Other Project Settings',
                    help_text='Other keys and values (for extensions)'
                    ) # other information or extensions
    md5 = models.CharField(
                    max_length=128,
                    editable=False,
                    help_text='md5 to compare two versions of projects'
                    ) # support maximum MD5 128
    
    def add_testee(self, testee):
        if type(testee) == Testee:
            m = ProjectTesteeMembership(project=self, testee=testee)
            m.save()
            return 0
        else:
            return 1 # Invalid Input
    
    def add_researcher(self, researcher):
        if type(researcher) == Researcher:
            m = ProjectResearcherMembership(project=self, testee=testee)
            m.save()
            return 0
        else:
            return 1 # Invalid Input
    
    def __unicode__(self):
        return u'Project %s' % (self.code)
    


class QuestionEntry(models.Model):
    qtype = models.CharField(max_length=20,
                    choices=QUESTION_TYPES)
    required = models.BooleanField(default=False)
    description = models.CharField(max_length=100,
                    blank=True)
    options = models.CharField(max_length=200,
                    blank=True)
    question = models.CharField(max_length=1000,
                    help_text='text label')
    code = models.CharField(max_length=4,
                    help_text='Please Speicify a 4 digit code')
    content = models.TextField() # json
    others = models.TextField() # other information
    
    def __unicode__(self):
        return u'%s'% (self.code)

class Survey(models.Model):
    sid = models.CharField(max_length=30, 
                    unique=True,
                    editable=False)
    project = models.ForeignKey(Project, related_name='project_surveys')
    code = models.CharField(max_length=4,
                    help_text='Please Speicify a 4 digit code'
                    ) # 4 Digit Code
    logo = models.CharField(
                    max_length=100
                    ) # logo of the field
    questions = models.ManyToManyField(QuestionEntry, 
                    through='SurveyMembership', 
                    related_name='questions_surveys')
    name = models.CharField(max_length=50)
    raw_content = models.TextField() # stored raw json of all the survey, @depreciated
    date_created = models.DateTimeField(auto_now=True)
    others = models.TextField()
    md5 = models.CharField(max_length=128) # support maximu MD5 128
    
    def __unicode__(self):
        return u'%s @ %s' % (self.project, self.date_created)
        
    def questions(self):
        array = []
        for page in self.survey_pages.all():
            array.extend(page.questions.all())
        return array

    # To be used for web app
    def to_raw_content(self):
        ret = {}
        ret["survey_name"] = self.name
        ret["fields"] =[]
        for question in self.questions():
            question_dict = {}
            question_dict["label"] = question.question
            question_dict["field_type"] = question.qtype
            question_dict["field_options"] = {}
            question_dict["field_options"]["description"] = question.description
            if question.options != None and question.options != "":
                question_dict["field_options"]["options"] = []
                options_array = simplejson.loads(question.options)
                for option in options_array:
                    question_dict["field_options"]["options"].append({"label":option})
                    pass
            ret["fields"].append(question_dict)
        return ret

class Page(models.Model):
    ptype = models.CharField(max_length=20,
                    choices=PAGE_TYPES)
    page_no = models.IntegerField(default=0)
    survey = models.ForeignKey(Survey, related_name='survey_pages')
    questions = models.ManyToManyField(QuestionEntry, 
                    through='PageMembership',
                    related_name='questions_pages')
    class Meta:
        ordering = ('page_no',)

class ProjectResearcherMembership(models.Model):
    project = models.ForeignKey(Project, related_name='project_researcher_memberships')
    researcher = models.ForeignKey(Researcher, related_name='project_researcher_memberships')
    
    alias = models.CharField(max_length=50) # researcher alias in each project


class ProjectTesteeMembership(models.Model):
    project = models.ForeignKey(Project, related_name='project_testee_memberships')
    testee = models.ForeignKey(Testee, related_name='testee_project_memberships')

    alias = models.CharField(max_length=50) # testee alias in each project


class SurveyMembership(models.Model):
    qentry = models.ForeignKey(QuestionEntry, related_name='question_memberships')
    survey = models.ForeignKey(Survey, related_name='survey_memberships')
    
    entry_order = models.IntegerField(default=0) # used to store qentry order in each survey
    
    class Meta:
        ordering = ('entry_order',)


class PageMembership(models.Model):
    qentry = models.ForeignKey(QuestionEntry, related_name='question_memberships_to_pages')
    page = models.ForeignKey(Page, related_name='page_membership_to_questions')
    
    entry_order = models.IntegerField(default=0)
    
    class Meta:
        ordering = ('entry_order',)


class Schedule(models.Model):
    cid = models.CharField(max_length=30, unique=True)
    project = models.ForeignKey(Project, related_name='project_schedules')
    name = models.CharField(max_length=50)
    content = models.TextField(default='') # json
    date_created = models.DateTimeField(auto_now=True)
    md5 = models.CharField(max_length=128)
    

class Plan(models.Model):
    survey = models.ForeignKey(Survey, related_name='survey_plans')
    owner = models.ForeignKey(Researcher, related_name='owner_plans')
    testee = models.ForeignKey(Testee, related_name='testee_plans')
    project = models.ForeignKey(Project, related_name='project_plans')
    schedule = models.ForeignKey(Schedule, related_name='schedule_plans')

    is_sent = models.BooleanField(default=False)
    is_done = models.BooleanField(default=False)
    date_created = models.DateTimeField(auto_now=True)
    date_start = models.DateTimeField()
    date_end = models.DateTimeField()
    entries_allowed = models.IntegerField(default=1)
    entries_required = models.IntegerField(default=1)
    
    def __unicode__(self):
        return u'%s to %s @ %s'%(self.owner, self.testee, self.date_created)


class Record(models.Model):
    rid = models.CharField(max_length=30, unique=True)
    testee = models.ForeignKey(Testee, related_name='testee_records')
    plan = models.ForeignKey(Plan, related_name='plan_records')
    
    date_created = models.DateTimeField()
    date_uploaded = models.DateTimeField(auto_now=True)

    def __unicode__(self):
        return u'%s @ %s'%(self.testee, self.date_created)

def content_file_name(instance, filename):
    if instance.answer != None:
        return '/'.join(['', instance.answer.record.plan.survey.project.code + "_" + str(instance.answer.record.plan.survey.project.pk) ,instance.answer.record.plan.survey.code + "_" + str(instance.answer.record.plan.survey.pk), instance.answer.record.testee.username, filename])
    else:
        return '/temp/' + filename

class AnswerEntry(models.Model):
    qentry = models.ForeignKey(QuestionEntry, related_name='question_aentries')
    record = models.ForeignKey(Record, related_name='record_aentries')
    reply = models.CharField(max_length=1000)
    content = models.TextField() # raw content @depreciated

class MediaEntry(models.Model):
    answer = models.ForeignKey(AnswerEntry, related_name="media", blank=True, null=True)
    uid = models.CharField(max_length = 100, null=True)
    bucket_name = models.CharField(max_length=100)
    object_name = models.CharField(max_length=100)
    content = models.FileField(upload_to = content_file_name, storage=BAEStorage(), blank=True, null=True)

