from django.conf.urls import url

import views

urlpatterns = [
	url(r'^signin$', views.signin, name='api_signin'),
	url(r'^signout$', views.signout, name='api_signout'),
	url(r'^create_survey$', views.create_survey, name='api_create_survey')
]