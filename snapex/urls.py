from django.conf.urls import include, url
from django.contrib import admin
from django.views.generic import RedirectView
import snapex.settings

import views
import xadmin

xadmin.autodiscover()

urlpatterns = [
    #url(r'^$', RedirectView.as_view(url='mypage/')),
    url(r'^$', include('myview.urls')),
    url(r'^polls/', include('polls.urls')),
    url(r'^admin/', include(xadmin.site.urls)),
    url(r'^test/', include('test.urls')),
    url(r'^login/', include('signin.urls')),
    url(r'^signin/', include('signin.urls')),
    url(r'^api/v0/', include('api.urls')),
    url(r'^myview/', include('myview.urls')),
    url(r'^mypage/', include('mypage.urls')),
]