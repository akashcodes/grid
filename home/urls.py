from django.conf.urls import url, include
from . import models
from . import views

urlpatterns = [
	url(r'^$', views.display_all)
]
