from django.http import HttpResponse

def index(request):
    return HttpResponse("Hello, world. You're at the polls index.")

def test(request):
	import db_ops
	# db_ops.create_admin()
	# db_ops.create_researcher()
	# db_ops.create_testees()
	
	# i = db_ops.create_project(owner='19770707', 
	# 				subject='test', 
	# 				researchers=['19770707',
	# 							'67d66e86-210c-11e4-a642-ee80fb9fa428'], 
	# 				testees=['19770707',
	# 						'67b0681c-210c-11e4-a642-ee80fb9fa428',
	# 						'67d1a98c-210c-11e4-a642-ee80fb9fa428'])

	# i = db_ops.create_survey('19770707', 1, content='this is a survey')

	

	return HttpResponse("I'm testing... %s %s"%(i))