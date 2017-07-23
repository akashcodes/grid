from django.conf.urls import url, include
from . import models
from . import views

urlpatterns = [
	url(r'search/', views.search_community_questions),
    url(r'submit_comment/', views.submit_comment),
    url(r'submit_answer/', views.submit_answer),
    url(r'action/', views.action_performed),
    url(r'^(?P<community_name>.+?)/ask_question', views.ask_question),
    url(r'^(?P<community_name>.+?)/question/(?P<question_id>.+?)/$', views.question_display),
    url(r'^(?P<community_name>.+?)/$', views.community_main),
    
    
]
