from django.http import HttpResponse
import polls.utility as utility
from django.contrib.auth.models import User
from polls.models import *


@utility.expose(rest=True)
def signin(req):
	if req.method == 'POST':
		return 200, dict(method='post')
	elif req.method == 'GET':
		return 200, dict(method='get')