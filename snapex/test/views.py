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
    from django.core.management import call_command
    ret = call_command('syncdb')
    # import logging
    # log = logging.getLogger(__name__)
    # log.debug(str(ret))

    # from django.contrib.auth import authenticate
    # u = authenticate(username='snapex', password='dingxiangyuan')
    return HttpResponse('complete')


def dbtest(request):
    # testcreateTable()
    from django.contrib.auth.models import User
    # u = User(username='snapex', is_active=True,
    #             is_staff=True, is_superuser=True, email='snapex@163.com')
    # u.set_password('dingxiangyuan')
    # u.save()

    from polls.models import UserProfile
    u = User.objects.get(username='snapex')
    up = UserProfile(device_id='19770707', is_admin=True, is_researcher=True, user=u)
    up.save()

    return HttpResponse('ok')


def runcmd(request):
    return excutecmd()
    # return HttpResponse('complete')