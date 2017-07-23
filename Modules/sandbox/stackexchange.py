import requests
import json
import multiprocessing
import pymongo
from pymongo import MongoClient
import json

client = MongoClient()
db = client.grid_database

def get_names():
    sites_name = list()
    sites_name_trimmed = list()
    for i in range(1, 10):

        i = str(i)

        url = "https://api.stackexchange.com/2.2/sites?page=" + i
        r = requests.get(url)
        for item in r.json().get('items'):

            name = item['name']
            sites_name.append(name)

    data = [{'sites_name': sites_name}]
    with open('stackexchange_sites.txt', 'w') as outfile:
        json.dump(data, outfile)


# get_names()


def get_tags():
    with open('stackexchange_sites.txt') as data_file:
        data = json.load(data_file)

    sites_name = data
    communities_tags = list()
    for site_name in sites_name:
        site_name_trimmed = site_name.replace(" ", "")
        tags = list()
        for page_name in range(1,5):

            url = "https://api.stackexchange.com/2.2/tags?page=%d&order=desc&sort=popular&site=%s" % (
                page_name, site_name_trimmed)

            r = requests.get(url)

            items = r.json().get('items')

            if items != None:
                for item in items:
                    tag = item['name']
                    tags.append(tag)

        communities_tag = [{
            site_name: tags
        }]
        communities_tags.append(communities_tag)
        del tags
        print(communities_tags)
    
    with open('stackexchange_communities_tags.txt', 'w') as outfile:
        json.dump(communities_tags, outfile)


#get_tags()


def process_url():
    with open('stackexchange_sites.txt') as data_file:
        data = json.load(data_file)
    left_community =list()
    for site_name in data:
        site_name_slashed = site_name.replace(" ","_")
        site_name_trimmed = site_name.replace(" ", "")
        
        url_new = "https://api.stackexchange.com/2.2/questions?order=desc&sort=activity&site="+site_name_trimmed
        r = requests.get(url_new)
        items  = r.json().get('items')
        if items != None:
            
            for item in items:
                posts = db[site_name_slashed]
                posts.insert_one(item)
        
#process_url()

urls =['webapps','gamedev','dba','ux','sqa']
urls_names = ['Web_applications','Game_development','Database_administrators','User_Experience','Software_Quality_Assurance_Testing']
i = 0
for url in urls:
    url_new = "https://api.stackexchange.com/2.2/questions?order=desc&sort=activity&site="+url
    print(url_new)
    r = requests.get(url_new)
    print(r.json())
    print(urls[i])
    items  = r.json().get('items')
    for item in items:
        posts = db[urls_names[i]]
        posts.insert_one(item)
    i+1
