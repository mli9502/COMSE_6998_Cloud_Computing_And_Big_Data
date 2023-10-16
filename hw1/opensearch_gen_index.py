import json
import os
import numbers
import time

def convert_to_index(restaurant, idx_list):
    # print(restaurant)
    idx_json = {
        "index": {
            "_index": "restaurants",
            "_id": time.time_ns()
        }
    }
    idx_list.append(idx_json)
    doc_json = {
        "RestaurantID": restaurant['business_id'],
        "Cuisine": restaurant['category']
    }
    idx_list.append(doc_json)

def gen_index_file(idx_list):
    with open('restaurants_index.json', 'w') as fd:
        for entry in idx_list:
            json.dump(entry, fd)
            fd.write('\n')

# `region` needs to be the same as where db is created.
def gen_cmd():
    config_json = json.load(open('restaurants_index_config.json'))
    print(config_json)
    return "curl -XPOST -u {}:{} {}/_bulk --data-binary @{} -H 'Content-Type: application/json'".format(config_json['MASTER_NAME'], config_json['MASTER_PASSWORD'], config_json['DOMAIN_ENDPOINT'], config_json['JSON_FILENAME'])

restaurants = json.load(open('restaurants.json'))

idx_list = []
for category in restaurants:
    category_restaurants = restaurants[category]
    for id in category_restaurants:
        curr = category_restaurants[id]
        curr['category'] = category
        convert_to_index(curr, idx_list)

gen_index_file(idx_list)
cmd = gen_cmd()
print(cmd)
os.system(cmd)