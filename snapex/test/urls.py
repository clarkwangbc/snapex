from django.conf.urls import url

import views

urlpatterns = [
    url(r'^dbtest$', views.dbtest, name='dbtest'),
    url(r'^runcmd$', views.runcmd, name='runcmd')
]