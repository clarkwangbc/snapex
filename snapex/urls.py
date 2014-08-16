from django.conf.urls import include, url
from django.contrib import admin

import views

admin.autodiscover()

urlpatterns = [
	url(r'^$', views.index, name='index'),
	url(r'^polls/', include('polls.urls')),
    url(r'^admin/', include(admin.site.urls)),
    url(r'^test/', include('test.urls')),
    url(r'^signin/', include('signin.urls')),
    url(r'^api/v0/', include('api.urls')),
    url(r'^mypage/', include('mypage.urls'))
]