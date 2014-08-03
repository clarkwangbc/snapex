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
    # ret = call_command('syncdb')
    ret = call_command('changepassword', username='admin', password='dingxiangyuan', interactive=False)
    import logging
    log = logging.getLogger(__name__)
    log.debug(str(ret))

def dbtest(request):
    testcreateTable()
    return HttpResponse('complete')

def runcmd(request):
    excutecmd()
    
    return HttpResponse('complete')