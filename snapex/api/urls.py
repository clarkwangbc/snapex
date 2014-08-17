from django.conf.urls import url

import views

urlpatterns = [
	url(r'^signin$', views.signin, name='api_signin'),
	url(r'^signout$', views.signout, name='api_signout')
]