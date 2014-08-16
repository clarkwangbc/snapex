from django.http import HttpResponse
from django.shortcuts import render


def mypage(req):
	return render(request, 'mypage/index.html', {})
