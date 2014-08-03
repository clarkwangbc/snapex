from django.http import HttpResponse

from bae.core import const

def testcreateTable():
   dbname = "beXsKRIOGfKKTwkkcTkh"
   mydb = MySQLdb.connect(
      host   = const.MYSQL_HOST,
      port   = int(const.MYSQL_PORT),
      user   = const.MYSQL_USER,
      passwd = const.MYSQL_PASS,
      db = dbname)
 
   cursor = mydb.cursor()
 
   cmd = '''create table employee (
         id int(4) auto_increment,
         name char(20) not null,
         age int(2),
         sex char(8) default 'man',
         primary key (id))'''
 
   cursor.execute(cmd)
 
   mydb.close()

def index(request):
    testcreateTable()
    return HttpResponse('complete')