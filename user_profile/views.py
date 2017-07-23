# -*- coding: utf-8 -*-
from __future__ import unicode_literals
import pprint
import json
import time
import datetime
import requests
from collections import Counter
from bson.objectid import ObjectId
from bson.json_util import dumps
from django.http import HttpResponse, HttpResponseRedirect
from django.shortcuts import redirect, render
from django.views.decorators.csrf import csrf_exempt
from grid.settings import app_id, app_secret
from Modules.tags.interest import get_interest, search_communities
from pymongo import MongoClient

client = MongoClient()
db = client.grid_database
# Create your views here.
@csrf_exempt
def profile_main(request,user_id):
    print(user_id)
    fetch_user = db.users
    
    user  = fetch_user.find_one({"_id":ObjectId(user_id)})
    question_tags = list()
    answered_tags =list()
    for question in user['questions_asked']:
        tag = question['question_tags'].split()
        question_tags.extend(tag)
    
    
    for question in user['answered_questions']:
        tag = question['question_tags']
        answered_tags.append(tag)
    
    all_tags = Counter(question_tags + answered_tags)
    most_used_tags = all_tags.most_common()
    print(most_used_tags)
        


    context={"user":user}
    
    return render(request, "user_profile/index.html", context)

@csrf_exempt
def bounty_question(request):
    if request.method =="POST":
        timestamp = int(time.time())
        param_text = request.body.decode('utf-8')
        params = json.loads(str(param_text))
        community_name = params["question_community"]
        question_id = params["question_id"]
        question_title = params ["question_title"]
        bounty_rep = params["bounty_rep"]
        email = request.session['email']
        fetch_user = db.users
        user  = fetch_user.find_one({"email":email})
        
        dec_rep = int("-"+bounty_rep)
        fetch_communities = db.communities
        community = fetch_communities.find_one({"name":community_name})
        print(community["id"])
        if int(user['rep']) < int(bounty_rep):
            return HttpResponse("no")
        
        else:
            context = {"question_id":question_id,"question_community":community_name,"title":question_title,"creation_date":timestamp}
            fetch_user.update_one({"_id": ObjectId(user["_id"])},{"$push":{"bounty_question":context}},upsert=True)
            fetch_communities.update_one({"_id": ObjectId(community)},{"$push":{"bounty_question":context}},upsert=True)
            fetch_user.update_one({'_id': ObjectId(user["_id"])}, {'$inc': {"rep":dec_rep}})