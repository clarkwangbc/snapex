from django.conf.urls import url

import views

urlpatterns = [
    url(r'^base$', views.base, name='test_base'),
    url(r'^syncdb$', views.syncdb, name='test_syncdb')
]