# %% -*- coding: utf-8 -*-
"""
Created on Wednesday July, 3 2019
@authors: Aditeya S and Avi S
"""

import json
import csv
import time
import DataToKeplerMain as Kepler
import tcrlib as lib
import os
os.chdir('/Users/aditeyashukla/Documents/MONA/Route-Classification/')  # Get to proper starting dir
routes = {}
ALL_ROUTE_IDS = {}


# ------------------------------------------------------------------------------------
# This helper function groups the routes by their route names
# ------------------------------------------------------------------------------------
def group_by(select_key, list_of_dicts):
    result_dict = {}
    if callable(select_key):
        key_fn = select_key
    else:
        key_fn = lambda d: d.get(select_key)
    for this_dict in list_of_dicts:
        this_key = key_fn( this_dict )
        value_this_key = result_dict.get(this_key, list())
        value_this_key.append(this_dict)
        result_dict[this_key] = value_this_key
    return result_dict


# ------------------------------------------------------------------------------------
# This function initialises the csv file of the waypoint condition sets and makes
# data structures of the routes and their waypoints
# ------------------------------------------------------------------------------------
def condition_maker():
    global routes
    global ALL_ROUTE_IDS
    routelist = []
    with open("waypoint_data.csv", encoding='utf-8-sig') as f_in:
        reader = csv.reader(f_in, delimiter=',', quotechar='"')
        data_list = list(reader)
        for line in range(1, len(data_list)):
            dict = {}
            count = 0
            for each in data_list[line]:
                dict[data_list[0][count]] = each
                count += 1
            routelist.append(dict)
            ALL_ROUTE_IDS[str(data_list[line][0])] = []
        routes = group_by('Route Name', routelist)
        print(routes)
        print(ALL_ROUTE_IDS)


# ------------------------------------------------------------------------------------
# This function applies the conditions that are found in each row of the input file,
# and checks them with the preset conditions listed above. The cond_set parameter is a
# dictionary (dict) type, and provides maximum and minimum values for the keys: 'track',
# 'altitude', 'vertical_rate', and 'ground_speed'. The row parameter specifies where to
# find these values in the input file that is tracked. The function returns 'True' if
# the values match, or 'other' if they do not.
# ------------------------------------------------------------------------------------
def apply_route_conditions(cond_set, row):

        track_min = cond_set['track_min']
        track_max = cond_set['track_max']
        alt_min = cond_set['alt_min']
        alt_max = cond_set['alt_max']
        vrate_min = cond_set['vrate_min']
        vrate_max = cond_set['vrate_max']
        ground_speed_min = cond_set['ground_speed_min']
        ground_speed_max = cond_set['ground_speed_max']
        ground_distance_min = cond_set['ground_distance_min']
        ground_distance_max = cond_set['ground_distance_max']
        ground_distance = row[3]
        track = row[13]
        altitude = row[10]
        vertical_rate = row[12]
        ground_speed = row[11]
        # print(track_min, track_max, track)

        if int(track) in range(int(track_min), int(track_max) + 1) \
                and int(altitude) in range(int(alt_min), int(alt_max) + 1) \
                and int(vertical_rate) in range(int(vrate_min), int(vrate_max) + 1) \
                and int(ground_speed) in range(int(ground_speed_min), int(ground_speed_max) + 1) \
                and float(ground_distance_min) <= float(ground_distance) <= float(ground_distance_max):
            return cond_set['Route Name']
        else:
            return 'other'


# ------------------------------------------------------------------------------------------
# This function reads in the latitude and longitude of the origin and destination airports,
# and then computes the spherical distance between them using the tcrlib.py file.
# ------------------------------------------------------------------------------------------
def distance_calc(seg_data, org_origin, global_input, dep_input):
    destination_lat_long = 0, 0
    origin_lat_long = 0, 0
    org_destination = seg_data['destination']

    if org_destination == 'unknown':
        flight_id = seg_data['flight']
        fa_id = dep_input['KSFO']['arrivals']['flights']
        for key in fa_id:
            if str(key).startswith(flight_id):
                airport_key = fa_id[key]['destination']['code']
                print('Dest: ' + airport_key)
                org_destination = airport_key
    print('Dest: ' + org_destination)

    for line in global_input:
        if line[1] == org_destination:
            destination_lat_long = float(line[4]), float(line[5])
        if line[1] == org_origin:
            origin_lat_long = float(line[4]), float(line[5])

    print('Spherical distance between origin (' + org_origin + ') and destination (' + org_destination + '): %1.2f'
          % lib.sph_distance(origin_lat_long, destination_lat_long) + ' miles')


def aircraft_type(seg_data, dep_input):
    flight_id = seg_data['flight']
    fa_id = dep_input['KSFO']['arrivals']['flights']
    for key in fa_id:
        if str(key).startswith(flight_id):
            aircraft_type = fa_id[key]['full_aircrafttype']
            print('Aircraft type: ' + aircraft_type)
            return aircraft_type


# ------------------------------------------------------------------------------------------
# This function finds the origin of the flights using their ICAO addresses. It opens the
# the sightings file, and then finds the flight number using the ICAO address. The arrivals
# and departures file is then opened (FlightAware). The flight number found by the sightings
# file is mapped onto the arrivals and departures file in order to find the correct key that
# holds the value for the origin airport of a flight. The function then returns the airport
# code of the origin, and adds it to the JSON feed.
# ------------------------------------------------------------------------------------------
def origin_finder(icao,seg_meta,dep_input, global_input):
    flight_id = seg_meta['flight']
    fa_id = dep_input['KSFO']['arrivals']['flights']
    for key in fa_id:
        if str(key).startswith(flight_id):
            print('\nOrigin ' + '(ICAO: ' + (icao) + '): ' + fa_id[key]['origin']['code'] + ' (' + str(seg_meta['segment']) + ')')
            airport_code = fa_id[key]['origin']['code']
            print(airport_finder(global_input, airport_code))
            distance_calc(seg_meta, airport_code, global_input, dep_input)
            return airport_code


# ---------------------------------------------------------------------------------------
# This function finds the latitude and longitude for a given airport code using the global
# airport database file.
# ---------------------------------------------------------------------------------------
def airport_finder(global_input, airport_code):
    for line in global_input:
        if line[1] == airport_code:
            return line[1] + ': ' + line[4] + ', ' + line[5]


# ---------------------------------------------------------------------------------------
# This function adds the route name to the row in the input file. It first finds the
# ICAO address for a flight, and then adds the 'route' column to the file. If the
# 'apply_route_conditions' returned 'True', it will add the route name for which
# the 'apply_route_conditions' returned 'True' to the file under the 'route' column/key.
# ---------------------------------------------------------------------------------------
def addToJSON(icaoList, routeName):
    startTimer = time.time()
    jsonFile = "./Data Sets by Date/" + target_date + "/FA_Sightings." + target_date + ".airport_ids.json.txt"
    departureFile = './Data Sets by Date/' + target_date + '/Airport to-from/fa_airport_arr_dep.' + target_date + '.json'
    global_database = 'airports.csv'
    print("\nAdding to JSON feed " + "(" + routeName + ")...")
    with open(jsonFile, 'r+') as f, open(departureFile, 'r+') as a, open(global_database, 'r+') as g:

        master_struct = json.load(f)
        dep_input = json.load(a)
        global_input = list(csv.reader(g, delimiter=',', quotechar='"'))

        master_buffer = master_struct['aircraft']

        icao_keys = list(master_buffer)
        for ic in icao_keys:
            r_set = master_buffer[ic]  # Meta/segment/sighting data for given icao

            for j_seg in range(1, len(r_set)):
                seg_data = r_set[j_seg]  # Data block for this segment
                seg_meta = seg_data[0]  # Fetch the segment hdr data
                if str(ic) in icaoList.keys() and str(seg_meta['segment']) in icaoList[str(ic)]:
                    seg_meta['route'] = routeName
                    seg_meta['origin'] = origin_finder(ic, seg_meta,dep_input, global_input)
                    seg_meta['ac_type'] = aircraft_type(seg_meta, dep_input)
        f.seek(0)  # should reset file position to the beginning.
        json.dump(master_struct, f)
        f.truncate()
    endTimer = time.time()
    finalTime = endTimer - startTimer
    print("\nJSON feed update complete in %1.2f seconds" % finalTime)


def routecounter(routelist, routename):
    counter = 0
    for each in routelist:
        counter += len(routelist[each])
    print(routename, ": ",counter)


# ---------------------------------------------------------------------------------------
# This function creates a dictionary which prints out the values to be the ICAO addresses
# which correspond to the route being classified. It also prints out the segment
# number of the flight flying on the route being classified.
# ---------------------------------------------------------------------------------------
def listMaker():
    for eachRoute in ALL_ROUTE_IDS:
        routeicaos = {}
        for each in ALL_ROUTE_IDS[eachRoute]:
            icao_name = each[5:13]
            icao_segment = each[14:].strip("()")
            icao_name = icao_name.strip(" ")
            if str(icao_name) in routeicaos.keys():
                existing = routeicaos[str(icao_name)]
                id_list = existing
                id_list = set(id_list)
                id_list.add(icao_segment)
                routeicaos[str(icao_name)] = id_list
            else:
                id_list = [icao_segment]
                id_list = set(id_list)
                routeicaos[str(icao_name)] = id_list
        routecounter(routeicaos, str(eachRoute))
        print(routeicaos)
        addToJSON(routeicaos, str(eachRoute))




# ----------------------------------------------------------------------------------------
# This function opens the input file that is specified for each waypoint and target date.
# It is the main function for the classification of routes. It calls the other functions
# in order to complete the classification task that it is given.
# ----------------------------------------------------------------------------------------
def sightingReader(date):
    print("\nStarting classification...")
    global target_date
    target_date = date
    for eachRoute in routes:
        flight_ids = []
        routeName = ' '
        count = 0
        for cond_set in routes[eachRoute]:

            file = "./Data Sets by Date/" + target_date + "/FA_rcas/FA_rcas." + target_date + "." + cond_set['Waypoint'] + ".rca.txt"

            with open(file) as f_in:
                reader = csv.reader(f_in, delimiter='\t', quotechar='"')

                linecount = 0
                # Transform the rest of the lines
                for line in reader:
                    if linecount == 3:
                        line += {"Route"}
                    if linecount > 3:
                        routeName = cond_set['Route Name']
                        route = apply_route_conditions(cond_set, line)
                        line += {route}
                        if route != 'other':
                            flight_ids.append(line[0])
                    linecount += 1
            count += 1

        ALL_ROUTE_IDS[routeName] = flight_ids

    print("\nClassification complete")
    listMaker()
    print("\nModule complete")
    print("\nMaking Kepler file")
    Kepler.runkepler()


if __name__ == "__main__":
    condition_maker()
    target_date_input = input('Enter the target date (yymmdd): ')
    sightingReader(target_date_input)