from django.http import HttpResponse


@login_required
def index(req):
    return HttpResponse("It works!")