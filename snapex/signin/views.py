from django.http import HttpResponse
from django.shortcuts import render

def index(request):
	if request.method == 'GET':
		return render(request, 'signin/index.html', {})
	elif request.method == 'POST':
		return HttpResponse('response for POST request')
