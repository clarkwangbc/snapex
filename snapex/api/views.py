from django.http import HttpResponse
import polls.utility as utility
from django.contrib.auth.models import User
from polls.models import *


@utility.expose(rest=True)
def signin(req):
	return 200, dict(secret=req.POST['secret'])