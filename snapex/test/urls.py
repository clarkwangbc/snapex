from django.conf.urls import url

import views

urlpatterns = [
    url(r'^base$', views.base, name='test_base'),
    url(r'^syncdb$', views.syncdb, name='test_syncdb'),
    url(r'^flush$', views.flush, name='test_flush'),
    url(r'^push_all$', views.push_all, name='test_push_all_plan'),
    url(r'^create_testees$', views.create_testees, name='test_create_testees'),
    url(r'^create_qrcodes$', views.create_qr_for_all_testee, name='generate_qrcodes'),
    url(r'^create_plans$', views.auto_create_plans, name='create_plans')
]

