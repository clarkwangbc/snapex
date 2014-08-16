from django.http import HttpResponse
import polls.utility as utility
from django.contrib.auth.models import User
from polls.models import *
from django.contrib.auth import authenticate


@utility.expose(rest=True)
def signin(req):
	if req.method == 'POST':
		if 'secret' in req.POST:
			user = None
			secret = req.POST['secret']
			if User.objects.filter(username=secret).exists():
				u = User.objects.get(username=secret)
				# authenticate admin
				if u.is_superuser and 'device_id' in req.POST:
					user = authenticate(username=secret, password=req.POST['device_id'])
				else:
					user = authenticate(username=secret, password='9')

			if user is not None and user.is_active:
				# redirect due to `next` field
				return 200, dict(msg='singin success')
			# else:
			# 	return 400, 
	return 400, dict(msg='invalid signin')
