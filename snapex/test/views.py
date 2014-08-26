from django.http import HttpResponse

def syncdb():
    from django.core.management import call_command
    ret = call_command('syncdb')
    return HttpResponse("complete")

def excutecmd():
    # import logging
    # log = logging.getLogger(__name__)
    # log.debug(str(ret))
    return HttpResponse("complete")


def base(request):
    import db_ops
    
    db_ops.create_admin('admin', 'taoliyuan', '19770707')
    users = db_ops.generate_uids(3)
    s = str(db_ops.create_researcher(users))

    return HttpResponse(s)
