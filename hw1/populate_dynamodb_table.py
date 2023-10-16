import json
import os
import numbers
import time

def convert_to_input(restaurant):
    print(restaurant)
    rtn = {}
    rtn['insertedAtTimestamp'] = {
        "S": str(time.time_ns())
    }
    time.sleep(0.001)
    for k in restaurant:
        if k == 'coordinates':
            rtn[k] = {
                "M": {
                    "latitude": {
                        "N": str(restaurant[k]["latitude"])
                    },
                    "longitude": {
                        "N": str(restaurant[k]["longitude"])
                    }
                }
            }
        elif isinstance(restaurant[k], numbers.Number):
            rtn[k] = {
                "N": str(restaurant[k])
            }
        else:
            rtn[k] = {
                "S": restaurant[k].replace(r"'", r"????")
            }
    return str(rtn).replace(r"'", r'"').replace(r"????", r"'\''")

# `region` needs to be the same as where db is created.
def gen_cmd(restaurant):
    return 'aws dynamodb put-item --table yelp-restaurants --item \'{}\' --region us-east-1'.format(convert_to_input(restaurant))

restaurants = json.load(open('restaurants.json'))

for category in restaurants:
    category_restaurants = restaurants[category]
    for id in category_restaurants:
        curr = category_restaurants[id]
        curr['category'] = category
        cmd = gen_cmd(curr)
        print(cmd)
        if os.system(cmd) != 0:
            print('Failed command: {}'.format(cmd))
