from django.conf.urls import url

import views

urlpatterns = [
	url(r'^$', views.mypage, name='mypage'),
	url(r'^user$', views.q_user, name='mypage_user'),
	url(r'^project$', views.myproject, name='mypage_project'),
	url(r'^survey$', views.mysurvey, name="mypage_survey"),
	url(r'^schedule$', views.myschedule, name="mypage_schedule")
]