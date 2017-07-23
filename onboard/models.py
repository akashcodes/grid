from django.db import models
import requests
from pymongo import MongoClient
# Create your models here.


class login:
    def __init__(self):
        self.client = MongoClient
        self.db = self.client.namesake


    def facebook_login():
        app_id = 443767629321246
        redirect_uri = "http://localhost:8000/login"
        login_dialouge_url = "https://www.facebook.com/v2.9/dialog/oauth?client_id="+app_id+"&redirect_uri="+redirect_uri+"&display =popup&response_type=token"
        r = requests.get(login_dialouge_url)
        print(r.json())
        try:
            return(r.json()['access_token'])
        except:
            return("error")
