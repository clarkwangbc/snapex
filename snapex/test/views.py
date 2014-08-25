from django.http import HttpResponse


def testcreateTable():
    dbname = "beXsKRIOGfKKTwkkcTkh"
    import MySQLdb
    mydb = MySQLdb.connect(
        host   = 'sqld.duapp.com',
        port   = 4050,
        user   = '4vvtke0DV3yR9bIYcGyDvKBC',
        passwd = '1B65i354OUTyyyVxMhI9IlgBxFztCp84',
        db = 'beXsKRIOGfKKTwkkcTkh')

    cursor = mydb.cursor()

    cmd = '''create table employee (
             id int(4) auto_increment,
             name char(20) not null,
             age int(2),
             sex char(8) default 'man',
             primary key (id))'''

    cursor.execute(cmd)

    mydb.close()


def excutecmd():
    import polls.bd_push as bd_push
    s = str(bd_push.test_pushMessage_to_user())
    # from django.core.management import call_command
    # ret = call_command('syncdb')
    # import logging
    # log = logging.getLogger(__name__)
    # log.debug(str(ret))

    # from django.contrib.auth import authenticate
    # u = authenticate(username='snapex', password='dingxiangyuan')
    return HttpResponse(s)


def dbtest(request):
    ret = ''

    from django.contrib.auth.models import User
    u = User(username='test')
    u.save()
    ret = str(u.user_profile) if hasattr(u,'user_profile') else 'None'

    return HttpResponse(ret)


def runcmd(request):
    return excutecmd()