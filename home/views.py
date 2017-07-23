# -*- coding: utf-8 -*-
from __future__ import unicode_literals
import pprint
import json
import time

import requests

from bson.json_util import dumps
from django.http import HttpResponse, HttpResponseRedirect
from django.shortcuts import redirect, render
from django.views.decorators.csrf import csrf_exempt
from grid.settings import app_id, app_secret
from Modules.tags.interest import get_interest, search_communities
from Modules.meta.time_filter import get_ago
from pymongo import MongoClient

client = MongoClient()
db = client.grid_database

# Create your views here.
def display_all(request):
    try:
        email = request.session['email']
        get_user = db.users
        user = get_user.find_one({"email":email})
    except:
        return HttpResponseRedirect("/login/")
    
    if user:
        name = user["name"] 
        questions = list()
        questions_ids = list()
        user_communities = []
        
        for community in user["communities"]:
            fetch_questions = db[community]
            
            cursor  = fetch_questions.find()
            cursor = cursor[:5]
            count = fetch_questions.count()
            for i in cursor:
                question = {
                    "question_title": i['title'],
                    "question_id": i['_id'],
                    "question_community":community,
                    "question_tags": i['tags'],
                    "answer_count": i['answer_count'],
                    "time": get_ago(i["creation_date"]),
                    "question_owner": i["owner"]
                    
                }
                questions.append(question)
            
            user_communities.append({
                "name": community.replace("_", " "),
                "community": community,
                "q_count": count
            })
                
                
        context={"communities":user_communities,"questions":questions, "top_communities": user_communities[:4], "name": name, "hot": True}
        
        return render(request, "home/index.html", context)
    
    return HttpResponse("User doesn't exists")
