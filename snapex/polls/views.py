from django.http import HttpResponse

def index(request):
    return HttpResponse("Hello, world. You're at the polls index.")

def test(request):
	import db_ops
	# db_ops.create_admin()
	# db_ops.create_researcher()
	# db_ops.create_testees()
	i = db_ops.create_project(owner='19770707', 
					subject='test', 
					researchers=['19770707'], 
					testees=['19770707'])

	return HttpResponse("I'm testing... %s %s"%(i))