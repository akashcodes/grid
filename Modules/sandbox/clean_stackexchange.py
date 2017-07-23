import json

def get_tags():
    with open('stackexchange_sites.txt') as data_file:
        data = json.load(data_file)
    sites_name = data[0]['sites_name']
    sites_name_meta = list()
    for name in sites_name:
        if 'Meta' in name:
            sites_name_meta.append(name)
            sites_name.remove(name)
    
    with open('stackexchange_sites_meta.txt', 'w') as outfile:
        json.dump(sites_name_meta, outfile)
    

    with open('stackexchange_sites.txt', 'w') as outfile:
        json.dump(sites_name, outfile)
#get_tags()

def remove_meta():
    with open('stackexchange_sites_meta.txt') as data_file:
        data = json.load(data_file)
        
        data_name = data
        sites_name =[]
        for name in data_name:
            print(name)
            try:
                name = name.replace(" Meta","")
                name = name.replace("Meta ","")
                name = name.replace("Meta","")
                sites_name.append(name)
                print("1",name)
            except ExplicitException:
                pass

        print(sites_name)
        with open('stackexchange_sites.txt', 'w') as outfile:
            json.dump(sites_name, outfile)
remove_meta()