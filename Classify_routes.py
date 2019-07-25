# %% -*- coding: utf-8 -*-
"""
Created on Wednesday July, 3 2019
@authors: Aditeya S and Avi S
"""

import csv
import json
import os
import DataToKeplerMain as Kepler
import time


# SERFR WAYPOINTS:

SIDBY_conds_SERFR = {'track': (300, 335), 'alt': (3000, 6000), 'ground_speed': (200, 275), 'vrate': (-2000, -100),
                     'ground_distance': (0, 0.125), 'name': 'SERFR'}

EDDY3_conds_SERFR = {'track': (320, 346), 'alt': (4500, 8400), 'ground_speed':(70, 265), 'vrate':(-2176, 594),
                     'ground_distance': (0, 0.5), 'name': 'SERFR'}

EDDY2_conds_SERFR = {'track': (320, 346), 'alt': (5700, 8401), 'ground_speed': (105, 401), 'vrate': (-2053, -457),
                     'ground_distance': (0, 0.5), 'name': 'SERFR'}

NARWL_conds_SERFR = {'track':(320, 346), 'alt':(7000, 10001), 'ground_speed':(196, 387),'vrate': (-2112, -181),
                     'ground_distance': (0, 2), 'name': 'SERFR'}

obs2_conds_SERFR = {'track':(280, 353), 'alt':(8300, 12100), 'ground_speed':(200, 372),'vrate': (-2032, -400),
                    'ground_distance': (0, 5), 'name': 'SERFR'}

obs1_conds_SERFR = {'track':(338, 351), 'alt':(10000, 15215), 'ground_speed':(324, 390),'vrate': (-2700, 00),
                    'ground_distance': (0, 5), 'name': 'SERFR'}

# PIRAT2 WAYPOINTS

BRINY_conds_PIRAT2 = {'track':(45, 75), 'alt':(0, 12000), 'ground_speed':(0, 400),'vrate': (-1700, -300),
                    'ground_distance': (0, 2), 'name': 'PIRAT2'}

ARGGG_conds_PIRAT2 = {'track':(45, 75), 'alt':(5000, 9000), 'ground_speed':(0, 400),'vrate': (-2500, 0),
                    'ground_distance': (0, 0.3), 'name': 'PIRAT2'}

PIRAT_conds_PIRAT2 = {'track':(45, 75), 'alt':(10000, 13501), 'ground_speed':(0, 400),'vrate': (-1501, 0),
                    'ground_distance': (0, 1), 'name': 'PIRAT2'}

# DYAMD5 WAYPOINTS

FLOWZ_conds_DYAMD5 = {'track':(244, 262), 'alt': (10001, 15000), 'ground_speed':(0, 400),'vrate': (-2240, -1100),
                     'ground_distance': (0, 1), 'name': 'DYAMD5'}

CEDES_conds_DYAMD5 = {'track':(240, 262), 'alt': (9000, 12001), 'ground_speed':(0, 400),'vrate': (-3000, -390),
                     'ground_distance': (0,1), 'name': 'DYAMD5'}

FRELY_conds_DYAMD5 = {'track':(235, 252), 'alt': (7000, 15000), 'ground_speed':(0, 270),'vrate': (-2240, 0),
                     'ground_distance': (0, 0.4), 'name': 'DYAMD5'}

ARCHI_conds_DYAMD5 = {'track':(235, 269), 'alt': (0, 7800), 'ground_speed':(0, 400),'vrate': (-2600, 0),
                     'ground_distance': (0, 0.15), 'name': 'DYAMD5'}

#BDEGA3 WAYPOINTS

LOZIT_conds_BDEGA3 = {'track':(120, 170), 'alt': (4300, 16000), 'ground_speed':(250, 400),'vrate': (-2900, 0),
                    'ground_distance': (0, 1), 'name': 'BDEGA3'}

BDEGA_conds_BDEGA3 = {'track':(130, 170), 'alt': (6100, 14000), 'ground_speed':(0, 400),'vrate': (-2900, -1000),
                    'ground_distance': (0, 1), 'name': 'BDEGA3'}

CORKK_conds_BDEGA3 = {'track':(120, 170), 'alt': (3600, 11000), 'ground_speed':(0, 400),'vrate': (-3000, 0),
                    'ground_distance': (0, 0.35), 'name': 'BDEGA3'}

BRIXX_conds_BDEGA3 = {'track':(120, 160), 'alt': (0, 11000), 'ground_speed':(0, 400),'vrate': (-4000, -100),
                    'ground_distance': (0, 0.15), 'name': 'BDEGA3'}


SERFR = {
    "SIDBY_SFO_Approach_SE": SIDBY_conds_SERFR,
    "EDDYY(3)": EDDY3_conds_SERFR,
    "EDDYY(2)": EDDY2_conds_SERFR,
    "NARWL": NARWL_conds_SERFR,
    "OBS_2": obs2_conds_SERFR,
    "OBS_1": obs1_conds_SERFR


}

PIRAT2 = {
    "ARGGG": ARGGG_conds_PIRAT2,
    "BRINY": BRINY_conds_PIRAT2,
    "PIRAT": PIRAT_conds_PIRAT2
}

DYAMD5 = {
    "FLOWZ": FLOWZ_conds_DYAMD5, #26
    "CEDES": CEDES_conds_DYAMD5, #0
    "FRELY": FRELY_conds_DYAMD5, #7
    "ARCHI": ARCHI_conds_DYAMD5 #0
}

BDEGA3 = {
    "LOZIT": LOZIT_conds_BDEGA3,
    "BDEGA": BDEGA_conds_BDEGA3,
    "CORKK": CORKK_conds_BDEGA3,
    "BRIXX": BRIXX_conds_BDEGA3
}

routes = [
    PIRAT2,
    SERFR,
    DYAMD5,
    BDEGA3
]

ALL_ROUTE_IDS = {
    "PIRAT2": [],
    "SERFR": [],
    "DYAMD5": [],
    "BDEGA3": []

}

target_date = ''


# ------------------------------------------------------------------------------------
# This function applies the conditions that are found in each row of the input file,
# and checks them with the preset conditions listed above. The cond_set parameter is a
# dictionary (dict) type, and provides maximum and minimum values for the keys: 'track',
# 'altitude', 'vertical_rate', and 'ground_speed'. The row parameter specifies where to
# find these values in the input file that is tracked. The function returns 'True' if
# the values match, or 'other' if they do not.
# ------------------------------------------------------------------------------------
def apply_route_conditions(cond_set, row):
    track_min, track_max = cond_set['track']
    alt_min, alt_max = cond_set['alt']
    vrate_min, vrate_max = cond_set['vrate']
    ground_speed_min, ground_speed_max = cond_set['ground_speed']
    ground_distance_min, ground_distance_max = cond_set['ground_distance']
    ground_distance = row[3]
    track = row[13]
    altitude = row[10]
    vertical_rate = row[12]
    ground_speed = row[11]

    if float(int(track)) in range(track_min, track_max+1) \
            and int(altitude) in range(alt_min, alt_max+1) \
            and int(vertical_rate) in range(vrate_min, vrate_max+1) \
            and int(ground_speed) in range(ground_speed_min, ground_speed_max+1)\
            and ground_distance_min <= float(ground_distance) <= ground_distance_max:
        return cond_set['name']
    else:
        return 'other'

def origin_finder(icaoList):
    jsonFile = "./Data Sets by Date/" + target_date + "/FA_Sightings." + target_date + ".airport_ids.json.txt"
    departureFile = './Data Sets by Date/' + target_date + '/fa_airport_arr_dep.' + target_date + '.json'
    with open(jsonFile, 'r+') as f:
        input = json.load(f)
        for icao in icaoList:
            #print(input['aircraft'][icao])
            id = input['aircraft'][icao][1][0]['flight']

    with open(departureFile, 'r+') as file:
        originFile = json.load(file)
        while len(icaoList):
            fa_id = originFile['KSFO']['arrivals']['flights']
            for key in fa_id:
                if str(key).startswith(id):
                    #print(origin)
                    airport_code = fa_id[key]['origin']['code']
                    return airport_code




# ---------------------------------------------------------------------------------------
# This function adds the route name to the row in the input file. It first finds the
# ICAO address for a flight, and then adds the 'route' column to the file. If the
# 'apply_route_conditions' returned 'True', it will add the route name for which
# the 'apply_route_conditions' returned 'True' to the file under the 'route' column/key.
# ---------------------------------------------------------------------------------------
def addToJSON(icaoList, routeName):
    startTimer = time.time()
    jsonFile = "./Data Sets by Date/" + target_date + "/FA_Sightings." + target_date + ".airport_ids.json.txt"
    print("\nAdding to JSON feed " + "(" + routeName + ")...")
    with open(jsonFile, 'r+') as f:

        master_struct = json.load(f)

        master_buffer = master_struct['aircraft']

        icao_keys = list(master_buffer)
        for ic in icao_keys:
            r_set = master_buffer[ic]  # Meta/segment/sighting data for given icao

            for j_seg in range(1, len(r_set)):
                seg_data = r_set[j_seg]  # Data block for this segment
                seg_meta = seg_data[0]  # Fetch the segment hdr data
                if str(ic) in icaoList.keys() and str(seg_meta['segment']) in icaoList[str(ic)]:
                    seg_meta['route'] = routeName
                    seg_meta['origin'] = origin_finder(icaoList)
                elif 'route' not in seg_meta.keys():
                    seg_meta['route'] = 'other'
                    seg_meta['origin'] = 'other'

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
        for waypoint in eachRoute:

            cond_set = eachRoute[waypoint]

            file = "./Data Sets by Date/" + target_date + "/FA_rcas/FA_rcas." + target_date + "." + waypoint + ".rca.txt"

            with open(file) as f_in:
                reader = csv.reader(f_in, delimiter='\t', quotechar='"')

                linecount = 0
                # Transform the rest of the lines
                for line in reader:
                    if linecount == 3:
                        line += {"Route"}
                    if linecount > 3:
                        routeName = cond_set['name']
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
    target_date_input = input('Enter the target date (yymmdd): ')
    sightingReader(target_date_input)
