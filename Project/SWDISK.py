import googlemaps
from datetime import datetime
import time
import random
import pprint
import numpy as np
import itertools as iter
import more_itertools as mi
import copy
import gmplot


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
                                'location': (51.1132,17.0584),
                                # 'location': (51.1117,17.0602),
                                # 'location': (51.095, 17.0146),
                                'radius': 1300
                             }
        self.gplot = gmplot.GoogleMapPlotter(self.search_params['location'][0],self.search_params['location'][1],15,apikey=api_key)
        #travel modes of deliverers
        self.travel_mode = ('walking')
        #travel time matrixes (in seconds)
        #D - DELIVERER , R - RESTAURANT, C - CLIENT
        #2D numpy arrays of seconds of travel between DR(deliverer <--> restaurant)
        self.travel_time_DR = np.arange(self.deliverers_quantity*self.restaurants_quantity).reshape(
            self.deliverers_quantity,self.restaurants_quantity)
        self.travel_time_RC = np.arange(self.restaurants_quantity * self.restaurants_quantity).reshape(
            self.restaurants_quantity, self.restaurants_quantity)
        self.travel_time_DC = np.arange(self.deliverers_quantity*self.restaurants_quantity).reshape(
            self.deliverers_quantity,self.restaurants_quantity)

        self.travel_time_RR = np.arange(self.restaurants_quantity * self.restaurants_quantity).reshape(
            self.restaurants_quantity, self.restaurants_quantity)
        self.travel_time_CC = np.arange(self.restaurants_quantity * self.restaurants_quantity).reshape(
            self.restaurants_quantity, self.restaurants_quantity)

        # distance matrixes(in meters)
        # D - DELIVERER , R - RESTAURANT, C - CLIENT
        # 2D numpy arrays of seconds of travel between DR(deliverer <--> restaurant)
        self.distance_DR = np.arange(self.deliverers_quantity * self.restaurants_quantity).reshape(
            self.deliverers_quantity, self.restaurants_quantity)
        self.distance_RC = np.arange(self.restaurants_quantity * self.restaurants_quantity).reshape(
            self.restaurants_quantity, self.restaurants_quantity)
        self.distance_DC = np.arange(self.deliverers_quantity * self.restaurants_quantity).reshape(
            self.deliverers_quantity, self.restaurants_quantity)

        self.distance_RR = np.arange(self.restaurants_quantity * self.restaurants_quantity).reshape(
            self.restaurants_quantity, self.restaurants_quantity)
        self.distance_CC = np.arange(self.restaurants_quantity * self.restaurants_quantity).reshape(
            self.restaurants_quantity, self.restaurants_quantity)

        self.generate_restaurants()
        self.generate_deliverers()
        self.generate_clients()
        self.assign_clients_restaurants()
        self.count_time_distance_DC()
        self.count_time_distance_DR()
        self.count_time_distance_RC()
        self.count_time_distance_RR()
        self.count_time_distance_CC()



    def generate_restaurants(self):
        #adds restaurants to restaurants dictionary according to search parameters
        #now searching restaurants in 500 meters radius from pasaż grunwaldzki
        restaurants_data = self.gmaps.places(**self.search_params)
        for i in range(self.restaurants_quantity):
            self.restaurants[i] = {'name': restaurants_data['results'][i]['name'],
                                   'loc': ((restaurants_data['results'][i]['geometry']['location']['lat'],
                                            restaurants_data['results'][i]['geometry']['location']['lng'])),
                                   'client': None
                                   }

    def generate_deliverers(self):
        # adds deliverers to deliverers dictionary
        # now locations of deliverers are randomly generated 'around' pasaż grunwaldzki in (more or less) 1,5km radius
        for i in range(self.deliverers_quantity):
            self.deliverers[i] = {'loc' : (random.uniform(51.1070, 51.1175),random.uniform(17.055, 17.065)),
                                  'travel_mode':'driving',
                                  'orders': []}

    def generate_clients(self):
        #adds clients to dictionary
        # now locations of clients are randomly generated 'around' pasaż grunwaldzki in (more or less) 1,5km radius
        for i in range(self.restaurants_quantity):
            self.clients[i] = {'loc': (random.uniform(51.1070, 51.1175), random.uniform(17.055, 17.065))}

    def assign_clients_restaurants(self):
         for key,client_id in zip(self.restaurants.keys(),self.clients):
             self.restaurants[key]['client'] = client_id

    def count_time_distance_DR(self):
        #fills travel distance and time matrixes between deliverers and restaurants
        for deliverer in self.deliverers:
            for restaurant in self.restaurants:
                distance = self.gmaps.distance_matrix(self.deliverers[deliverer]['loc'], self.restaurants[restaurant]['loc'],self.deliverers[deliverer]['travel_mode'])
                self.travel_time_DR[deliverer][restaurant] = distance['rows'][0]['elements'][0]['duration']['value']
                self.distance_DR[deliverer][restaurant] = distance['rows'][0]['elements'][0]['distance']['value']

    # def count_travel_time_RC(self):
    #     # fills travel time matrix between restaurants and clients
    #     for restaurant in self.restaurants:
    #         for client in self.clients:
    #             distance = self.gmaps.distance_matrix(self.restaurants[restaurant]['loc'], self.clients[client]['loc'],self.deliverers[deliverer]['travel_mode'])
    #             self.travel_time_RC[restaurant][client] = distance['rows'][0]['elements'][0]['duration']['value']

    def count_time_distance_DC(self):
        #fills travel distance and time matrixes  between deliverers and clients
        for deliverer in self.deliverers:
            for client in self.clients:
                distance = self.gmaps.distance_matrix(self.deliverers[deliverer]['loc'], self.clients[client]['loc'],self.deliverers[deliverer]['travel_mode'])
                self.travel_time_DC[deliverer][client] = distance['rows'][0]['elements'][0]['duration']['value']
                self.distance_DC[deliverer][client] = distance['rows'][0]['elements'][0]['distance']['value']

    def count_time_distance_RC(self):
        # fills travel time matrix between restaurants and clients
        for restaurant in self.restaurants:
            for client in self.clients:
                distance = self.gmaps.distance_matrix(self.restaurants[restaurant]['loc'], self.clients[client]['loc'],'driving')
                self.distance_RC[restaurant][client] = distance['rows'][0]['elements'][0]['distance']['value']
                self.travel_time_RC[restaurant][client] = distance['rows'][0]['elements'][0]['duration']['value']

    def count_time_distance_RR(self):
        # fills travel time matrix between restaurants
        for restaurant in self.restaurants:
            for client in self.clients:
                distance = self.gmaps.distance_matrix(self.restaurants[restaurant]['loc'], self.restaurants[client]['loc'],'driving')
                self.distance_RR[restaurant][client] = distance['rows'][0]['elements'][0]['distance']['value']
                self.travel_time_RR[restaurant][client] = distance['rows'][0]['elements'][0]['duration']['value']

    def count_time_distance_CC(self):
        # fills travel time matrix between restaurants
        for restaurant in self.restaurants:
            for client in self.clients:
                distance = self.gmaps.distance_matrix(self.clients[restaurant]['loc'], self.clients[client]['loc'],'driving')
                self.distance_CC[restaurant][client] = distance['rows'][0]['elements'][0]['distance']['value']
                self.travel_time_CC[restaurant][client] = distance['rows'][0]['elements'][0]['duration']['value']


    def cost_function(self,distance ,delivery_price ,duration, travel_mode,deliverer_pay = 12,transport_cost = None):
        if travel_mode == 'driving':
            transport_cost = 0.83
        elif travel_mode == 'bicycling':
            transport_cost = 0.05
        else:
            transport_cost = 0

        return distance/1000 * delivery_price - duration/3600 * deliverer_pay - distance/1000 * transport_cost # 3,6 * 5 - 0,069 * 12 - 3,6 * 0.83

    def cost_function_DR(self, distance, delivery_price, duration, travel_mode, deliverer_pay=12, transport_cost=None):
        if travel_mode == 'driving':
            transport_cost = 0.83
        elif travel_mode == 'bicycling':
            transport_cost = 0.05
        else:
            transport_cost = 0

        return - duration / 3600 * deliverer_pay - distance / 1000 * transport_cost  # 3,6 * 5 - 0,069 * 12 - 3,6 * 0.83

    def draw_map(self):
        for deliverer in self.deliverers:
            self.gplot.marker(self.deliverers[deliverer]['loc'][0],
                              self.deliverers[deliverer]['loc'][1],
                              color='green',
                              title= 'Deliverer {}'.format(deliverer))
        for restaurant,client in zip(self.restaurants,self.clients):
            self.gplot.marker(self.restaurants[restaurant]['loc'][0],
                              self.restaurants[restaurant]['loc'][1],
                              color='red',
                              title= '{} - {}'.format(str(self.restaurants[restaurant]['name'].encode(encoding='ascii',errors = 'ignore'),"utf-8"),restaurant))
            self.gplot.marker(self.clients[client]['loc'][0],
                              self.clients[client]['loc'][1],
                              color = 'blue',
                              title = 'Client {}'.format(client))
        self.gplot.draw('map.html')


    def helper(self, stations, final_station):
        time = 0
        rc_dict = {}
        for orders in stations:
            rc_dict[orders] = int(orders[1:])
        for i in range(len(stations)-1):
            if stations[i] == final_station:
                break
            if stations[i][0] == 'r' and stations[i+1][0] == 'r':
                time += self.travel_time_RR[rc_dict[stations[i]]][rc_dict[stations[i+1]]]
            elif stations[i][0] == 'r' and stations[i+1][0] == 'c':
                time += self.travel_time_RC[rc_dict[stations[i]]][rc_dict[stations[i + 1]]]
            elif stations[i][0] == 'c' and stations[i+1][0] == 'r':
                time += self.travel_time_RC[rc_dict[stations[i+1]]][rc_dict[stations[i]]]
            else:
                time += self.travel_time_CC[rc_dict[stations[i]]][rc_dict[stations[i+1]]]
        return time

    def brute_force(self):
        combinations = []
        deliv = [i for i in range(self.deliverers_quantity)]
        rest = [i for i in range(self.restaurants_quantity)]
        r_combinations = mi.powerset(rest)
        comb_iter = iter.combinations(r_combinations, self.deliverers_quantity)
        before_perm = []
        for i in comb_iter:
            temp = []
            for j in i:
                for z in j:
                    temp.append(z)
            if sorted(temp) == rest:
                before_perm.append(i)
        for i in before_perm:
            k = iter.permutations(i)
            for j in k:
                combinations.append(j)
        total_cost = 0
        final_combination=[]
        best_delivery_times = []
        for comb in combinations:
            i_combination = []
            delivery_times = []
            cost = 0
            for orders,deliverer in zip(comb,range(self.deliverers_quantity)):
                if len(orders) == 0:
                    i_combination.append(orders)
                    delivery_times.append(0)
                    continue
                elif len(orders) == 1:
                    cost += self.cost_function_DR(self.distance_DR[deliverer][orders[0]],5,
                                               self.travel_time_DR[deliverer][orders[0]],'driving')
                    cost += self.cost_function(self.distance_RC[orders[0]][orders[0]], 5,
                                               self.travel_time_RC[orders[0]][orders[0]], 'driving')
                    i_combination.append(orders)
                    delivery_times.append(self.travel_time_DR[deliverer][orders[0]] + self.travel_time_RC[orders[0]][orders[0]])
                else:
                    rc_dict ={}
                    rc_list = []
                    r_dict = {}
                    for i in orders:
                        r_dict[f'r{i}'] = i
                        rc_list.append(f'r{i}')
                    c_dict = {}
                    for i in orders:
                        c_dict[f'c{i}'] = i
                        rc_list.append(f'c{i}')
                    rc_dict = {**c_dict,**r_dict}

                    # max_cost = 0
                    # perm_max = None
                    best_perm_value = 0
                    best_perm = None
                    best_time = 0
                    for perm in iter.permutations(rc_list):
                        perm_cost = 0  #koszt dla danej permutacji
                        perm_time = 0
                        possible_combination_flag = True
                        for c,r in zip(c_dict.keys(),r_dict.keys()):
                            if perm.index(c) < perm.index(r):
                                possible_combination_flag = False

                        if possible_combination_flag == False:
                            break
                        else:
                            perm_cost += self.cost_function_DR(self.distance_DR[deliverer][rc_dict[perm[0]]],5,
                                           self.travel_time_DR[deliverer][orders[0]],'driving')
                            perm_time += self.travel_time_DR[deliverer][orders[0]]
                            for place_index in range(len(perm)-1):
                                if perm[place_index][0] == 'r' and perm[place_index+1][0] == 'c':
                                    perm_time += self.helper(perm,perm[place_index+1])
                                    if perm_time > 2400:
                                        perm_cost += self.cost_function_DR(
                                            self.distance_RC[c_dict[perm[place_index+1]]][c_dict[perm[place_index + 1]]],
                                            5,
                                            self.travel_time_RC[r_dict[perm[place_index]]][
                                                c_dict[perm[place_index + 1]]],
                                            'driving')
                                    else:
                                        perm_cost += self.cost_function(
                                            self.distance_RC[r_dict[perm[place_index]]][c_dict[perm[place_index + 1]]],
                                            5,
                                            self.travel_time_RC[r_dict[perm[place_index]]][
                                                c_dict[perm[place_index + 1]]],
                                            'driving')
                                elif perm[place_index][0] == 'c' and perm[place_index+1][0] == 'r':
                                    perm_cost += self.cost_function(self.distance_RC[r_dict[perm[place_index + 1]]][
                                                                        c_dict[perm[place_index]]],
                                                                    5,
                                                                    self.travel_time_RC[
                                                                        r_dict[perm[place_index + 1]]][
                                                                        c_dict[perm[place_index]]],
                                                                    'driving')
                                    perm_time  += self.travel_time_RC[
                                                                        r_dict[perm[place_index + 1]]][
                                                                        c_dict[perm[place_index]]]
                                elif perm[place_index][0] == 'r' and perm[place_index+1][0] == 'r':
                                    perm_cost += self.cost_function(self.distance_RR[r_dict[perm[place_index]]][r_dict[perm[place_index + 1]]],
                                                                    5,
                                                                    self.travel_time_RR[r_dict[perm[place_index]]][r_dict[perm[place_index + 1]]],
                                                                    'driving')
                                    perm_time += self.travel_time_RR[r_dict[perm[place_index]]][r_dict[perm[place_index + 1]]]
                                else:
                                    perm_time += self.helper(perm,perm[place_index+1])
                                    if perm_time > 2400:
                                        perm_cost += self.cost_function_DR(
                                            self.distance_RC[c_dict[perm[place_index + 1]]][c_dict[perm[place_index + 1]]],
                                            5,
                                            self.travel_time_CC[c_dict[perm[place_index]]][
                                                c_dict[perm[place_index + 1]]],
                                            'driving')
                                    else:
                                        perm_cost += self.cost_function(
                                            self.distance_CC[c_dict[perm[place_index]]][c_dict[perm[place_index + 1]]],
                                            5,
                                            self.travel_time_CC[c_dict[perm[place_index]]][
                                                c_dict[perm[place_index + 1]]],
                                            'driving')
                        if perm_cost > best_perm_value:
                            best_perm_value = perm_cost
                            best_perm = perm
                            best_time = perm_time
                    cost+= best_perm_value
                    delivery_times.append(best_time)
                    i_combination.append(best_perm)
            if cost > total_cost:
                total_cost = cost
                final_combination = i_combination
                best_delivery_times = delivery_times
        results_dict = {
            'combination' : final_combination,
            'total_cost' : total_cost,
            'Delivery times' : delivery_times
        }
        return results_dict
    def heuristic(self):
        pass
    #
    #
    # def test(self):
    #     x = iter.permutations([self.restaurants[0],self.restaurants[1],self.clients[0],self.clients[1]])
    #     for i in x:
    #         print(i)





def main():
    finder = UberFinder(api_key,4,3)
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
    print('TRAVEL TIMES RESTAURANT - RESTAURANT')
    print(finder.travel_time_RR)
    print('TRAVEL TIMES CLIENT - CLIENT')
    print(finder.travel_time_CC)
    print('---------------------')
    print('DISTANCE MATRIXES')
    print('DISTANCE MATRIX DELIVERER - RESTAURANT')
    print(finder.distance_DR)
    print('DISTANCE DELIVERER - CLIENT')
    print(finder.distance_DC)
    print('DISTANCE RESTAURANT - CLIENT')
    print(finder.distance_RC)
    print('DISTANCE RESTAURANT - RESTAURANT')
    print(finder.distance_RR)
    print('DISTANCE CLIENT - CLIENT')
    print(finder.distance_CC)
    finder.draw_map()
    pp.pprint(finder.brute_force())

if __name__ == '__main__':
    main()