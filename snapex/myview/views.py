from django.http import HttpResponse
from django.shortcuts import render
from django.contrib.auth.decorators import login_required
from django.contrib.auth.models import User
import polls.db_ops as db_ops
from django.shortcuts import redirect
from django.views.decorators.csrf import csrf_exempt
from polls.models import *
from django.db.models import Q
from django.db.models import Min, Max, Count
from datetime import date
from datetime import timedelta


@csrf_exempt
def index(req):
    return render(req, 'myview/index.html', None)

@csrf_exempt
@login_required
def profile(req):
    ret = {'user_name': req.user.username}
    return render(req, 'myview/profile.html', ret)

@csrf_exempt
@login_required
def myprojects(req):
    '''
        /mypage
    '''
    # display an all projects page
    if req.method == 'GET':    
        # for superuser, direct them to an all plan page
        if req.user.is_superuser:
            return redirect('/mypage/project')
        # for researchers, display a project displaying page
        elif req.user.user_profile.is_researcher:
            ret = {'user_name': req.user.username}
            projects = db_ops.get_projects_from_researcher(req.user)
            ret['projects'] = projects
            return render(req, 'myview/project.html', ret)
        else:
            # for testees, direct them to their project page
            return redirect('/myview/project')
    
    # create new project
    elif req.method == 'POST':
        if req.user.user_profile.is_researcher:
            project_name = req.POST.get('project_name', None)
            project_subject = req.POST.get('project_subject', None)
            init_testees = req.POST.get('init_testees', None)
            init_testees = int(init_testees) if init_testees else None
            if project_name and project_subject and (init_testees is not None):
                db_ops.create_project(owner=req.user, 
                                        subject=project_subject,
                                        name=project_name, 
                                        init=init_testees)
        return redirect('/myview/project')

@csrf_exempt
@login_required
def myproject(req, pid=None, action=None):
    '''
        /mypage/project
    '''
    # project page for testees
    if not req.user.user_profile.is_researcher:
        if req.method=='GET':
            user = req.user
            plans = Plan.objects.filter(testee=user).all()
            return render(req, 'mypage/testee.html', {'plans':plans})
        else:
            return HttpResponse('invalid method')

    # project page for superusers
    if req.user.is_superuser:
        if req.method=='GET':
            plans = Plan.objects.all()
            return render(req, 'mypage/testee.html', {'plans':plans})
        else:
            return HttpResponse('invalid method')        

    if pid is None or pid=='':
        return myprojects(req);

    if req.method=='GET':   

        # default: view project
        if action is None or action == 'dash':
            ret = {'user_name': req.user.username}
            project = Project.objects.get(pk=int(pid))
            ret['project'] = project
            ret['testees'] = db_ops.get_testees_from_project(project)
            ret['surveys'] = Survey.objects.filter(project=project)
            ret['records'] = Record.objects.filter(plan__survey__project=project)
            ret['schedules'] = Schedule.objects.filter(project=project)
            today = date.today()
            if today < project.date_start:
                ret['project_progress'] = 0;
            elif today >= project.date_start and today <= project.date_end:
                ret['project_progress'] = int((today - project.date_start).days / (project.date_end - project.date_start).days *100)
            else:
                ret['project_progress'] = 100;

            t = []
            testees = db_ops.get_testees_from_project(project)
            for testee in testees:
                tinfo = {}
                tinfo['name'] = testee.username
                tinfo['last_name'] = testee.last_name
                tinfo['telephone'] = testee.telephone
                tinfo['email'] = testee.email
                tinfo['age'] = testee.age
                tinfo['is_active'] = testee.is_active
                pls = Plan.objects.filter(testee=testee, project=project)
                tinfo['plan_count'] = pls.count()
                #tinfo['record_count'] = Record.objects.filter(plan__in=pls).count()
                tinfo['record_count'] = Record.objects.filter(testee=testee).count()
                if testee.qr_image:
                    tinfo['qr_code'] = testee.qr_image.url
                else:
                    db_ops.create_qrcode_for_testee(testee)
                    tinfo['qr_code'] = testee.qr_image.url
                t.append(tinfo)
            ret['testees'] = t
            ret['surveys'] = Survey.objects.filter(project=project).all()
            today = date.today()
            yesterday = today - timedelta(days=1)
            ret['surveys_summary'] = []
            ret['date'] = today
            for survey in ret['surveys']:
                total_number_today = db_ops.get_records_from_survey_and_date(survey, today).count()
                total_number_yesterday = db_ops.get_records_from_survey_and_date(survey, yesterday).count()
                total = Record.objects.filter(plan__survey=survey).count()
                ret['surveys_summary'].append({
                    "name": survey.name,
                    "total_today": total_number_today,
                    "total_yesterday": total_number_yesterday,
                    "total": total
                    })
            ret['schedules'] = Schedule.objects.filter(project=project).all()
            ret['plans'] = Plan.objects.filter(project=project).all()
            return render(req, 'myview/project_dashboard.html', ret)
        

        elif action == "stats":
            ret = {}
            project = Project.objects.get(pk=int(pid))
            ret['project'] = project
            schedules = Schedule.objects.filter(project=project).all()
            #ret['surveys'] = Survey.objects.filter(project=project).all()
            #ret['testees'] = db_ops.get_testees_from_project(project)
            ret['stats'] = []
            for schedule in schedules:
                #print schedule
                result = Plan.objects.filter(schedule=schedule).all().aggregate(Min('date_start'), Max('date_end'))
                #print result
                date_start__min = result['date_start__min'].date()
                date_end__max = result['date_end__max'].date()
                number_of_days = (date_end__max - date_start__min).days + 1
                #print number_of_days
                date_list = [date_start__min + timedelta(days=x) for x in range(number_of_days)]
                #print date_list
                testee_list = list(db_ops.get_testees_from_project(project))
                testee_id_list = [testee.pk for testee in testee_list]
                testee_name_list = [testee.last_name for testee in testee_list]
                survey_list = Survey.objects.filter(project=project).all()
                survey_id_list = [survey.pk for survey in survey_list]
                number_of_surveys = Survey.objects.filter(project=project).count()
                count_matrix = [[[0 for z in range(number_of_surveys)] for y in range(number_of_days + 1)] for x in range(len(testee_list))]

                stats_raw = Record.objects.filter(plan__schedule=schedule).all().extra({'date': 'date(polls_record.date_created)'
                    }).values('testee', 'testee__last_name', 'date', 'plan__survey').annotate(count=Count('id')).order_by('testee', 'date')
                for row in stats_raw:
                    x = testee_id_list.index(row['testee'])
                    y = date_list.index(row['date'])
                    z = survey_id_list.index(row['plan__survey'])
                    count_matrix[x][y][z] = row['count']
                    count_matrix[x][number_of_days][z] += row['count']


                ret['stats'].append({'schedule': schedule, 'testee_list': testee_list, 'date_list': date_list, 'survey_list': survey_list, 'count_matrix': zip(testee_name_list, count_matrix)})
            return render(req, 'mypage/project_stats.html', ret)
            
        else:
            return HttpResponse('nothing projects')      




    elif req.method=='POST':
        # handle form submitting: new testees or new plan
        action_type = req.POST.get('action_type', None)
        if action_type == 'new_user':
            user_secret = req.POST.get('user_secret', None)
            user_number = req.POST.get('user_number', None)
            if user_secret is not None and user_number is not None:
                p = Project.objects.get(pk=int(pid))
                if user_secret != '':
                    u = db_ops.get_user_from_secret(user_secret)
                    if u and p:
                        db_ops.add_testee_to_project(u, p)
                else:
                    user_number = int(user_number)
                    st, new_testees = db_ops.create_new_testees(user_number)
                    if st == 0:
                        for testee in new_testees:
                            db_ops.add_testee_to_project(testee, p)

        elif action_type == 'new_plan':
            plan_testee = req.POST.get('plan_testee', None)
            plan_survey = req.POST.get('plan_survey', None)
            plan_schedule = req.POST.get('plan_schedule', None)
            if plan_testee is not None and plan_survey is not None and plan_schedule is not None:
                user = req.user
                testee = db_ops.get_user_from_secret(plan_testee)
                survey = db_ops.get_survey_from_pk(int(plan_survey))
                schedule = db_ops.get_schedule_from_pk(int(plan_schedule))
                project = Project.objects.get(pk=int(pid))

                if not project.owner==user:
                    return HttpResponse('permission denied')

                if testee and survey and schedule and project:
                    plan = Plan(survey=survey, owner=user, 
                        testee=testee, project=project, schedule=schedule)
                    plan.save()
                    from django.conf import settings
                    # push the plan intantly if settings.PUSH_ON_TIME is true
                    if settings.PUSH_ON_TIME:
                        db_ops.send_plan(plan)

        return redirect('/mypage/project?pid=%s'%(pid))        


@csrf_exempt
@login_required
def mytestee(req, pid, uid = None):
    ret = {'user_name': req.user.username}
    project = Project.objects.get(pk=int(pid))
    ret['project'] = project
    ret['testees'] = db_ops.get_testees_from_project(project)
    if uid is None:
        ret['testee'] = ret['testees'][0]
        ret['records'] = Record.objects.filter(testee=ret['testee']).all()
    else:
        testee = Testee.objects.filter(pk=int(uid)).all()[0]
        ret['records'] = Record.objects.filter(testee=testee).all()
        ret['testee'] = testee
    return render(req, 'myview/project_testees.html', ret)

def myrecords(req, pid):
    return render(req, 'myview/project_records.html', {})

def myschedules(req, pid):
    return render(req, 'myview/project_schedule.html', {})

def myquestionaires(req, pid):
    return render(req, 'myview/project_questionaire.html', {})

@login_required
def mysurvey(req):
    '''
        /mypage/survey
    '''
    action = req.GET.get('action', None)
    pid = req.GET.get('pid', None)
    sid = req.GET.get('sid', None)

    if action is None:
        return HttpResponse("action can't be blank")

    user = req.user
    
    if req.method == 'GET':
        if pid is None or pid == '':
            return HttpResponse("pid can't be blank")
        project = db_ops.get_project_from_pk(int(pid))
        if project is None:
            return HttpResponse('invalid pid')
        
        if action == 'create': # a survey creating page
            return render(req, 'mypage/survey_create.html', 
                {'project': project, 'create_survey': 1, 'raw_survey': [], 'survey_id': 0})
                    
        elif action == 'view': # a survey displaying page
            if sid is None or sid=='':
                return HttpResponse("sid can't be blank")
            survey = db_ops.get_survey_from_pk(int(sid))
            if survey is None:
                return HttpResponse('invalid sid')
            import simplejson
            if survey.raw_content == None or survey.raw_content == "":
                survey_content = simplejson.dumps(survey.to_raw_content()["fields"])
            else:
                survey_content = simplejson.dumps(simplejson.loads(survey.raw_content)["data"]["fields"])
            from django.utils.safestring import mark_safe
            return render(req, 'mypage/survey_create.html',
                {'project': project, 'create_survey': 0, 
                    'survey_name': survey.name,
                    'survey_id': survey.id,
                    'raw_survey': mark_safe(survey_content)})    

    elif req.method == 'POST':
        return HttpResponse('invalid method')


def myschedule(req):
    '''
        /mypage/schedule
    '''
    action = req.GET.get('action', None)
    pid = req.GET.get('pid', None)
    sid = req.GET.get('sid', None)

    if action is None:
        return HttpResponse("action can't be blank")

    user = req.user

    if req.method == 'GET':
        if action == 'create': # a schedule creating page
            if pid is None or pid=='':
                return HttpResponse("pid can't be blank")
            project = db_ops.get_project_from_pk(int(pid))
            if project is None:
                return HttpResponse('invalid pid')
            import datetime
            return render(req, 'mypage/schedule_create.html', 
                {'project': project, 'create_schedule': 1, 
                    'events': [], 'schedule_start': (datetime.date.today()+datetime.timedelta(days=2)).isoformat()})
                    
        elif action == 'view': # a schedule displaying page
            if sid is None or sid=='':
                return HttpResponse("sid can't be blank")
            schedule = db_ops.get_schedule_from_pk(int(sid))
            if schedule is None:
                return HttpResponse('invalid sid')
            import simplejson
            import dateutil.parser
            schedule_content = simplejson.loads(schedule.content)
            from django.utils.safestring import mark_safe
            return render(req, 'mypage/schedule_create.html',
                {'create_schedule': 0, 
                    'schedule_name': mark_safe(schedule.name),
                    'events': mark_safe(schedule.content),
                    'schedule_start': min([dateutil.parser.parse(x['start']) for x in schedule_content]).date().isoformat()})    

    elif req.method == 'POST':
        # post a schedule creating form?
        return HttpResponse('post test')


@login_required
def myrecord(req):
    '''
        /mypage/record
    '''
    rid = req.GET.get('rid', None)
    if rid is None or rid=='':
        return HttpResponse("rid can't be blank")

    # permission: for everyone logged in
    record = db_ops.get_record_from_pk(int(rid))
    if not record:
        return HttpResponse('invalid rid')

    template_simpletext_question = '<div>question: %s</div><div>description: %s</div><div>answer: %s</div>'
    template_textfield_question = '<div>question: %s</div><div>description: %s</div><div>answer: %s</div>'
    template_single_choice = '<div>question: %s</div><div>description: %s</div><div>options: %s</div><div>answer: %s</div>'
    template_multi_choice = '<div>question: %s</div><div>description: %s</div><div>options: %s</div><div>answer: %s</div>'
    template_l5 = '<div>question: %s</div><div>description: %s</div><div>1 option: %s</div><div>5 option: %s</div><div>answer: %s</div>'
    template_l7 = '<div>question: %s</div><div>description: %s</div><div>1 option: %s</div><div>7 option: %s</div><div>answer: %s</div>'
    template_date = '<div>question: %s</div><div>description: %s</div><div>answer: %s</div>'
    template_photo = '<div>question: %s</div><div>description: %s</div><div><img src="%s" style="width:480px;"></div>'
    template_audio = '<div>question: %s</div><div>description: %s</div><div><audio controls style="width:480px;"><source src="%s" type="audio/aac" /><p>Your browser does not support HTML5 audio.</p></audio></div>'

    i_html = ''

    for ae in record.record_aentries.all():
        entry_type = ae.qentry.qtype
        print entry_type
        import simplejson
        data = simplejson.loads(ae.qentry.content)
        question = ae.qentry.question
        description = ae.qentry.description
        required = ae.qentry.required
        reply = ae.reply
        
        if entry_type=='SimpleText':
            i_html += template_simpletext_question%(question, description, reply) + '<br>'
        elif entry_type=='TextField':
            i_html += template_textfield_question%(question, description, reply) + '<br>'
        elif entry_type=='PhotoInput':
            i_html += template_photo%(question, description, ae.media.all()[0].content.url) + '<br>'
        elif entry_type=='AudioInput':
            i_html += template_audio%(question, description, ae.media.all()[0].content.url) + '<br>'
        else:
            i_html += template_simpletext_question%(question, description, reply) + '<br>'

    from django.utils.safestring import mark_safe
    return render(req, 'mypage/record.html', {'record': mark_safe(i_html)})
    