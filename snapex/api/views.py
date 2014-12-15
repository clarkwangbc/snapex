from django.http import HttpResponse
import polls.utility as utility
from django.contrib.auth.models import User
from polls.models import *
from django.contrib.auth import authenticate, login, logout
from django.views.decorators.csrf import csrf_exempt
from django.conf import settings
from django.contrib.auth.decorators import login_required
import polls.db_ops as db_ops
import simplejson
import base64
import tempfile
from datetime import datetime

import pybcs

@csrf_exempt
@utility.expose(rest=True)
def signin(req):
    if req.method == 'POST':
        if 'device_id' in req.POST:
            user = req.POST['device_id']
            secret = req.POST['secret']
            if User.objects.filter(username=user).exists():
                u = User.objects.get(username=user)
                # authenticate admin
                if u.is_superuser:
                    user = authenticate(username=user, password=secret)
                # authenticate researcher
                elif u.is_staff:
                    user = authenticate(username=user, password=secret)
                # authenticate testee
                else:
                    user = authenticate(username=user, password=settings.DEFAULT_PASSWORD)

                if user is not None and user.is_active:
                    login(req, user)
                    return 200, dict(msg='singin success')
                else:
                    return 401, dict(msg='debug')
        else:
            return 400, dict(msg='no secret in req.POST')
    return 400, dict(msg='invalid signin debug')


@csrf_exempt
@utility.expose(rest=True)
def signout(req):
    logout(req)
    return 200, dict(msg='signout success')


@csrf_exempt
@login_required
@utility.expose(rest=True)
def create_survey(req):
    if req.method=='POST':
        try:
            json_data = simplejson.loads(req.body)
            data = json_data['data']
            project_id = int(data['project_id'])
            survey_name = data['survey_name']
            surveys = data['fields']

            # only ownner of the project have permission to create survey
            user = req.user
            if not Project.objects.filter(owner=user, pk=project_id).exists():
                return 400, dict(msg='permission denied')

            project = db_ops.get_project_from_pk(project_id)
            # create survey
            survey = Survey(project=project, name=survey_name, raw_content=req.body)
            survey.save()
            # create question entries
            for rank, s in enumerate(surveys):
                qe = QuestionEntry(qtype=s['field_type'], content=simplejson.dumps(s))
                qe.save()
                sm = SurveyMembership(qentry=qe, survey=survey, entry_order=rank)
                sm.save()

            return 200, dict(msg='ok')
        except Exception as e:
            return 1001, dict(msg='json format error', verbose=str(e))


@csrf_exempt
@login_required
@utility.expose(rest=True)
def create_schedule(req):
    if req.method=='POST':
        try:
            json_data = simplejson.loads(req.body)
            events = json_data['data']
            schedule_name = json_data['schedule_name']
            user = req.user
            schedule = Schedule(name=schedule_name, content=simplejson.dumps(events), owner=user)
            schedule.save()

            return 200, dict(msg='ok')
        except Exception as e:
            return 1001, dict(msg='json format error', verbose=str(e))


@csrf_exempt
@utility.expose(rest=True)
def auth(req):
    '''
        Auth a testee and activate it
        input:
        {
            testee: 'testee_secret',
            device_id: 'unique device id'
        }
        output:
        {status: status, msg: 'msg'}
        200: ok
        1000: json format error
        1001: secret has been used
        1002: secret invalid
        test:
        curl "http://snapex.duapp.com/api/v0/auth" -d @body.txt
    '''
    if req.method=='POST':
        try:
            json_data = simplejson.loads(req.body)
            secret = json_data['testee']
            device_id = json_data['device_id']
            user = db_ops.get_user_from_secret(secret)
            if user is None:
                return 1002, dict(msg='secret invalid')
            if user.is_active:
                return 1001, dict(msg='secret has been used')

            user.is_active = True
            if device_id != '':
                user.user_profile.device_id = device_id
            user.save()
            return 200, dict(msg='ok')
        except Exception as e:
            return 1000, dict(msg='json format error')


@csrf_exempt
@utility.expose(rest=True)
def pull_plans(req):
    '''
        Pull all plans of a testee
        input:
        {
            testee: 'testee_secret'
        }
        output:
        {
            status: status,
            plans: [
                {
                    id: plan_id,
                    project_name: 'name of the project this plan belongs to',                    
                    survey: {
                        survey_name: 'name of the survey'
                        fields: [
                            {
                                label: 'the question',
                                required: true or false // without quote, wheather media is required
                                field_type: 'simple_question or hard_question or date', // three types
                                field_options: { // always exists
                                    description: 'detailed description of the question' // may not exists
                                }
                            }, // different types of question
                            {
                                ... // same
                                field_type: 'single_choice or multi_choice', // two types
                                field_options: {
                                    include_other_option: true or false,
                                    options: [ // order counts!
                                        {
                                            label: 'content of the option'
                                        }, // one option
                                    ]
                                }
                            },
                            {
                                ... // same
                                field_type: 'l5 or l7', // two types
                                field_options: {
                                    options: [ // order counts!
                                        {
                                            label: 'strongly disagree text'
                                        },
                                        {
                                            label: 'strongly agree text'
                                        } // only the first 2 options take effect here
                                    ]
                                }
                            },

                        ]
                    },
                    schedule: [
                        {
                            msg: 'the msg for testee when alerted',
                            start: '2014-08-17T12:00:00' // app shall alert randomly in [start, end]
                            end: '2014-08-17T14:00:00' // time format: datetime isoformat
                        }, // one alert
                    ]
                }, // a plan
            ]
        }
        200: ok, with plans
        else: error, without plans
        test:
        curl "http://snapex.duapp.com/api/v0/pull_plans" -d @body.txt
    '''
    if req.method=='POST':
        try:            
            json_data = simplejson.loads(req.body)
            secret = json_data['testee']
            user = db_ops.get_user_from_secret(secret)
            if user is None:
                return 1002, dict(msg='secret invalid')
            if not user.is_active:
                return 1001, dict(msg='secret has not been activated')

            plans = []
            pls = user.testee_plans
            for pl in pls.all():
                ret = {}
                ret['id']=  pl.id
                ret['project_name'] = pl.project.name
                survey = simplejson.loads(pl.survey.raw_content)['data']
                ret['survey'] = survey
                ret['schedule'] = simplejson.loads(pl.schedule.content)
                pl.is_sent = True
                plans.append(ret)

            return 200, dict(msg='ok', plans=plans)
        except Exception as e:
            return 1000, dict(msg='json format error')


@csrf_exempt
@utility.expose(rest=True)
def pull_project(req):
    if req is None:
        secret = "b45fd4c0-17f9-45e1-8719-8d160c"
        user = db_ops.get_testee_from_secret(secret)
        if user is None:
            return 1002, dict(msg='secret invalid')
        if not user.is_active:
            return 1001, dict(msg='secret has not been activated')
        
        ret = get_dict_with_testee(user)

        return 200, dict(msg='ok', project=ret)
    
    if req.method=='POST':
        try:   
            print req.body
            json_data = simplejson.loads(req.body)
            print json_data
            secret = json_data['testee']
            print secret
            user = db_ops.get_testee_from_secret(secret)
            if user is None:
                return 1002, dict(msg='secret invalid')
            if not user.is_active:
                return 1001, dict(msg='secret has not been activated')
            
            ret = get_dict_with_testee(user)

            return 200, dict(msg='ok', project=ret)
        except Exception as e:
            print e
            return 1000, dict(msg='json format error')
    
    secret = "b45fd4c0-17f9-45e1-8719-8d160c"
    user = db_ops.get_testee_from_secret(secret)
    if user is None:
        return 1002, dict(msg='secret invalid')
    if not user.is_active:
        return 1001, dict(msg='secret has not been activated')
    
    ret = get_dict_with_testee(user)

    return 200, dict(msg='ok', project=ret)

def get_dict_with_testee(testee):
    projects = testee.testees_projects.all()
    
    if len(projects) == 0:
    # The testee belongs to no project
        return None
    aProject = projects[0]
    surveys = aProject.project_surveys.all()
    schedules = aProject.project_schedules.all()
    
    ret = {}
    ret['id'] = aProject.id
    ret['md5'] = aProject.md5
    ret['code'] = aProject.code
    if aProject.date_start:
        ret['date_start'] = aProject.date_start.strftime('%Y-%m-%dT%H:%M:%S')
    else:
        ret['date_start'] = ""
    
    if aProject.date_end:
        ret['date_end'] = aProject.date_end.strftime('%Y-%m-%dT%H:%M:%S')
    else:
        ret['date_end'] = ""
        
    ret['name'] = aProject.name
    ret['organization'] = aProject.organization
    ret['subject'] = aProject.subject
    ret['surveys'] = []
    ret['schedules'] = []
    
    for survey in surveys:
        survey_dict = {}
        survey_dict['id'] = survey.id
        survey_dict['md5'] = survey.md5
        survey_dict['code'] = survey.code
        survey_dict['logo'] = survey.logo
        survey_dict['name'] = survey.name
        survey_dict['raw_contents'] = survey.raw_content
        survey_dict['others'] = survey.others
        pages_list = []
        pages = survey.survey_pages.all()
        
        for page in pages:
            page_dict = {}
            page_dict['type'] = page.ptype
            page_dict['page_no'] = page.page_no
            questions = page.questions.all()
            questions_list = []
            
            for question in questions:
                question_dict = {}
                question_dict['code'] = question.code
                question_dict['description'] = question.description
                question_dict['options'] = question.options
                question_dict['type'] = question.qtype
                question_dict['required'] = question.required
                question_dict['content'] = question.content
                question_dict['orderNumber'] = 0
                question_dict['question'] = question.question
                question_dict['others'] = question.others
                questions_list.append(question_dict)
            
            page_dict['items']=questions_list
            pages_list.append(page_dict)
            
        survey_dict['pages']=pages_list
        ret['surveys'].append(survey_dict)
    
    for schedule in schedules:
        schedule_dict={}
        schedule_dict['id']=schedule.cid
        schedule_dict['md5']=schedule.md5
        schedule_dict['name']=schedule.name
        plans = schedule.schedule_plans.filter(testee=testee)
        plans_list = []
        
        for plan in plans:
            plan_dict = {}
            plan_dict['id']=plan.id
            plan_dict['start']=plan.date_start.strftime('%Y-%m-%dT%H:%M:%S')
            plan_dict['end']=plan.date_end.strftime('%Y-%m-%dT%H:%M:%S')
            plan_dict['entries_required']=plan.entries_required
            plan_dict['entries_allowed']=plan.entries_allowed
            plan_dict['is_done']=plan.is_done
            plan_dict['survey_id']=plan.survey.pk
            if plan.date_created:
                plan_dict['date_created']=plan.date_created.strftime('%Y-%m-%dT%H:%M:%S')
            else:
                plan_dict['date_created']=""
            
            plans_list.append(plan_dict)
            
        schedule_dict["plans"]=plans_list
        ret['schedules'].append(schedule_dict)
    
    return ret

@csrf_exempt
@utility.expose(rest=True)
def report_media(req):
    '''
        Report a media url to server
        input:
        {
            uid: 'unique media id with max length of 100, may use device_id as a prefix',
            content: [
                {
                    type: 'image' or 'audio' or 'video',
                    url: 'url of the media'
                }, // one media
            ]
        }
        output:
        {status: status, msg: 'msg'}
        200: ok
        else: error
        test:
        curl "http://snapex.duapp.com/api/v0/report_media" -d @body.txt
    '''
    if req.method=='POST':
        try:
            json_data = simplejson.loads(req.body)
            uid = json_data['uid']
            if MediaEntry.objects.filter(uid=uid).exists():
                return 1001, dict(msg='uid already used')
            content = json_data['content']
            me = MediaEntry(uid=uid, content=simplejson.dumps(content))
            me.save()
            return 200, dict(msg='ok')
        except Exception as e:
            return 1000, dict(msg='json format error', verbose=str(e))
            

@csrf_exempt
@utility.expose(rest=True)
def report_media_list(req):
    '''
        Report a media url to server
        input:
        [{
            {
                    type: 'image' or 'audio' or 'video',
                    url: 'url of the media'
            }, // one media
        }]
        output:
        {status: status, msg: 'msg'}
        200: ok
        else: error
        test:
        curl "http://snapex.duapp.com/api/v0/report_media" -d @body.txt
    '''
    if req.method=='POST':
        try:
            json_data = simplejson.loads(req.body)
            uid_lists = []
            for aMedia in json_data:
                uid = generate_uid()
                me = MediaEntry(uid=uid, content=simplejson.dumps(content))
                me.save()
                uid_lists.append(uid)
            return 200, dict(msg='ok', media_ids=uid_lists)
        except Exception as e:
            return 1000, dict(msg='json format error', verbose=str(e))

@csrf_exempt
@utility.expose(rest=True)
def report_record(req):
    '''
        Report a survey record
        input:
        {    
            pid: plan_id, 
            testee: 'testee_secret',
            fields: [ // order counts!
                {
                    field_type: 'field_type',
                    reply: 'reply' // a string
                    // simple/hard question: just the reply, e.g. 'text'
                    // single/multi choice: number with spaces, e.g. '2 4 7'
                    // l5/l7: the number choosed, e.g. '3' for l5; '7' for l7
                    // if media included then: 'reply@@media:uid'
                },
            }
        }
        output:
        {status: status, msg: 'msg'}
        200: ok
        else: error
        test:
        curl "http://snapex.duapp.com/api/v0/report" -d @body.txt
    '''
    if req.method=='POST':
        try:
            json_data = simplejson.loads(req.body)
            pid = json_data['pid']
            user_secret = json_data['testee']

            plan = db_ops.get_plan_from_pk(int(pid))
            user = db_ops.get_user_from_secret(user_secret)

            if not plan.testee==user.testee:
                return 1002, dict(msg='permission denied')

            reply_entries = json_data['data']
            qms = plan.survey.questions
            #qms = plan.survey.survey_memberships.order_by('entry_order')

            if len(reply_entries) != len(qms):
                return 1003, dict(msg='record not matching survey', replied=len(reply_entries), qms=len(qms))
            for re, qm in zip(reply_entries, qms):
                # check if their types
                if re['field_type'] != qm.qentry.qtype:
                    return 1003, dict(msg='record not matching survey', field_type=re['field_type'], field_type_on_server=qm.qentry.qtype)

            record = Record(testee=user, plan=plan)
            record.save()

            for re, qm in zip(reply_entries, qms):
                if(re['field_type'] == "photoInput"):
                    rawb64str = re['reply']
                    data = base64.b64decode(rawb64str)
                    tempMediaFile = tempfile.TemporaryFile()
                    temp.write(data)
                    filename = '/photo_' + str(plan.survey.id) + "_" + user_secret + "_" + str(datetime.now()).replace("_","T") +".png"
                    HOST = "http://bcs.duapp.com/"
                    AK = "4vvtke0DV3yR9bIYcGyDvKBC"
                    SK = "1B65i354OUTyyyVxMhI9IlgBxFztCp84"
                    bbcs = pybcs.BCS(HOST, AK, SK, pybcs.HttplibHTTPC)
                    bucketName = "snapex-photo"
                    bucket = bcs.bucket(bucketName)
                    bucketObject = bucket.object(filename)
                    bucketObject.post_file(tempMediaFile)
                    url = HOST + bucketName + fileName
                    re['reply'] = "media@url:" + url
                    ae = AnswerEntry(qentry=qm.qentry, record=record, content=simplejson.dumps(re))
                    
                elif(re['field_type'] == "audioInput"):
                    rawb64str = re['reply']
                    data = base64.b64decode(rawb64str)
                    filename = '/audio_' + str(plan.survey.id) + "_" + user_secret + "_" + str(datetime.now()).replace("_","T") +".acc"
                    HOST = "http://bcs.duapp.com/"
                    AK = "4vvtke0DV3yR9bIYcGyDvKBC"
                    SK = "1B65i354OUTyyyVxMhI9IlgBxFztCp84"
                    bbcs = pybcs.BCS(HOST, AK, SK, pybcs.HttplibHTTPC)
                    bucketName = "snapex-audio"
                    bucket = bcs.bucket(bucketName)
                    bbcs.put_object(bucketName, fileName, data)
                    url = HOST + bucketName + fileName
                    re['reply'] = "media@url:" + url
                    ae = AnswerEntry(qentry=qm.qentry, record=record, content=simplejson.dumps(re))
                    
                else:
                    ae = AnswerEntry(qentry=qm.qentry, record=record, content=simplejson.dumps(re))
                    ae.save()

            plan.is_done = True

            return 200, dict(msg='ok')

        except Exception as e:
            return 1000, dict(msg='json format error', verbose=str(e))