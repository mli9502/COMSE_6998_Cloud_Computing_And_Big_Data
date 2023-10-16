import requests
import json
import time

# https://www.yelp.com/developers/v3/manage_app
apikey = 'Ki0G3hVJfHzHobPc8hMmsLetVogyPX-T7jRzKlUD9Iyc8mud5TjlsC4BYDRx0OeWt6Oy7IrsUxNFy8-E0ZlrCZiZIX1NrMmKH8cUA-7bh0sp2WZ0YN4mx77IIfwoZXYx'

url = "https://api.yelp.com/v3/businesses/search"
# categories can be found from https://docs.developer.yelp.com/reference/v3_all_categories
categories = ['newamerican', 'french', 'chinese', 'greek', 'japanese', 'malaysian', 'mediterranean', 'mexican', 'chicken_wings']

headers = {
    "accept": "application/json",
    "Authorization": 'Bearer ' + apikey,
}

resp_per_category = {}
restaurants = []
restaurant_ids = set()
for category in categories:
    resp_per_category[category] = {}
    print('category: ', category)
    for offset in range(0, 1000, 50):
        time.sleep(1)
        params = {
            'limit': 50,
            'location': 'New+York',
            'term': 'restaurants',
            'categories': category,
            'offset': offset,
        }
        resp = requests.get(url, headers=headers, params=params)
        if resp.status_code != 200:
            print('Got bad response: {} for params: {}'.format(resp, params))
            offset -= 50
            continue
        infos = resp.json()['businesses']
        for info in infos:
            if info['id'] in restaurant_ids:
                print('Found duplicate: ', info['name'])
                continue
            zip_code_int = 0
            try:
                zip_code_int = int(info['location']['zip_code'])
            except Exception as e:
                continue
            restaurant_ids.add(info['id'])
            print('{}: {}'.format(len(resp_per_category[category]), info['name']))
            resp_per_category[category][info['id']] = {
                'idx': len(restaurant_ids) - 1,
                'business_id': info['id'],
                'name': info['name'],
                'address': ', '.join(info['location']['display_address']),
                'coordinates': info['coordinates'],
                'number_of_reviews': info['review_count'],
                'rating': info['rating'],
                'zip_code': int(info['location']['zip_code']),
            }
with open('restaurants.json', 'w') as fd:
    fd.write(json.dumps(resp_per_category))

# If we need hours:
# https://docs.developer.yelp.com/graphql
# query MyQuery {
#   business(id: "fVbUVAiLiGgLA_nxBFxyww") {
#     hours {
#       hours_type
#       open {
#         day
#         end
#         is_overnight
#         start
#       }
#       is_open_now
#     }
#     messaging
#     location
#     special_hours
#   }
# }