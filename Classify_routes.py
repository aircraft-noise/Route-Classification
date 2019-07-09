# %% -*- coding: utf-8 -*-
"""
Created on Wednesday July, 3 2019
@authors: Aditeya S and Avi S
"""

import csv
import json
import os
import DataToKeplerMain as Kepler


SIDBY_conds_SERFR = {'track': (340, 346), 'alt': (4000, 5501), 'ground_speed': (200, 275), 'vrate': (-2000, -100),
                     'ground_distance': (0, 0.125), 'name': 'SERFR'}

EDDY2_conds_SERFR = {'track': (340, 346), 'alt': (5700, 8401), 'ground_speed': (105, 401), 'vrate': (-2053, -457),
                     'ground_distance': (0, 0.125), 'name': 'SERFR'}

EDDY3_conds_SERFR = {'track': (340, 346), 'alt': (4500, 7400), 'ground_speed':(70, 265), 'vrate':(-2176, 594),
                     'ground_distance': (0, 0.125), 'name': 'SERFR'}

NARWL_conds_SERFR = {'track':(340, 346), 'alt':(7000, 10001), 'ground_speed':(196, 387),'vrate': (-2112, -181),
                     'ground_distance': (0, 0.125), 'name': 'SERFR'}

SERFR = {
    "SIDBY_SFO_Approach_SE": SIDBY_conds_SERFR,
    "EDDYY(2)": EDDY2_conds_SERFR,
    "NARWL": NARWL_conds_SERFR,
    "EDDYY(3)": EDDY3_conds_SERFR,

}

routes = [
    SERFR
]

ALL_ROUTE_IDS = {
    "SERFR": []
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

    if float(int(track)) in range(track_min, track_max) \
            and int(altitude) in range(alt_min, alt_max) \
            and int(vertical_rate) in range(vrate_min, vrate_max) \
            and int(ground_speed) in range(ground_speed_min, ground_speed_max) \
            and ground_distance_min <= float(ground_distance) <= ground_distance_max:
        return cond_set['name']
    else:
        return 'other'


# ---------------------------------------------------------------------------------------
# This function adds the route name to the row in the input file. It first finds the
# ICAO address for a flight, and then adds the 'route' column to the file. If the
# 'apply_route_conditions' returned 'True', it will add the route name for which
# the 'apply_route_conditions' returned 'True' to the file under the 'route' column/key.
# ---------------------------------------------------------------------------------------
def addToJSON(icaoList, routeName):
    jsonFile = "./Data Sets by Date/" + target_date + "/FA_Sightings." + target_date + ".airport_ids.json.txt"
    print("\nAdding to JSON feed...")
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
                elif 'route' not in seg_meta.keys():
                    seg_meta['route'] = 'other'

        f.seek(0)  # should reset file position to the beginning.
        json.dump(master_struct, f)
        f.truncate()
    print("\nJSON feed update complete")


# ---------------------------------------------------------------------------------------
# This function creates a dictionary which prints out the values to be the ICAO addresses
# which correspond to the route being classified. It also prints out the segment
# number of the flight flying on the route being classified.
# ---------------------------------------------------------------------------------------
def listMaker():
    routeicaos = {}
    for eachRoute in ALL_ROUTE_IDS:
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
        addToJSON(routeicaos, str(eachRoute))

    print("\n\nROUTE TALLY:")
    for eachRoute in ALL_ROUTE_IDS:
        print(str(eachRoute) + ": " + str(len(ALL_ROUTE_IDS[eachRoute])))


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
        print('\nALL ROUTE IDS:\n', ALL_ROUTE_IDS)
        print("\nClassification complete")
        listMaker()
    print("\nModule complete")
    print("\nMaking Kepler file")
    Kepler.runkepler()


if __name__ == "__main__":
    target_date_input = input('Enter the target date (yymmdd): ')
    sightingReader(target_date_input)
