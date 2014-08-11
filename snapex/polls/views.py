from django.http import HttpResponse

def index(request):
    return HttpResponse("Hello, world. You're at the polls index.")

def test(request):
	import db_ops
	db_ops.create_admin()
	db_ops.create_researcher()
	db_ops.create_testees()

	return HttpResponse("I'm testing...")