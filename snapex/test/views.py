from django.http import HttpResponse
import polls.db_ops as db_ops


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
