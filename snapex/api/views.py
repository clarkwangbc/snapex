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
from datetime import datetime
import bc_ops
from polls.qentry_type_map import *
from django.db.models import Q

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
            sid = db_ops.generate_uid()
            survey = Survey(sid=sid, project=project, name=survey_name, raw_content=req.body)
            survey.save()
            # create question entries
            previous_page_type = ""
            previous_page_items_count = 0
            page = None
            page_no = 0
            for rank, s in enumerate(surveys):
                try:
                    options_array = s['field_options']['options']
                    options_plain_array = []
                    for option in options_array:
                        option_label = option["label"]
                        options_plain_array.append(option_label)
                    options = simplejson.dumps(options_plain_array)
                except Exception as e:
                    options = ""
                try:
                    description = s['field_options']['description']
                except Exception as e:
                    description = ""
                qe = QuestionEntry(qtype=s['field_type'], description=description, options=options, required=s['required'], question=s['label'], content=simplejson.dumps(s))
                qe.save()
                sm = SurveyMembership(qentry=qe, survey=survey, entry_order=rank)
                sm.save()

                current_page_type = ptype_for_qtype(s['field_type'])

                if previous_page_type == current_page_type and previous_page_items_count < max_items_for_ptype(current_page_type):
                    pm = PageMembership(qentry=qe, page=page, entry_order=previous_page_items_count * 10)
                    pm.save()
                    previous_page_items_count += 1

                else:
                    page_no += 10
                    page = Page(ptype=current_page_type, page_no=page_no, survey=survey)
                    page.save()
                    pm = PageMembership(qentry=qe, page=page, entry_order=0)
                    pm.save()
                    previous_page_type = current_page_type
                    previous_page_items_count = 1

            return 200, dict(msg='ok')
        except Exception as e:
            return 1001, dict(msg='json format error', verbose=str(e))

@csrf_exempt
@login_required
@utility.expose(rest=True)
def update_survey(req):
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

            # Create Plan for each event

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
                if user.user_profile.device_id == device_id:
                    return 200, dict(msg='welcome back')
                else:
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
        plans = schedule.schedule_plans.filter(Q(testee=testee) | Q(testee=None))
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
def report_record_with_file_attachment(req):
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
            qms = plan.survey.questions()
            #qms = plan.survey.survey_memberships.order_by('entry_order')

            if len(reply_entries) != len(qms):
                return 1003, dict(msg='record not matching survey', replied=len(reply_entries), qms=len(qms))
            for re, qm in zip(reply_entries, qms):
                # check if their types
                if re['field_type'] != qm.qtype:
                    return 1003, dict(msg='record not matching survey', field_type=re['field_type'], field_type_on_server=qm.qentry.qtype)

            record = db_ops.create_record_to_plan(user.testee, plan, json_data['date_created'])
            #Record(testee=user.testee, plan=plan, date_created=json_data['date_created'])
            record.save()

            for re, qm in zip(reply_entries, qms):
                if(re['field_type'] == "PhotoInput"):
                    rawb64str = re['reply']
                    data = base64.b64decode(rawb64str)
                    filename = '/photo_' + user_secret + "/" + "photo_" + str(plan.survey.id) + "_" + plan.survey.code + "_" + str(datetime.now()).replace(" ","T") +".jpg"
                    media = bc_ops.put_photo(filename, data)
                    re['reply'] = "media@uid:" + str(media.pk)
                    ae = AnswerEntry(qentry=qm, record=record, content=simplejson.dumps(re), reply="media@uid:"+str(media.pk))
                    ae.save()
                    
                elif(re['field_type'] == "AudioInput"):
                    rawb64str = re['reply']
                    data = base64.b64decode(rawb64str)
                    filename = '/audio_' + user_secret + "/" + "audio_" + str(plan.survey.id) + "_" + plan.survey.code + "_" + str(datetime.now()).replace(" ","T") +".aac"
                    media = bc_ops.put_audio(filename, data)
                    re['reply'] = "media@uid:" + str(media.pk)
                    ae = AnswerEntry(qentry=qm, record=record, content=simplejson.dumps(re), reply="media@uid:"+str(media.pk))
                    ae.save()
                    
                else:
                    ae = AnswerEntry(qentry=qm, record=record, content=simplejson.dumps(re), reply=re['reply'])
                    ae.save()

            plan.is_done = True

            return 200, dict(msg='ok')

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

            if not (plan.testee == None or plan.testee == user.testee):
                return 1002, dict(msg='permission denied')

            reply_entries = json_data['data']
            qms = plan.survey.questions()
            #qms = plan.survey.survey_memberships.order_by('entry_order')

            if len(reply_entries) != len(qms):
                return 1003, dict(msg='record not matching survey', replied=len(reply_entries), qms=len(qms))
            for re, qm in zip(reply_entries, qms):
                # check if their types
                if re['field_type'] != qm.qtype:
                    return 1003, dict(msg='record not matching survey', field_type=re['field_type'], field_type_on_server=qm.qentry.qtype)

            record = db_ops.create_record_to_plan(user.testee, plan, json_data['date_created'])
            #Record(testee=user.testee, plan=plan, date_created=json_data['date_created'])
            record.save()

            for re, qm in zip(reply_entries, qms):
                if(re['field_type'] == "PhotoInput"):
                    ae = AnswerEntry(qentry=qm, record=record, content="", reply="")
                    ae.save()
                    rawb64str = re['reply']
                    data = base64.b64decode(rawb64str)
                    filename = '/photo_' + user_secret + "/" + "photo_" + str(plan.survey.id) + "_" + plan.survey.code + "_" + str(datetime.now()).replace(" ","T") +".jpg"
                    media = bc_ops.put_photo_for_answer(filename, data, ae)
                    re['reply'] = "media@uid:" + str(media.pk)
                    ae.content = simplejson.dumps(re)
                    ae.reply = "media@uid:" + str(media.pk)
                    ae.save()

                elif(re['field_type'] == "AudioInput"):
                    ae = AnswerEntry(qentry=qm, record=record, content="", reply="")
                    ae.save()
                    rawb64str = re['reply']
                    data = base64.b64decode(rawb64str)
                    filename = '/audio_' + user_secret + "/" + "audio_" + str(plan.survey.id) + "_" + plan.survey.code + "_" + str(datetime.now()).replace(" ","T") +".aac"
                    media = bc_ops.put_audio_for_answer(filename, data, ae)
                    re['reply'] = "media@uid:" + str(media.pk)
                    ae.content = simplejson.dumps(re)
                    ae.reply = "media@uid:" + str(media.pk)
                    ae.save()
                    
                else:
                    ae = AnswerEntry(qentry=qm, record=record, content=simplejson.dumps(re), reply=re['reply'])
                    ae.save()

            plan.is_done = True
            plan.save()

            return 200, dict(msg='ok')

        except Exception as e:
            return 1000, dict(msg='json format error', verbose=str(e))

@csrf_exempt
@utility.expose(rest=True)
def update_userinfo(req):
    if req.method=='POST':
        try:
            json_data = simplejson.loads(req.body)
            secret = json_data['testee']
            testee = db_ops.get_testee_from_secret(secret)
            if testee is None:
                return 1002, dict(msg='secret invalid')
            if not testee.is_active:
                return 1001, dict(msg='secret has not been activated')
            name = json_data['name']

            print json_data
            #if only one part of name is given, name is stored entirely in auth_user's last_name field
            #or split into first_name and last_name
            splitted_name_array = name.split(" ", 2)

            if len(splitted_name_array) == 2:
                testee.first_name = splitted_name_array[0]
                testee.last_name = splitted_name_array[1]
            else:
                testee.last_name = name

            testee.occupation = json_data['occupation']
            testee.age = json_data['age']
            testee.gender = json_data['gender']
            testee.user_profile.telephone = json_data['telephone']
            testee.email = json_data['email']
            other_info_dict = {}
            wechat = json_data.get("wechat")
            facebook = json_data.get("facebook")
            if wechat != None and wechat != "":
                other_info_dict['WECHAT_ID'] = wechat
            if facebook != None and facebook != "":
                other_info_dict['FACEBOOK_ID'] = facebook
            db_ops.update_other_info(testee.user_profile, other_info_dict)
            testee.save()
            return 200, dict(msg='ok')
        except Exception as e:
            return 1000, dict(msg='json format error', verbose=str(e))
    else:
        return 1000, dict(msg='only POST method will be accepted')

@csrf_exempt
@utility.expose(rest=True)
def get_userinfo(req):
    if req.method=='POST':
        try:
            json_data = simplejson.loads(req.body)
            secret = json_data['testee']
            testee = db_ops.get_testee_from_secret(secret)
            if testee is None:
                return 1002, dict(msg='secret invalid')
            if not testee.is_active:
                return 1001, dict(msg='secret has not been activated')
            
            ret = {'testee': secret}
            if (testee.first_name and test.first_name != ""):
                ret['name'] = testee.first_name + " " + testee.last_name
            else:
                ret['name'] = testee.last_name
            ret['occupation'] = testee.occupation
            ret['age'] = testee.age
            ret['gender'] = testee.gender
            ret['telephone'] = testee.user_profile.telephone
            ret['email'] = testee.email
            other_info_dict = db_ops.get_other_info(testee)
            if 'WECHAT_ID' in other_info_dict:
                ret['wechat'] = other_info_dict['WECHAT_ID']
            else:
                ret['wechat'] = None

            if 'FACEBOOK_ID' in other_info_dict:
                ret['facebook'] = other_info_dict['FACEBOOK_ID']
            else:
                ret['facebook'] = None           
            return 200, dict(msg='ok', testee=ret)
        except Exception as e:
            return 1000, dict(msg='json format error', verbose=str(e))
    else:
        return 1000, dict(msg='only POST method will be accepted')




            
             



