# -*- coding: utf-8 -*-
from __future__ import unicode_literals
import pprint
import json
import time
import datetime
import requests

from bson.objectid import ObjectId
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
@csrf_exempt
def community_main(request,community_name):

    if "name" and "email" and "picture" in request.session:
    
        fetch_questions = db[community_name]
        questions =list()
        cursor  = fetch_questions.find()
        
        for i in cursor:
            question = {
                "question_title": i['title'],
                "question_id": str(i['_id']),
                "question_community": community_name,
                "question_tags": i['tags'],
                "answer_count": i['answer_count'],
                "time": get_ago(i["creation_date"]),
                "question_owner": i["owner"]
            }

            questions.append(question)
                
        context={"questions": questions,"community_name": community_name}
    
        return render(request, "community/index.html", context)
    
    return HttpResponse("Please login.")


@csrf_exempt
def search_community_questions(request): 
    if request.method =="POST":
        
        param_text = request.body.decode('utf-8')
        params = json.loads(str(param_text))
        community_name = params["community_name"]
        fetch_questions = db[community_name]
        questions =list()
        tags =list()
        if "question_text" in params and params["question_text"] != "" :
            search_text = params["question_text"]
            cursor  = fetch_questions.find({"title":{"$regex":search_text,"$options": "-i"}})
            for doc in cursor:
            
                questions.append(doc)
                print(doc)
            
        
            return HttpResponse(dumps(questions))
      
        elif "tag_text" in params and params["tag_text"] != "":
            search_text = params["tag_text"]
            cursor  = fetch_questions.find({"tags":{"$regex":search_text,"$options": "-i"}})
            print("tags",search_text)
            for doc in cursor:
                if doc['tags'] not in tags:            
                    for tag in doc['tags']:
                        tags.append(tag)
            print(tags)
            tags = list(set(tags))
            return HttpResponse(dumps(tags))
        else:
            return HttpResponse("not found")


@csrf_exempt
def ask_question(request, community_name):

    # Get user from session
    try:
        email = request.session['email']
        get_user = db.users
        user = get_user.find_one({"email":email})
    except:
        return HttpResponseRedirect("/community/"+community_name)

    if user:
        
        # Question Submission
        if request.method == "POST":
            title = request.POST['q_title']
            desc = request.POST['q_desc']
            tags = request.POST['q_tags']
            
            print(title, desc, tags)
            
            comm = db[community_name]


            timestamp = int(time.time())

            question = {
                "title": title,
                "description": desc,
                "tags_string": tags,
                "tags": tags.split(' '),
                "creation_date": timestamp,
                "last_edit_date": timestamp,
                "last_activity_date": timestamp,
                "is_answered": False,
                "view_count": 1,
                "answer_count": 0,
                "score": 0,
                "owner": {
                    "_id": str(user["_id"]),
                    "display_name": user["name"],
                    "email": user["email"],
                    "picture": user["picture"]["data"]["url"]
                }
            }

            q_cursor = comm.insert(question)
            context = {"question_id":q_cursor,"question_tags":tags,"question_community":community_name,"title":title,"creation_date":timestamp}
            get_user.update_one({"_id": ObjectId(user["_id"])},{"$push":{"questions_asked":context}})
            get_user.update_one({'_id': ObjectId(user["_id"])}, {'$inc': {"rep": 50}})
        
            if q_cursor:
                return HttpResponseRedirect("/community/"+community_name+"/question/"+str(q_cursor))
            else:
                return HttpResponse("Error Posting Question")
        
        # Show him page
        if community_name not in user['communities']:
            print("Make him a member")
        else:
            
            context = {
                "community": community_name,
                "community_name": community_name.replace('_', ' '),
                "user":user,
                "editor": True,
                "preview": True
            }
            return render(request, "ask_question/ask_question.html", context)
        
        return HttpResponse("not a member of the community")
    else:
        return HttpResponseRedirect("/community/"+community_name)


@csrf_exempt
def question_display(request,community_name,question_id):
    access_token =  request.session["access_token"]
    fetch_question = db[community_name]
    question = fetch_question.find_one({"_id": ObjectId(question_id)})
    context= {
        "question": question,
        "editor": True,
        "preview": True,
        "community": community_name,
        "community_name": community_name.replace('_', ' '),
        "question_id": question_id
    }
    return render(request, "community/question.html",context)


@csrf_exempt
def submit_comment(request):
    if request.method == "POST":
        param_text = request.body.decode('utf-8')
        params = json.loads(str(param_text))
        timestamp = int(time.time())
        comment = params["comment_text"]
        community = params["community"]
        question_id = params["question_id"]
        posts = db[community]

        data = {
            "text": comment,
            "owner": {
                "_id": request.session["id"],
                "name": request.session["name"],
                "picture": request.session["picture"],
                "email": request.session["email"],
                "date": datetime.date.today().strftime("%d-%m-%Y"),
                "time": time.time()
            }
        }

        question = posts.find_one({"_id": ObjectId(question_id)})

        if params["type"] =="comment":
            if params["is_answer"] == "no":
                context = {"text":comment, "replies": [],"owner_id": ObjectId(request.session["id"])}
                posts.update_one({"_id": ObjectId(question_id)},{"$push":{"comment":data}})
            else:
                answer_index = params["answer_index"]
                print(answer_index)
                posts.update_one({"_id": ObjectId(question_id)},{"$push":{"answers."+answer_index+".comment":data}})
        
        elif params["type"] == "reply":
            comment_index = params["comment_index"]
            posts.update_one({"_id": ObjectId(question_id)},{"$push":{"comment."+comment_index+".replies":data}})
        

        
        get_user = db.users
        email = request.session['email']
        user = get_user.find_one({"email":email})
        question_title = params["question_title"]
        context = {"comment":comment,"question_id":question_id,"question_community":community,"title":question_title,"creation_date":timestamp}
        get_user.update_one({"_id": ObjectId(user["_id"])},{"$push":{"commented_question":context}})
        get_user.update_one({'_id': ObjectId(user["_id"])}, {'$inc': {"rep": 10}})
        print(params)


@csrf_exempt
def submit_answer(request):

     if request.method == "POST":
        param_text = request.body.decode('utf-8')
        timestamp = int(time.time())
        params = json.loads(str(param_text))
        answer_title = params["answer_title"]
        a_desc = params["answer_desc"]
        community = params["community"]
        question_tags = params["question_tags"]
        question_id = params["question_id"]
        posts = db[community]
        data = {
            "answer_title":answer_title,
            "answer_desc":a_desc,
            "owner": {
                "_id": request.session["id"],
                "name": request.session["name"],
                "picture": request.session["picture"],
                "email": request.session["email"],
                "date": datetime.date.today().strftime("%d-%m-%Y"),
                "time": time.time()
            }
        }
        context = data
        posts.update_one({"_id": ObjectId(question_id)},{"$push":{"answers":context}})
        
        get_user = db.users
        email = request.session['email']
        user = get_user.find_one({"email":email})
        question_title = params["question_title"]
        context = {"question_id":question_id,"question_tags":question_tags,"answer_title":answer_title,"question_community":community,"question_title":question_title,"creation_date":timestamp}
        get_user.update_one({"_id": ObjectId(user["_id"])},{"$push":{"answered_questions":context}},upsert=True)
        get_user.update_one({'_id': ObjectId(user["_id"])}, {'$inc': {"rep": 70}})


@csrf_exempt
def action_performed(request):
    if request.method == "POST":
        param_text = request.body.decode('utf-8')
        params = json.loads(str(param_text))
        timestamp = int(time.time())
        action = params["action"]
        community = params["community"]
        posts = db[community]
        question_id = params["question_id"]
        get_user = db.users
        email = request.session['email']
        user = get_user.find_one({"email":email})
        question_title = params["question_title"]
        if action == "interested":
            context = {"owner_id":"5973c55fa15e7fa710a48590"}
            posts.update_one({"_id": ObjectId(question_id)},{"$push":{"interested":context}},upsert=True) 
            
            context = {"question_id":question_id,"question_community":community,"title":question_title,"creation_date":timestamp}
            get_user.update_one({"_id": ObjectId(user["_id"])},{"$push":{"fav_question":context}},upsert=True)
            get_user.update_one({'_id': ObjectId(user["_id"])}, {'$inc': {"rep": 30}})
          
        elif action == "upvote":
            context = {"owner_id":"5973c55fa15e7fa710a48590","last_modified": datetime.datetime.now()}
            posts.update_one({"_id": ObjectId(question_id)},{"$push":{"upvote":context}},upsert=True)   
            posts.update_one({'_id': ObjectId(question_id)}, {'$inc': {"upvote_count": 1}})

            context = {"question_id":question_id,"question_community":community,"title":question_title,"creation_date":timestamp}
            get_user.update_one({"_id": ObjectId(user["_id"])},{"$push":{"upvoted_question":context}},upsert=True)
            get_user.update_one({'_id': ObjectId(user["_id"])}, {'$inc': {"rep": 20}})

        elif action == "downvote":
            context = {"owner_id":"5973c55fa15e7fa710a48590","last_modified": datetime.datetime.now()}
            posts.update_one({"_id": ObjectId(question_id)},{"$push":{"downvote":context}},upsert=True)   
            posts.update_one({'_id': ObjectId(question_id)}, {'$inc': {"downvote_count": 1}})
            
            context = {"question_id":question_id,"question_community":community,"title":question_title,"creation_date":timestamp}
            get_user.update_one({"_id": ObjectId(user["_id"])},{"$push":{"downvoted_question":context}},upsert=True)
            get_user.update_one({'_id': ObjectId(user["_id"])}, {'$inc': {"rep": 20}})

        else:
            context = {"owner_id":"5973c55fa15e7fa710a48590","answer_index":action,"last_modified": datetime.datetime.now()}
            posts.update_one({"_id": ObjectId(question_id)},{"$push":{"correct_answer":context}},upsert=True)   
            posts.update_one({'_id': ObjectId(question_id)}, {'$set': {"is_answered": True}})
            
            context = {"question_id":question_id,"question_community":community,"title":question_title,"creation_date":timestamp}
            get_user.update_one({"_id": ObjectId(user["_id"])},{"$push":{"correct_answer":context}},upsert=True)
            get_user.update_one({'_id': ObjectId(user["_id"])}, {'$inc': {"rep": 100}})