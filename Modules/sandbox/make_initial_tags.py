#import pymongo
#from pymongo import MongoClient
from Modules.db import client
'''
client = MongoClient()
db = client.grid_database
collection = db.tags

tag =[{
        "name":"python",
        "communities":["programming","wildlife","data science","software engineering"]
    },
    {
        "name":"design",
        "communities":["arts","software design"]
    }
    ]

posts = db.tags
#posts.insert_many(tag)

print(dbclient.Mongo.fetch("grid_databse","tags","{'name':'python'}"))
'''