from pymongo import MongoClient
from bson.json_util import dumps
import json

# Create your models here.

class Mongo:

	client = None

	def __init__(self, host="localhost", port=27017):
		self.client = MongoClient(host, port)

	def insert(self, database, collection, document):
		return self.client[database][collection].insert(document)

	def fetch(self, database, collection, query, one=True):
		if one:
			return json.loads(dumps(self.client[database][collection].find_one(*query)))
		return json.loads(dumps(self.client[database][collection].find(*query)))

	def update(self, database, collection, query):
		return self.client[database][collection].update(*query)

	def __del__(self):
		self.client.close()

print("hrllo")