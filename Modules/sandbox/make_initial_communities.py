import pymongo
from pymongo import MongoClient
import json

client = MongoClient()
db = client.grid_database
with open('stackexchange_communities_tags.txt') as data_file:
        data = json.load(data_file)
        my_dict = {}
        communities = list()
        for i in data:
            my_dict = i[0]
            print(my_dict.keys())
            key = my_dict.keys()[0]
            values = my_dict.values()[0]
            community = {"name":key,"tags":values}
            communities.append(community)
        print(communities)
''' 
communities =[{
        "name":"Programming",
        "tags":["python","java","javascript","html","threading","async","database"]
    },
    {
        "name":"database admins",
        "tags":["mysql","sql","database","oracle","sql-server"]
    },
    {
        "name":"Artificial intelligence",
        "tags":["neural network","machine learning","loss function","tensorflow"]
    },
    {
        "name":"graphic design",
        "tags":["photoshop","design","pdf","svg"]
    },
    {
        "name":"wildlife",
        "tags":["python","snakes"]
    },
    {
        "name":"woodworks",
        "tags":["circa","axe-type","wood moisture"]
    }
    ]
'''
posts = db.communities
posts.insert_many(communities)

posts.create_index([("name", pymongo.TEXT),("tags", pymongo.TEXT)])
