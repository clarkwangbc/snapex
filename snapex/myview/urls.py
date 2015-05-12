from django.conf.urls import url

import views

urlpatterns = [
    url(r'^$', views.index, name='index'),
    url(r'^profile$', views.profile, name='myview_profile'),
    url(r'^project$', views.myprojects, name='myview_projects'),
    #url(r'^profile$', views.myprofile, name='myview_profile'),
    url(r'^project/(\d+)$', views.myproject, name='myview_project'),
    url(r'^project/(\d+)/([a-z]{3,4})$', views.myproject, name='myview_project'),
    url(r'^project/(\d+)/testees$', views.mytestee, name='myview_project_testees'),
    url(r'^project/(\d+)/testee/(\d+)$', views.mytestee, name='myview_project_testee'),
    url(r'^project/(\d+)/records$', views.myrecords, name='myview_project_records'),
   	url(r'^project/(\d+)/questionaires$', views.myquestionaire, name='myview_project_questionaires'),
   	url(r'^project/(\d+)/schedules$', views.myschedule, name='myview_project_schedules'),
    #url(r'^project_testess/(\d+)/w{30}$', views.mytestees, name='myview_project_testees'),
    url(r'^survey/(\d+)', views.mysurvey, name="myview_survey"),
    url(r'^schedule$', views.myschedule, name="myview_schedule"),
    url(r'^record$', views.myrecord, name="myview_record")
]