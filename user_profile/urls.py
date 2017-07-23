from django.conf.urls import url, include
from . import models
from . import views

urlpatterns = [
	url(r'^bounty/$', views.bounty_question),
    url(r'^(?P<user_id>.+?)/$', views.profile_main),
    
    
]
