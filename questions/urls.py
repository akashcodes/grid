from django.conf.urls import url, include
from . import models
from . import views

urlpatterns = [
	url(r'^(?P<community_name>.+?)/(?P<question_id>.+?)/', views.question_display),
]
