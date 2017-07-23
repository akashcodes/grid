# -*- coding: utf-8 -*-
from __future__ import unicode_literals
import pprint
import json
import time

import requests

from bson.json_util import dumps
from django.http import HttpResponse, HttpResponseRedirect
from django.shortcuts import redirect, render,render_to_response
from django.views.decorators.csrf import csrf_exempt
from grid.settings import app_id, app_secret
from Modules.tags.interest import get_interest, search_communities
from pymongo import MongoClient

client = MongoClient()
db = client.grid_database
# Create your views here.
@csrf_exempt
def question_display(request,community_name,question_id):
    access_token =  request.session["access_token"]
    fetch_question = db[community_name]
    question = fetch_question.find_one({"question_id": int(question_id)})
    context= {"question":question,"editor": True, "preview": True}
    return render(request, "questions/index.html",context)