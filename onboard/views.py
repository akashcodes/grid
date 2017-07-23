import time
import json

import requests
from bson.json_util import dumps
from django.http import HttpResponse, HttpResponseRedirect
from django.shortcuts import render,redirect
from django.views.decorators.csrf import csrf_exempt
from grid.settings import app_id, app_secret
from Modules.tags.interest_tags import get_tags, search_tags
from Modules.tags.interest import get_interest, search_communities
from pymongo import MongoClient

client = MongoClient()
db = client.grid_database


def facebook_login_request(request):
    """Send Login request to graph api."""

    Login_request_time = time.time()

    permissions = "public_profile, email, user_friends, user_likes,user_birthday, user_posts,\
         user_photos,user_work_history,user_education_history, user_hometown, user_location"

    redirect_uri = "http://localhost:8000/login/facebook_login_response"
    login_dialouge_url = "https://www.facebook.com/v2.9/dialog/oauth?client_id=" + app_id + \
        "&redirect_uri=" + redirect_uri + \
        "&auth_type=rerequest&scope=%s" % (permissions)
    print("--- %s seconds (Login request) ---" %
          (time.time() - Login_request_time))
    return HttpResponseRedirect(login_dialouge_url)


def facebook_login_response(request):
    """Take Code from facebook_response and send it back to get Access Token.
        Send Access Token to get Likes
        from likes(about) figure out user's interest(Modules.tags.get_interest) """
    start_time = time.time()
    access_token_time = time.time()
    code = request.GET.get('code', "Access")
    access_token_response = requests.get("https://graph.facebook.com/v2.9/oauth/access_token?client_id=" + app_id +
                                         "&redirect_uri=http://localhost:8000/login/facebook_login_response&\
                     client_secret=" + app_secret + "&code=%s" % code)
    access_token = access_token_response.json().get('access_token')

    #Hadling Declined Permissions
    if access_token != None:
        permissions = requests.get("https://graph.facebook.com/v2.6/me/permissions?access_token="+access_token).json().get("data", None)
        if permissions != None:
            permission_declined = False
            declined_permissions = list()
            for i in permissions:
                if i["status"] == "declined":
                    permission_declined = True
                    declined_permissions.append(i["permission"])
            if permission_declined:
                declined_permissions_string = ""
                for i in declined_permissions:
                    declined_permissions_string = declined_permissions_string + i + " ,"
                declined_permissions_string = declined_permissions_string[:-1]
                declined_permissions_url = "https://www.facebook.com/dialog/oauth?client_id="+app_id+"&redirect_uri=http://localhost:8000/login/facebook_login_response&auth_type=rerequest&scope="+declined_permissions_string
                return HttpResponse("You've denied some permission(s). => "+declined_permissions_string+"<br/><br/>Click <a href='"+declined_permissions_url+"'>Here</a> to allow denied permissions.")
        else:
            return HttpResponse("Error in getting permissions.")
    else:
        return HttpResponse("Error in creating user login. Please try again.")

    print("--- %s seconds (Get access_token) ---" %
          (time.time() - access_token_time))

    likes_response_time = time.time()
    likes_response = requests.get("https://graph.facebook.com/v2.9/me?fields=name,email,picture,likes.limit(100)\
    {category,name,about}&access_token=%s" % (access_token))
    name = likes_response.json().get('name')
    email = likes_response.json().get('email')
    likes = likes_response.json().get('likes')['data']
    picture = likes_response.json().get("picture")
    
    posts = db.users
    user = posts.update_one(
        {"email": email},{"$setOnInsert":{"name":name,
        "email":email,
        "picture": picture,
        "facebook_likes": likes,
        "access_token":access_token}},upsert=True)
    
    print("--- %s seconds (Get likes) ---" %
          (time.time() - likes_response_time))
    
    user = posts.find_one({"email": email})
    
    # Create session if user created in database
    if user:
        request.session["id"] = str(user["_id"])
        request.session["name"] = name
        request.session["email"] = email
        request.session["picture"] = picture
        request.session["access_token"] = access_token
        print("============================>", user)
    
    return HttpResponseRedirect("/login/welcome")


def welcome(request):

    if "name" and "email" and "access_token" and "picture" in request.session:
        name = request.session["name"]
        email = request.session["email"]
        picture = request.session["picture"]
        access_token = request.session["access_token"]

        user_data = db.users.find_one({"email": email})

        if user_data:

            likes = user_data["facebook_likes"]

            suggested_communities_time = time.time()
            suggested_communities = get_tags(likes)
            print("--- %s seconds (Get interest from likes) ---" %
                (time.time() - suggested_communities_time))
            suggested_communities = dict(suggested_communities)
            print(name,email,suggested_communities)
            posts = db.communities
            get_all_communities = posts.find()
            all_communities =list()
            for doc in get_all_communities:
                all_communities.append(doc['name'])
            context = {
                "suggested_tags":suggested_communities,
                "name":name,
                "picture": picture,
                "all_communities":all_communities,
                
            }
            
            return render(request, "onboard/index.html", context)
        
        return HttpResponse("User doesn't exists in Database.")
    
    return HttpResponseRedirect("/")


@csrf_exempt
def communities(request):
    
    if request.method == "POST":

        if "name" and "email" and "access_token" and "picture" in request.session:
            name = request.session["name"]
            email = request.session["email"]
            picture = request.session["picture"]
            access_token = request.session["access_token"]

            user_data = db.users.find_one({"email": email})

            if user_data:

                tags = request.POST.get("tags", None)
                print(request.POST)
                tags = tags.split(' ')

                coll = db.communities
                
                suggested_communities = coll.aggregate(
                    [
                        {"$match": {"tags": {"$in": tags}}},
                        {"$unwind": "$tags"},
                        {"$match": {"tags": {"$in": tags}}},
                        {"$group": {"_id": "$name", "count": {"$sum": 1}}},
                        {"$project": {"name": "$_id"}},
                        {"$sort": {"count": -1}}
                    ]
                )

                context = {
                    "name": name,
                    "picture": picture,
                    "suggested_communities": suggested_communities
                }

                return render(request, "onboard/select_communities.html", context)
            return HttpResponse("Unable to find user.")
        
        return HttpResponse("Please Login.")
    
    return HttpResponseRedirect("/login/welcome/")


@csrf_exempt
def get_more_tags(request):
    if request.method =="POST":
        param_text = request.body.decode('utf-8')
        params = json.loads(str(param_text))
        name = params["name"]
        communities = search_tags(name)
        print(communities)
        return HttpResponse(dumps(communities))
    print("njj")


@csrf_exempt
def get_communities(request):
    if request.method =="POST":
        param_text = request.body.decode('utf-8')
        params = json.loads(str(param_text))
        name = params["name"]
        communities = search_communities(name)
        print(communities)
        return HttpResponse(dumps(communities))
    print("njj")


@csrf_exempt
def create_user(request):
    if request.method =="POST":
        param_text = request.body.decode('utf-8')
        print("pt",param_text)
        params = json.loads(str(param_text))
        communities = params["communities"]
        print(communities)
        email = request.session["email"]
        post = db.users.update_one(
        {"email": email},
        {
            "$set": {
                "communities": communities
            },
            "$currentDate": {"lastModified": True}
        },True
    )
    return HttpResponse("done")