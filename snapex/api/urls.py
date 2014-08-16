from django.conf.urls import include, url
import views


urlpatterns = [
	url(r'^signin', views.signin, name="api_signin"),
]