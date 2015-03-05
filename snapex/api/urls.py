from django.conf.urls import url

import views

urlpatterns = [
    url(r'^signin$', views.signin, name='api_signin'),
    url(r'^signout$', views.signout, name='api_signout'),
    url(r'^create_survey$', views.create_survey, name='api_create_survey'),
    url(r'^create_schedule$', views.create_schedule, name='api_create_schedule'),
    url(r'^report$', views.report_record, name='api_report_survey'),
    #url(r'^report_media$', views.report_media_list, name='api_report_media'),
    #url(r'^pull_plans$', views.pull_plans, name='api_pull_plans'),
    url(r'^auth$', views.auth, name='api_auth'),
    url(r'^pull_project$', views.pull_project, name='api_pull_project'),
    url(r'^update_userinfo',views.update_userinfo, name='update_userinfo')
]