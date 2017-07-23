from pymongo import MongoClient

client = MongoClient()
db = client.grid_database
collection = db.tags