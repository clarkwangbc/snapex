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

def change_pw():
    pass

def excutecmd():
    # from django.core.management import call_command
    # ret = call_command('syncdb')
    # ret = call_command('createsuperuser', username='root', email='snapex@163.com', interactive=False)
    # ret = call_command('changepassword', username='admin', password='dingxiangyuan', interactive=False)
    # import logging
    # log = logging.getLogger(__name__)
    # log.debug(str(ret))

    from django.contrib.auth import authenticate
    # u = authenticate(username='admin', password='dingxiangyuan')
    from django.contrib.auth.models import User
    u = User.objects.filter(is_superuser=True)[0]
    s1 = u.is_staff
    s2 = u.is_superuser
    s3 = u.is_active
    s = '%s %s %s'%(s1,s2,s3)
    return HttpResponse(s)

def dbtest(request):
    # testcreateTable()
    from django.contrib.auth.models import User
    u = User(username='admin', password='dingxiangyuan', is_active=True,
                is_staff=True, is_superuser=True, email='snapex@163.com')
    u.save()

    return HttpResponse('ok')

def runcmd(request):
    return excutecmd()
    # return HttpResponse('complete')