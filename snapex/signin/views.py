from django.http import HttpResponse
from django.shortcuts import render
from django.shortcuts import redirect

def index(req):
    if req.user.is_authenticated():
        return redirect('/myview/project')
    
    if req.method == 'GET':
        return render(req, 'signin/login.html', {})
