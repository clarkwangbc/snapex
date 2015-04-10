from django.http import HttpResponse
import polls.db_ops as db_ops
import qrcode



def syncdb(req):
    from StringIO import StringIO
    content = StringIO()
    
    from django.core.management import call_command
    ret = call_command('syncdb', stdout=content)
    content.seek(0)
    return HttpResponse(content.getvalue())

def logging(*args):
    # logging example: log to debug.txt
    import logging
    log = logging.getLogger(__name__)
    log.debug('a debug message')
    return HttpResponse("complete")

def base(req):
    db_ops.create_admin('admin', 'taoliyuan', '19770707')
    users = ["Sudo Researcher 1", "Sudo Researcher 2", "Sudo Researcher "]
    s = str(db_ops.create_researcher(users))
    testees = db_ops.generate_uids(10)
    
    return HttpResponse(s)

def create_testees(req):
    d, testees = db_ops.create_new_testees(10)
    return HttpResponse(str(testees))

def flush(req):
    from django.core.management import call_command
    ret = call_command('flush')
    return HttpResponse("complete")

def push_all(req):
    '''
        Not considered for a lot of plans
    '''
    from polls.models import Plan
    plans = Plan.objects.filter(is_sent=False).all()
    ret = ''
    for plan in plans:
        st, msg = db_ops.send_plan(plan)
        if st==0:
            ret += 'plan %s success\n'%(plan.id)
        else:
            ret += 'plan %s failed: %s'%(plan.id, msg)

    return HttpResponse(ret)

def create_qr_for_all_testee(req):
    '''
        Manually create QRCode for all testee if doesn't exist
    '''
    from polls.models import Testee
    testees = Testee.objects.all()
    for testee in testees:
        if testee.qr_image == None:
            testee.qr_image = db_ops.create_qrcode(testee.username)
            testee.save()

    return HttpResponse("Succeeded")

def auto_create_plans(req):
    from polls.models import Plan
    from polls.models import Schedule
    import datetime
    plan_example_0 = Plan.objects.filter(pk=106)[0]
    plan_example_1 = Plan.objects.filter(pk=107)[0]
    plan_example_2 = Plan.objects.filter(pk=108)[0]
    for i in range(6):
        plan_example_0.pk = None
        plan_example_0.date_start = plan_example_0.date_start + datatime.timedelta(days=1)
        plan_example_0.date_end = plan_example_0.date_end + datetime.timedelta(days=1)
        plan_example_0.save()
        plan_example_1.pk = None
        plan_example_1.date_start = plan_example_1.date_start + datatime.timedelta(days=1)
        plan_example_1.date_end = plan_example_1.date_end + datetime.timedelta(days=1)
        plan_example_1.save()
        plan_example_2.pk = None
        plan_example_2.date_start = plan_example_2.date_start + datatime.timedelta(days=1)
        plan_example_2.date_end = plan_example_2.date_end + datetime.timedelta(days=1)
        plan_example_2.save()

    schedule_w2 = Schedule.objects.filter(pk=5)
    plan_example_0.pk = None
    plan_example_0.schedule = schedule_w2
    plan_example_0.date_start = plan_example_0.date_start + datatime.timedelta(days=1)
    plan_example_0.date_end = plan_example_0.date_end + datetime.timedelta(days=1)
    plan_example_0.save()
    plan_example_1.pk = None
    plan_example_1.schedule = schedule_w2
    plan_example_1.date_start = plan_example_1.date_start + datatime.timedelta(days=1)
    plan_example_1.date_end = plan_example_1.date_end + datetime.timedelta(days=1)
    plan_example_1.save()
    plan_example_2.pk = None
    plan_example_2.schedule = schedule_w2
    plan_example_2.date_start = plan_example_2.date_start + datatime.timedelta(days=1)
    plan_example_2.date_end = plan_example_2.date_end + datetime.timedelta(days=1)
    plan_example_2.save()

    for i in range(6):
        plan_example_0.pk = None
        plan_example_0.date_start = plan_example_0.date_start + datatime.timedelta(days=1)
        plan_example_0.date_end = plan_example_0.date_end + datetime.timedelta(days=1)
        plan_example_0.save()
        plan_example_1.pk = None
        plan_example_1.date_start = plan_example_1.date_start + datatime.timedelta(days=1)
        plan_example_1.date_end = plan_example_1.date_end + datetime.timedelta(days=1)
        plan_example_1.save()
        plan_example_2.pk = None
        plan_example_2.date_start = plan_example_2.date_start + datatime.timedelta(days=1)
        plan_example_2.date_end = plan_example_2.date_end + datetime.timedelta(days=1)
        plan_example_2.save()

    schedule_w3 = Schedule.objects.filter(pk=6)
    plan_example_0.pk = None
    plan_example_0.schedule = schedule_w2
    plan_example_0.date_start = plan_example_0.date_start + datatime.timedelta(days=1)
    plan_example_0.date_end = plan_example_0.date_end + datetime.timedelta(days=1)
    plan_example_0.save()
    plan_example_1.pk = None
    plan_example_1.schedule = schedule_w2
    plan_example_1.date_start = plan_example_1.date_start + datatime.timedelta(days=1)
    plan_example_1.date_end = plan_example_1.date_end + datetime.timedelta(days=1)
    plan_example_1.save()
    plan_example_2.pk = None
    plan_example_2.schedule = schedule_w2
    plan_example_2.date_start = plan_example_2.date_start + datatime.timedelta(days=1)
    plan_example_2.date_end = plan_example_2.date_end + datetime.timedelta(days=1)
    plan_example_2.save()

    for i in range(6):
        plan_example_0.pk = None
        plan_example_0.date_start = plan_example_0.date_start + datatime.timedelta(days=1)
        plan_example_0.date_end = plan_example_0.date_end + datetime.timedelta(days=1)
        plan_example_0.save()
        plan_example_1.pk = None
        plan_example_1.date_start = plan_example_1.date_start + datatime.timedelta(days=1)
        plan_example_1.date_end = plan_example_1.date_end + datetime.timedelta(days=1)
        plan_example_1.save()
        plan_example_2.pk = None
        plan_example_2.date_start = plan_example_2.date_start + datatime.timedelta(days=1)
        plan_example_2.date_end = plan_example_2.date_end + datetime.timedelta(days=1)
        plan_example_2.save()

    schedule_w4 = Schedule.objects.filter(pk=7)
    plan_example_0.pk = None
    plan_example_0.schedule = schedule_w2
    plan_example_0.date_start = plan_example_0.date_start + datatime.timedelta(days=1)
    plan_example_0.date_end = plan_example_0.date_end + datetime.timedelta(days=1)
    plan_example_0.save()
    plan_example_1.pk = None
    plan_example_1.schedule = schedule_w2
    plan_example_1.date_start = plan_example_1.date_start + datatime.timedelta(days=1)
    plan_example_1.date_end = plan_example_1.date_end + datetime.timedelta(days=1)
    plan_example_1.save()
    plan_example_2.pk = None
    plan_example_2.schedule = schedule_w2
    plan_example_2.date_start = plan_example_2.date_start + datatime.timedelta(days=1)
    plan_example_2.date_end = plan_example_2.date_end + datetime.timedelta(days=1)
    plan_example_2.save()

    for i in range(6):
        plan_example_0.pk = None
        plan_example_0.date_start = plan_example_0.date_start + datatime.timedelta(days=1)
        plan_example_0.date_end = plan_example_0.date_end + datetime.timedelta(days=1)
        plan_example_0.save()
        plan_example_1.pk = None
        plan_example_1.date_start = plan_example_1.date_start + datatime.timedelta(days=1)
        plan_example_1.date_end = plan_example_1.date_end + datetime.timedelta(days=1)
        plan_example_1.save()
        plan_example_2.pk = None
        plan_example_2.date_start = plan_example_2.date_start + datatime.timedelta(days=1)
        plan_example_2.date_end = plan_example_2.date_end + datetime.timedelta(days=1)
        plan_example_2.save()



    