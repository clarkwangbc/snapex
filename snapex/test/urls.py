from django.conf.urls import url

import views

urlpatterns = [
    url(r'^dbtest$', views.index, name='index')
]