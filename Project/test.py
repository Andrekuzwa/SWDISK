import random
import googlemaps
from datetime import datetime
import pprint
import time

gmaps = googlemaps.Client(key='AIzaSyCwpVdTaCjH7QzsduH3Jb0XP548eUzSSDw')
api_key = 'AIzaSyCwpVdTaCjH7QzsduH3Jb0XP548eUzSSDw'
# Geocoding an address
geocode_result = gmaps.geocode('1600 Amphitheatre Parkway, Mountain View, CA')

# Look up an address with reverse geocoding
reverse_geocode_result = gmaps.reverse_geocode((40.714224, -73.961452))

# Request directions via public transit
now = datetime.now()
directions_result = gmaps.directions("Sydney Town Hall",
                                     "Parramatta, NSW",
                                     mode="walking",
                                     departure_time=now)
#godz 16 - 1601564400
#godzina 1:00 - 1601510400
distance = gmaps.distance_matrix('Wrocław Vertigo Jazz Club & Restaurant',(51.1117,17.0602),'driving',departure_time=1601510400,traffic_model = 'pessimistic')



# print(geocode_result)
# print(reverse_geocode_result)
# print(directions_result)
pp = pprint.PrettyPrinter(indent=1)
pp.pprint(distance)
print(distance['rows'][0]['elements'][0]['distance']['value'],distance['rows'][0]['elements'][0]['distance']['text'])
print(distance['rows'][0]['elements'][0]['duration']['value'],distance['rows'][0]['elements'][0]['duration']['text'])
print(distance['rows'][0]['elements'][0]['duration_in_traffic']['value'],distance['rows'][0]['elements'][0]['duration_in_traffic']['text'])
# print(distance)
#
#
# params = {
#     'query': ['restaurants'],
#     'location': (51.1117,17.0602),
#     'radius': 500
# }
#
# restaurants_list = gmaps.places(**params)
# # pp.pprint([i['name'] for i in restaurants_list['results']])
# pp.pprint(restaurants_list)
# # pp.pprint(restaurants_list['results'])
# list1 = []
# dict1 = {}
# dict_key = 'name','location'
# for result in restaurants_list['results']:
#     # list1.append(dict  (result['name'],(result['geometry']['location']['lat'],result['geometry']['location']['lng'])))
#     dict1[result['name']] = (result['geometry']['location']['lat'],result['geometry']['location']['lng'])
#
# print(list1)
# print(dict1)
# for key,value in dict1.items():
#     distance1 = gmaps.distance_matrix(value, (51.1117, 17.0602), 'walking')
#     print(distance1['rows'][0]['elements'][0]['distance']['value'],distance1['rows'][0]['elements'][0]['distance']['text'])
#     time.sleep(2)


#lewygorny 51.1201,17.0424
#pasaz     51.1117, 17.0602
#          0.0084, -0.0178
#          51.1033 , 17.0602

#51.1172, 17.049  lewy gotny
#51.1038, 17.0497 lewy dolny
#51.1048 ,17.0707 prawy dolny
#51.1178, 17.0698 prawy gorny


# 51.1175, 17.05  lewy gotny
# 51.1040, 17.05 lewy dolny
# 51.1040 ,17.07 prawy dolny
# 51.1175, 17.07 prawy gorny

# params['page_token'] = restaurants_list['next_page_token']
#
# time.sleep(2)
#
# restaurants_list1 = gmaps.places(**params)
#
#
# pp.pprint([i['name'] for i in restaurants_list1['results']])
#
# params['page_token'] = restaurants_list1['next_page_token']
#
# time.sleep(2)
# restaurants_list2 = gmaps.places(**params)
# pp.pprint([i['name'] for i in restaurants_list2['results']])
#

