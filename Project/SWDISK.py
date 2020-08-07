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
api_key = '******************************************'
colors = ['blue','green','red','black']

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
                                # 'location': (51.1132,17.0584),
                                'location': (51.080131, 17.004544),
                                # 'location': (51.098965, 17.017979),


                                'radius': 2000
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
        #51.1 - 51.095    17.004 - 17.04
    def generate_deliverers(self):
        # adds deliverers to deliverers dictionary
        # now locations of deliverers are randomly generated 'around' pasaż grunwaldzki in (more or less) 1,5km radius
        for i in range(self.deliverers_quantity):
            self.deliverers[i] = {'loc' : (random.uniform(51.0801 , 51.1110),random.uniform(17.00401, 17.0601)),
                                  'travel_mode':'driving',
                                  'orders': []}

    def generate_clients(self):
        #adds clients to dictionary
        # now locations of clients are randomly generated 'around' pasaż grunwaldzki in (more or less) 1,5km radius
        for i in range(self.restaurants_quantity):
            self.clients[i] = {'loc': (random.uniform(51.0801 , 51.1110), random.uniform(17.00401, 17.0601))}

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

        return distance/1000 * delivery_price - duration/3600 * deliverer_pay - distance/1000 * transport_cost

    def cost_function_income(self,distance ,delivery_price):
        return distance/1000 * delivery_price

    def cost_function_DR(self, distance, delivery_price, duration, travel_mode, deliverer_pay=12, transport_cost=None):
        if travel_mode == 'driving':
            transport_cost = 0.83
        elif travel_mode == 'bicycling':
            transport_cost = 0.05
        else:
            transport_cost = 0

        return - duration / 3600 * deliverer_pay - distance / 1000 * transport_cost  # 3,6 * 5 - 0,069 * 12 - 3,6 * 0.83

    def income(self,stations):
        income = 0
        for station in stations:
            if station[0] == 'r':
                income += self.cost_function_income(self.distance_RC[int(station[1:])][int(station[1:])],5)
        return income


    def draw_map(self,result,mode,algorythm):
        for deliverer in self.deliverers:
            self.gplot.marker(self.deliverers[deliverer]['loc'][0],
                              self.deliverers[deliverer]['loc'][1],
                              color='green',
                              title= 'Deliverer {}'.format(deliverer))
            self.gplot.text(self.deliverers[deliverer]['loc'][0],
                              self.deliverers[deliverer]['loc'][1], 'Deliverer {}'.format(deliverer))
        for restaurant,client in zip(self.restaurants,self.clients):
            self.gplot.marker(self.restaurants[restaurant]['loc'][0],
                              self.restaurants[restaurant]['loc'][1],
                              color='red',
                              title= '{} - {}'.format(str(self.restaurants[restaurant]['name'].encode(encoding='ascii',errors = 'ignore'),"utf-8"),restaurant))
            self.gplot.text(self.restaurants[restaurant]['loc'][0],
                            self.restaurants[restaurant]['loc'][1], 'Restaurant {}'.format(restaurant))
            self.gplot.marker(self.clients[client]['loc'][0],
                              self.clients[client]['loc'][1],
                              color = 'blue',
                              title = 'Client {}'.format(client))
            self.gplot.text(self.clients[client]['loc'][0],
                            self.clients[client]['loc'][1], 'Client {}'.format(client))
        if mode == 'route':
            for orders,index in zip(result,range(len(result))):
                if len(orders) == 0:
                    continue
                elif len(orders) == 1:
                    self.gplot.directions(
                        self.deliverers[index]['loc'],
                        self.clients[orders[0]]['loc'],
                        waypoints=[
                            self.restaurants[orders[0]]['loc']
                        ]
                    )
                else:
                    loc_points = []
                    for station in orders:
                        if station[0] == 'r':
                            loc_points.append(self.restaurants[int(station[1:])]['loc'])
                        else:
                            loc_points.append(self.clients[int(station[1:])]['loc'])
                    self.gplot.directions\
                        (
                            self.deliverers[index]['loc'],
                            loc_points[-1],
                            waypoints=loc_points[:-1]
                         )
                    pass
        else:

            for orders,index in zip(result,range(len(result))):
                if len(orders) == 0:
                    continue
                elif len(orders) == 1:
                    path = zip(*[self.deliverers[index]['loc'],self.restaurants[orders[0]]['loc'],self.clients[orders[0]]['loc']])
                    self.gplot.plot(*path, edge_width=4, color= random.choice(colors))
                else:
                    path = []
                    path.append(self.deliverers[index]['loc'])
                    for station in orders:
                        if station[0] == 'r':
                            path.append(self.restaurants[int(station[1:])]['loc'])
                        else:
                            path.append(self.clients[int(station[1:])]['loc'])
                    path = zip(*path)
                    self.gplot.plot(*path, edge_width=4, color=random.choice(colors))

        if algorythm == "NN":
            self.gplot.draw('mapN_N.html')
        else:
            self.gplot.draw('map_brute.html')

    def brute_force(self):
        start = time.perf_counter()
        combinations = []
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
        for comb in combinations:
            i_combination = []
            cost = 0
            for orders,deliverer in zip(comb,range(self.deliverers_quantity)):
                if len(orders) == 0:
                    i_combination.append(orders)
                    continue
                elif len(orders) == 1:
                    cost += self.cost_function_DR(self.distance_DR[deliverer][orders[0]],5,
                                               self.travel_time_DR[deliverer][orders[0]],'driving')
                    cost += self.cost_function(self.distance_RC[orders[0]][orders[0]], 5,
                                               self.travel_time_RC[orders[0]][orders[0]], 'driving')
                    i_combination.append(orders)
                else:
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

                    best_perm_value = 0
                    best_perm = None
                    for perm in iter.permutations(rc_list):
                        perm_cost = 0  #koszt dla danej permutacji
                        possible_combination_flag = True
                        for c,r in zip(c_dict.keys(),r_dict.keys()):
                            if perm.index(c) < perm.index(r):
                                possible_combination_flag = False

                        if possible_combination_flag == False:
                            break
                        else:
                            perm_cost += self.cost_function_DR(self.distance_DR[deliverer][rc_dict[perm[0]]],5,
                                           self.travel_time_DR[deliverer][orders[0]],'driving')
                            perm_cost += self.income(perm)
                            for place_index in range(len(perm)-1):
                                if perm[place_index][0] == 'r' and perm[place_index+1][0] == 'c':
                                    perm_cost += self.cost_function_DR(
                                        self.distance_RC[r_dict[perm[place_index]]][c_dict[perm[place_index + 1]]],
                                        5,
                                        self.travel_time_RC[r_dict[perm[place_index]]][
                                            c_dict[perm[place_index + 1]]],
                                        'driving')
                                elif perm[place_index][0] == 'c' and perm[place_index+1][0] == 'r':
                                    perm_cost += self.cost_function_DR(self.distance_RC[r_dict[perm[place_index + 1]]][
                                                                        c_dict[perm[place_index]]],
                                                                    5,
                                                                    self.travel_time_RC[
                                                                        r_dict[perm[place_index + 1]]][
                                                                        c_dict[perm[place_index]]],
                                                                    'driving')
                                elif perm[place_index][0] == 'r' and perm[place_index+1][0] == 'r':
                                    perm_cost += self.cost_function_DR(self.distance_RR[r_dict[perm[place_index]]][r_dict[perm[place_index + 1]]],
                                                                    5,
                                                                    self.travel_time_RR[r_dict[perm[place_index]]][r_dict[perm[place_index + 1]]],
                                                                    'driving')
                                else:
                                    perm_cost += self.cost_function_DR(
                                        self.distance_CC[c_dict[perm[place_index]]][c_dict[perm[place_index + 1]]],
                                        5,
                                        self.travel_time_CC[c_dict[perm[place_index]]][
                                            c_dict[perm[place_index + 1]]],
                                        'driving')
                        if perm_cost > best_perm_value:
                            best_perm_value = perm_cost
                            best_perm = perm
                    cost+= best_perm_value
                    i_combination.append(best_perm)
            if cost > total_cost:
                total_cost = cost
                final_combination = i_combination

        end = time.perf_counter()
        exec_time = end - start

        results_dict = {
            'combination' : final_combination,
            'total_cost' : total_cost,
            'exec_time' : exec_time
        }
        return results_dict


    def NN(self):
        start = time.perf_counter()
        min_list = []
        min_index_list = []
        for deli in self.deliverers:
            min = 999999
            min_index = ()
            for restaurant in self.restaurants:
                if restaurant in [i[1] for i in min_index_list]:
                    continue
                for deliverer in self.deliverers:
                    if deliverer in [i[0] for i in min_index_list]:
                        continue
                    if self.distance_DR[deliverer][restaurant] < min:
                        if self.distance_DR[deliverer][restaurant] not in min_list:
                            min = self.distance_DR[deliverer][restaurant]
                            min_index = (deliverer,restaurant)
            if min not in min_list:
                min_list.append(min)
                min_index_list.append((min_index))
        #przydziela po jednym najblizszym zamowieniu dla kazdego dostawcy
        restaurants_left = [i for i in self.restaurants if i not in [j[1] for j in min_index_list]]

        for i in range(len(restaurants_left)):
            min = 999999
            min_index = ()
            for restaurant in restaurants_left:
                for deliverer in self.deliverers:
                    if self.distance_DR[deliverer][restaurant] < min:
                        if self.distance_DR[deliverer][restaurant] not in min_list:
                            min = self.distance_DR[deliverer][restaurant]
                            min_index = (deliverer, restaurant)
            if min_index[1] not in [i[1] for i in min_index_list]:
                min_list.append(min)
                min_index_list.append((min_index))
                restaurants_left.remove(min_index[1])
        #reszte przydziela najblizszym bez ograniczen ilosci zamowien na dostawce

        for deliverer,order in min_index_list:
            self.deliverers[deliverer]['orders'].append(order)

        comb = [self.deliverers[i]['orders'] for i in self.deliverers]

        i_combination = []
        cost = 0

        for orders, deliverer in zip(comb, range(self.deliverers_quantity)):
            if len(orders) == 0:
                i_combination.append(orders)
                continue
            elif len(orders) == 1:
                cost += self.cost_function_DR(self.distance_DR[deliverer][orders[0]], 5,
                                              self.travel_time_DR[deliverer][orders[0]], 'driving')
                cost += self.cost_function(self.distance_RC[orders[0]][orders[0]], 5,
                                           self.travel_time_RC[orders[0]][orders[0]], 'driving')
                i_combination.append(orders)
            else:
                rc_dict = {}
                rc_list = []
                r_dict = {}
                for i in orders:
                    r_dict[f'r{i}'] = i
                    rc_list.append(f'r{i}')
                c_dict = {}
                for i in orders:
                    c_dict[f'c{i}'] = i
                    rc_list.append(f'c{i}')
                rc_dict = {**c_dict, **r_dict}

                best_perm_value = 0
                best_perm = None
                for perm in iter.permutations(rc_list):
                    perm_cost = 0  # koszt dla danej permutacji
                    possible_combination_flag = True
                    for c, r in zip(c_dict.keys(), r_dict.keys()):
                        if perm.index(c) < perm.index(r):
                            possible_combination_flag = False

                    if possible_combination_flag == False:
                        break
                    else:
                        perm_cost += self.cost_function_DR(self.distance_DR[deliverer][rc_dict[perm[0]]], 5,
                                                           self.travel_time_DR[deliverer][orders[0]], 'driving')
                        perm_cost += self.income(perm)
                        for place_index in range(len(perm) - 1):
                            if perm[place_index][0] == 'r' and perm[place_index + 1][0] == 'c':
                                perm_cost += self.cost_function_DR(
                                    self.distance_RC[r_dict[perm[place_index]]][c_dict[perm[place_index + 1]]],
                                    5,
                                    self.travel_time_RC[r_dict[perm[place_index]]][
                                        c_dict[perm[place_index + 1]]],
                                    'driving')
                            elif perm[place_index][0] == 'c' and perm[place_index + 1][0] == 'r':
                                perm_cost += self.cost_function_DR(self.distance_RC[r_dict[perm[place_index + 1]]][
                                                                       c_dict[perm[place_index]]],
                                                                   5,
                                                                   self.travel_time_RC[
                                                                       r_dict[perm[place_index + 1]]][
                                                                       c_dict[perm[place_index]]],
                                                                   'driving')
                            elif perm[place_index][0] == 'r' and perm[place_index + 1][0] == 'r':
                                perm_cost += self.cost_function_DR(
                                    self.distance_RR[r_dict[perm[place_index]]][r_dict[perm[place_index + 1]]],
                                    5,
                                    self.travel_time_RR[r_dict[perm[place_index]]][r_dict[perm[place_index + 1]]],
                                    'driving')
                            else:
                                perm_cost += self.cost_function_DR(
                                    self.distance_CC[c_dict[perm[place_index]]][c_dict[perm[place_index + 1]]],
                                    5,
                                    self.travel_time_CC[c_dict[perm[place_index]]][
                                        c_dict[perm[place_index + 1]]],
                                    'driving')
                    if perm_cost > best_perm_value:
                        best_perm_value = perm_cost
                        best_perm = perm
                cost += best_perm_value
                i_combination.append(best_perm)

        end = time.perf_counter()
        exec_time = end - start
        results_dict = {
            'combination': i_combination,
            'total_cost': cost,
            'exec_time': exec_time
        }

        return results_dict




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
    print('DISTANCE DELIVERER - CLIENT')
    print(finder.distance_DC)
    print('DISTANCE RESTAURANT - CLIENT')
    print(finder.distance_RC)
    print('DISTANCE RESTAURANT - RESTAURANT')
    print(finder.distance_RR)
    print('DISTANCE CLIENT - CLIENT')
    print(finder.distance_CC)
    # print('DISTANCE MATRIX DELIVERER - RESTAURANT')
    # print(finder.distance_DR)
    # brute = finder.brute_force()
    pp.pprint(finder.brute_force())
    finder.draw_map(finder.brute_force()['combination'], 'plot', "BRUTE")
    # NN = finder.NN()
    # pp.pprint(NN)
    # finder.draw_map(NN['combination'],'plot','NN')
    # pp.pprint(finder.deliverers)
    # # finder.draw_marks()

if __name__ == '__main__':
    main()
