import csv
import json
import os
import DataToKeplerMain as Kepler


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


# ---------------------------------------------------------------------------------------
# This function adds the route name to the row in the input file. It first finds the
# ICAO address for a flight, and then adds the 'route' column to the file. If the
# 'apply_route_conditions' returned 'True', it will add the route name for which
# the 'apply_route_conditions' returned 'True' to the file under the 'route' column/key.
# ---------------------------------------------------------------------------------------
def addToJSON(flightList, routeName):
    jsonFile = "./Data Sets by Date/" + target_date + "/FA_Sightings_new." + target_date + ".airport_ids.json.txt"
    print("\nAdding to JSON feed...")
    with open(jsonFile, 'r+') as f:

        master_struct = json.load(f)

        for each in master_struct:
            if each['flight'] in flightList:
                each['metadata']['route'] = routeName
            else:
                each['metadata']['route'] = 'other'
        f.seek(0)  # should reset file position to the beginning.
        json.dump(master_struct, f)
        f.truncate()
    print("\nJSON feed update complete")


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
    print('Making list of flights')
    for eachRoute in ALL_ROUTE_IDS:
        routeflights = []
        for each in ALL_ROUTE_IDS[eachRoute]:
            routeflights.append(each[11:])
        print("flights with routes:",str(eachRoute),routeflights)
        print("Number of flights with route",str(eachRoute),": ",len(routeflights))
        addToJSON(routeflights, str(eachRoute))


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
                            flight_ids.append(line[1])
                    linecount += 1
            count += 1

        ALL_ROUTE_IDS[routeName] = flight_ids
    print("ALL WITH FLIGHT IDS:", ALL_ROUTE_IDS)
    print("\nClassification complete")
    listMaker()
    print("\nModule complete")
    print("\nMaking Kepler file")
    Kepler.runkepler()

def reformat(input_date):
    print("Reformatting Sightings file")
    jsonFile = "./Data Sets by Date/" + input_date + "/FA_Sightings." + input_date + ".airport_ids.json.txt"
    jsonFile_new = "./Data Sets by Date/" + input_date + "/FA_Sightings_new." + input_date + ".airport_ids.json.txt"
    Flights = []
    with open(jsonFile) as f:
        data = json.load(f)

        master_buffer = data['aircraft']

        for each_icao in master_buffer:
            count = 0
            icao_metadata = {}
            for each_data in master_buffer[each_icao]:
                if count == 0:
                    icao_metadata = each_data
                else:
                    for each_segment, flight_data in zip(each_data[:-1], each_data[1:]):
                        alldata = {}
                        alldata['flight'] = each_segment['flight']
                        icao_metadata.update(each_segment)
                        alldata['metadata'] = icao_metadata
                        alldata['positions'] = flight_data
                        Flights.append(alldata)
                count += 1

    with open(jsonFile_new, 'w') as f2:  # writing JSON object
        json.dump(Flights, f2)

    print("Sightings File reformatted")


target_date_input = input('Enter the target date (yymmdd): ')
reformat(target_date_input)
sightingReader(target_date_input)