from collections import Counter

from textblob import TextBlob

from pymongo import MongoClient

client = MongoClient()
db = client.grid_database
def get_interest(likes):

    
    collection = db.tags

    interest = list()
    for like in likes:
        if 'about' in like:
            about = like['about']
            about = TextBlob(about)
            propernouns = about.noun_phrases
            interest.extend(propernouns)

        else:
            pass

        if 'name' in like:

            name = like['name']
            name = TextBlob(name)
            propernouns = name.noun_phrases
            interest.extend(propernouns)

        else:
            pass

        if 'category' in like:
            category = like['category']
            interest.append(category)

        else:
            pass

    interest = filter(None, interest)
    interest = set(interest)
    #print(interest)

    suggested_communities = list()

    for i in interest:
        cursor = db.communities.find(
            {'$text': {'$search': i}},
            {'score': {'$meta': 'textScore'}})
        cursor.sort([('score', {'$meta': 'textScore'})])
        
        cursor = cursor[2:]
        
        for doc in cursor:
            if doc['score'] >1.0:
                suggested_communities.append(doc['name'])

    suggested_communities = Counter(suggested_communities).most_common(10)
    
    
   
    return suggested_communities

def search_communities(name):
    print("name",name)
    cursor = db.communities.find({"$text": {"$search":name}})
    
    searched_communities=list()
    for doc in cursor:
        searched_communities.append(doc['name'])
    print(searched_communities)
    return searched_communities
