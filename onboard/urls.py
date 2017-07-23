from django.conf.urls import url, include
from . import models
from . import views

urlpatterns = [
	url(r'^$', views.facebook_login_request),
	url(r'^facebook_login_response/$', views.facebook_login_response),
	url(r'^welcome/$', views.welcome),
	url(r'^welcome/communities/$', views.communities),
	url(r'^get-communities/$', views.get_communities),
	url(r'^get-tags/$', views.get_more_tags),
	url(r'^create-user/$', views.create_user),
]
