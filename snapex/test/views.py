from django.http import HttpResponse
import polls.db_ops as db_ops


def syncdb(req):
    from django.core.management import call_command
    ret = call_command('syncdb')
    return HttpResponse("complete")


def logging(*args):
    logging example: log to debug.txt
    import logging
    log = logging.getLogger(__name__)
    log.debug('a debug message')
    return HttpResponse("complete")


def base(req):
    db_ops.create_admin('admin', 'taoliyuan', '19770707')
    users = db_ops.generate_uids(3)
    s = str(db_ops.create_researcher(users))
    return HttpResponse(s)


def flush(req):
    from django.core.management import call_command
    ret = call_command('flush')
    return HttpResponse("complete")    


def push_all(req):
    '''
        Not considered for a lot of plans
    '''
    from polls.models import *
    plans = Plan.objects.filter(is_sent=False).all()
    ret = ''
    for plan in plans:
        st, msg = db_ops.send_plan(plan)
        if st==0:
            ret += 'plan %s success\n'%(plan.id)
        else:
            ret += 'plan %s failed: %s'%(plan.id, msg)

    return HttpResponse(ret)
