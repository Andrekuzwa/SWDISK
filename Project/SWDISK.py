import googlemaps
from datetime import datetime
import time
import random
import pprint
import numpy as np

pp = pprint.PrettyPrinter(indent=1)
api_key = 'AIzaSyCwpVdTaCjH7QzsduH3Jb0XP548eUzSSDw'

class UberFinder:

    def __init__(self, api_key, restaurants_quantity,deliverers_quantity):
        self.restaurants_quantity = restaurants_quantity
        self.deliverers_quantity = deliverers_quantity
        self.gmaps = googlemaps.Client(key=api_key)

        #dictionary of restaurants in form
        #{id:{
        #       'loc':(float,float)
        #       'name': string
        #       'client': client_id
        #     }
        # }
        self.restaurants = {}
        # dictionary of deliverers in form
        # {id:{
        #       'loc':(float,float)
        #       'orders': list
        #       'travel_mode': string (driving/walking/bycicling)
        #     }
        # }
        self.deliverers = {}
        #dictionary
        # {id:{
        #       'loc':(float,float)
        #     }
        # }
        self.clients = {}

        #parameters for gmaps api search
        self.search_params = {
                                'query': ['restaurants'],
                                'location': (51.1117,17.0602),
                                'radius': 500
                             }
        #travel modes of deliverers
        self.travel_mode = ('walking','bicycling','driving')

        #travel time matrixes
        #D - DELIVERER , R - RESTAURANT, C - CLIENT
        #2D numpy arrays of seconds of travel between DR(deliverer <--> restaurant)
        self.travel_time_DR = np.arange(self.deliverers_quantity*self.restaurants_quantity).reshape(
            self.deliverers_quantity,self.restaurants_quantity)
        self.travel_time_RC = np.arange(self.restaurants_quantity * self.restaurants_quantity).reshape(
            self.restaurants_quantity, self.restaurants_quantity)
        self.travel_time_DC = np.arange(self.deliverers_quantity*self.restaurants_quantity).reshape(
            self.deliverers_quantity,self.restaurants_quantity)

        self.generate_restaurants()
        self.generate_deliverers()
        self.generate_clients()
        self.assign_clients_restaurants()
        self.count_travel_time_DR()
        self.count_travel_time_RC()
        self.count_travel_time_DC()

    def generate_restaurants(self):
        #adds restaurants to restaurants dictionary according to search parameters
        #now searching restaurants in 500 meters radius from pasaż grunwaldzki
        restaurants_data = self.gmaps.places(**self.search_params)
        for i in range(self.restaurants_quantity):
            self.restaurants[i] = {'name': restaurants_data['results'][i]['name'],
                                   'loc': ((restaurants_data['results'][i]['geometry']['location']['lat'],
                                            restaurants_data['results'][i]['geometry']['locat  ion']['lng'])),
                                   'client': None
                                   }

    def generate_deliverers(self):
        # adds deliverers to deliverers dictionary
        # now locations of deliverers are randomly generated 'around' pasaż grunwaldzki in (more or less) 1,5km radius
        for i in range(self.deliverers_quantity):
            self.deliverers[i] = {'loc' : (random.uniform(51.1070, 51.1175),random.uniform(17.055, 17.065)),
                                  'travel_mode':random.choice(self.travel_mode),
                                  'orders': []}

    def generate_clients(self):
        #adds clients to dictionary
        # now locations of clients are randomly generated 'around' pasaż grunwaldzki in (more or less) 1,5km radius
        for i in range(self.restaurants_quantity):
            self.clients[i] = {'loc': (random.uniform(51.1070, 51.1175), random.uniform(17.055, 17.065))}

    def assign_clients_restaurants(self):
         for key,client_id in zip(self.restaurants.keys(),self.clients):
             self.restaurants[key]['client'] = client_id

    def count_travel_time_DR(self):
        #fills travel time matrix between deliverers and restaurants
        for deliverer in self.deliverers:
            for restaurant in self.restaurants:
                distance = self.gmaps.distance_matrix(self.deliverers[deliverer]['loc'], self.restaurants[restaurant]['loc'],'walking')
                self.travel_time_DR[deliverer][restaurant] = distance['rows'][0]['elements'][0]['duration']['value']


    def count_travel_time_RC(self):
        # fills travel time matrix between restaurants and clients
        for restaurant in self.restaurants:
            for client in self.clients:
                distance = self.gmaps.distance_matrix(self.restaurants[restaurant]['loc'], self.clients[client]['loc'],'walking')
                self.travel_time_RC[restaurant][client] = distance['rows'][0]['elements'][0]['duration']['value']

    def count_travel_time_DC(self):
        # fills travel time matrix between deliverers and clients
        for deliverer in self.deliverers:
            for client in self.clients:
                distance = self.gmaps.distance_matrix(self.deliverers[deliverer]['loc'], self.clients[client]['loc'],'walking')
                self.travel_time_DC[deliverer][client] = distance['rows'][0]['elements'][0]['duration']['value']


def main():
    finder = UberFinder(api_key,5,4)
    print('RESTAURANTS')
    pp.pprint(finder.restaurants)
    print("DELIVERERRS")
    pp.pprint(finder.deliverers)
    print("CLIENTS")
    pp.pprint(finder.clients)
    print('TRAVEL TIME MATRIXES')
    print('TRAVEL TIMES DELIVERER - RESTAURANT')
    print(finder.travel_time_DR)
    print('TRAVEL TIMES RESTAURANT - CLIENT')
    print(finder.travel_time_RC)
    print('TRAVEL TIMES DELIVERER - CLIENT')
    print(finder.travel_time_DC)

if __name__ == '__main__':
    main()