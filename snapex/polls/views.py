from django.http import HttpResponse

def index(request):
    return HttpResponse("Hello, world. You're at the polls index.")

def test(request):
	import db_ops
	
	db_ops.create_admin('admin', 'taoliyuan', '19770707')
	users = db_ops.generate_uids(3)
	s = str(db_ops.create_researcher(users))

	return HttpResponse(s)