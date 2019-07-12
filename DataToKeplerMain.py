#%% -*- coding: utf-8 -*-
"""
Created on Friday June 29, 2018
@author: Luca B
"""
import json #import json library
import csv # Library to read excel files
import time as tt #time lib
import datetime as dt #datetime 
import calendar as cal
import os
os.chdir('/Users/avisingh/Desktop/MONA/Classification/') # Get to proper starting dir
import sys
import glob as ll
import tcrlib as tcr
import math as m
import string
import random

#%%
# =============================================================================
# Function to generate random ID strings
# =============================================================================
def id_generator(size=6, chars=string.ascii_lowercase + string.digits):
    return (''.join(random.choice(chars) for _ in range(size)))
# End def id_generator

#%%
# =============================================================================
# Function to get the list of sighting and track files for the target date.
# The function returns a list of lists of file names:
#   [[sighting file],[track files]]
# =============================================================================
def get_file_list(path_sight_str, path_track_str, target_date):
    # Make search strings to find the list of relevant files
    date_str = dt.datetime.fromtimestamp(target_date) \
                    .strftime('%Y%m%d')
    
    # Get a list of the main input files
    s_file_list = ll.glob(path_sight_str + '/FA*_Sightings*' + date_str[2 :] + 
                        '.airport_ids.json.txt')
    if s_file_list == []: # Quit if nothing found
        print('No sighting files found for {0}'.format(date_str))
        sys.exit()
    elif len(s_file_list) > 1:
        print('Multiple sighting files found for {0}'.format(date_str))
        sys.exit()
    # End if s_file_list == []
    
    # Now get the track file list
    t_file_list = ll.glob(path_track_str + '/Track-*.json')
    if t_file_list == []: # Quit if nothing found
        print('No track files found.')
        #sys.exit()
    # End if t_file_list == []:
    
    # Wrap things up: sort track list and return it
    t_file_list.sort()
    file_list = [] # Build return list of lists
    file_list.append(s_file_list)
    file_list.append(t_file_list)
    return(file_list)
# End def get_file_list

##############################

#%% Define paths and file name parts, first for the sighting file
pathIn = '/Users/avisingh/Desktop/MONA/Classification/Data Sets by Date'
path_trk = '/Users/avisingh/Desktop/MONA/Classification/Mapping jsons'
pathOut = '/Users/avisingh/Desktop/MONA/Classification/Data Sets by Date'
in_file_name_stem = 'FAA_FOIA_Sightings.'
# FA_Sightings.180430.airport_ids.json.txt
in_file_name_post = '.airport_ids.json.txt'
out_folder = 'Mapping/'
out_file_name_stem = '' # Empty output name for now


def runkepler():
    #%% Set up date to process
    # Check to see if the program was called with a command line input
    if len(sys.argv) == 2:
        cmd_date = sys.argv[1] # Cmd line, try to use that value
        target_tuple = tcr.get_target_date(cmd_date)
    else:
        target_tuple = tcr.get_target_date() # Get value from keyboard
    # End if len(sys.argv) == 2:

    # Check to see if we have a real date
    if target_tuple == -1: # If date failed, pack it in
        print('Invalid target date: {0}'.format(cmd_date))
        sys.exit()
    # End if target_tuple == -1:

    # Here we have a good date to be processed
    # Announce program running
    print ('Program to make kepler input point display file for {0} ' \
               .format(str(target_tuple)))

    # Now compute the bounding dates for the day in UNIX epoch format
    target_date_beg = tt.mktime(target_tuple.timetuple()) # UNIX version
    target_date_str = dt.datetime.fromtimestamp(target_date_beg). \
                        strftime('%Y%m%d')
    short_date_str = target_date_str[2 : ] # yymmdd
    target_date_end = target_date_beg + 24 * 3600 # UNIX version
    print('Date: {0}; Start: {1}, End: {2}'.format(target_date_str, \
          round(target_date_beg, 1), round(target_date_end, 1)))

    # Check on daylight savings time
    tm_dst_idx  = 8 # Index into time structure for DST flag
    gmt_epoch = cal.timegm(target_tuple.timetuple()) # Get GMT UNIX epoch
    loc_dt_struct = tt.localtime(gmt_epoch)
    # Now set offset to make kepler time histogram show local time
    if loc_dt_struct[tm_dst_idx] == 0:
        time_offset = 8 * 3600
    elif loc_dt_struct[tm_dst_idx] == 1:
        time_offset = 7 * 3600
    else:
        print('Could not determine daylight savings time state')
        sys.exit() # Bughlt
    # End if loc_dt_struct[tm_dst_idx] == 0: ...

    print('Time offset = {0} hrs'.format(str(time_offset / 3600)))

    #%% Set up some date ID strings and data set ID random strings
    data_id_len = 9 # ID string length for data sets
    layer_id_len = 6 # ID string length for layers
    adsb_flights = 'flights: ' + short_date_str # yymmdd
    adsb_sightings = 'Sightings: ' + short_date_str # yymmdd
    sighting_id = id_generator(data_id_len) # Unique ID for sighting data set
    sighting_pt_layer_id = id_generator(layer_id_len) # Unique ID for sighting layer
    sighting_line_layer_id = id_generator(layer_id_len) # Unique ID for sighting line layer
    airport_id = id_generator(data_id_len) # Unique ID for airport data set
    airport_layer_id = id_generator(layer_id_len) # Unique ID for airport layer
    waypoint_id =  id_generator(data_id_len) # Unique ID for waypoint data set
    waypoint_layer_id =  id_generator(layer_id_len) # Unique ID for waypoint layer
    other_id =  id_generator(data_id_len) # Unique ID for other data set
    other_layer_id =  id_generator(layer_id_len) # Unique ID for other layer
    track_id =  id_generator(data_id_len) # Unique ID for track data set
    track_layer_id =  id_generator(layer_id_len) # Unique ID for track layer
    dnl_id = id_generator(data_id_len) # Unique ID for dnl data set
    dnl_pt_layer_id = id_generator(layer_id_len) # Unique ID for dnl point layer
    dnl_hex_layer_id = id_generator(layer_id_len) # Unique ID for dnl column layer
    dnl_heat_layer_id = id_generator(layer_id_len) # Unique ID for dnl heat layer
    count_id =  id_generator(data_id_len) # Unique ID for count data set
    count_pt_layer_id =  id_generator(layer_id_len) # Unique ID for count layer
    count_hex_layer_id = id_generator(layer_id_len) # Unique ID for count col layer
    count_heat_layer_id = id_generator(layer_id_len) # Unique ID for cnt heat layer
    lmax_id = id_generator(data_id_len) # Unique ID for lmax data set
    lmax_pt_layer_id = id_generator(layer_id_len) # Unique ID for lmax point layer
    lmax_hex_layer_id = id_generator(layer_id_len) # Unique ID for lmax col layer
    lmax_heat_layer_id = id_generator(layer_id_len) # Unique ID for lmax heat layer
    agl_id = id_generator(data_id_len) # Unique ID for agl data set
    agl_pt_layer_id = id_generator(layer_id_len) # Unique ID for agl point layer
    agl_hex_layer_id = id_generator(layer_id_len) # Unique ID for agl column layer
    agl_heat_layer_id = id_generator(layer_id_len) # Unique ID for agl heat layer
    time_filter_id = id_generator(data_id_len) # Unique ID for time filter config


    #%% Set up the full names of sighting files from FAA history data for the
    # target date and the mapping matrix node analysis file
    filez = filez_h = filez_sight = [] #Default empty sighting file sets

    path_in = os.path.join(pathIn, short_date_str).replace('\\', '/')
    filez_all = get_file_list(path_in, path_trk, target_date_beg)
    filez_sight = filez_all[0] # Sighting data should be in the 1st sublist
    if len(filez_sight) != 1:
        print('Error: {0} Sighting files\n  {1}' \
            .format(str(len(filez_sight)), filez))
    # End if len(filez_sight) != 1:

    filez_track = filez_all[1] # Track data should be in the 2nd sublist
    # Now for the mapping matrix node analysis file
    #file_p = 'C:/Users/TCR/Dropbox/FlightAware/Data Sets by Date/' + \
    #            short_date_str + '/Mapping/FA.rca-map.3mi.matrix_nodes.' \
    #            '50-mi-circle-hex-packed.1320-ft.ALL_AIRPORTS.' + \
    #            short_date_str + '.txt'
    #file_p = 'C:/Users/TCR/Dropbox/FlightAware/Data Sets by Date/' + \
    #            short_date_str + '/Mapping/FA.rca-map.5mi.matrix_nodes.' \
    #            '50-mi-circle-hex-packed.1320-ft.ALL_AIRPORTS.' + \
    #            short_date_str + '.txt'
    file_p = 'C:/Users/TCR/Dropbox/FlightAware/Data Sets by Date/' + \
                short_date_str + '/Mapping/FA.rca-map.5mi.matrix_nodes.' \
                '50-mi-circle-hex-packed.2640-ft.ALL_AIRPORTS.' + \
                short_date_str + '.txt'
    #file_p = 'C:/Users/TCR/Dropbox/FlightAware/Data Sets by Date/' + \
    #            short_date_str + '/Mapping/FA.rca-map.5mi.matrix_nodes.' \
    #            '50-mi-circle-hex-packed.2640-ft.KSFO_KSJC.' + \
    #            short_date_str + '.txt'
    #print(file_p) # Debug
    # Split out the airport designator to qualify the output file name
    ft_idx = file_p.rindex('-ft.')
    airport_str = file_p[ft_idx + 4 : file_p.rindex('.' + short_date_str + '.txt')]
    #FA.rca-map.3mi.matrix_nodes.50-mi-circle-hex-packed.5280-ft.ALL_AIRPORTS.\
    #150114
    # String showing how densely packed the hex nodes are
    hex_pack_dist = file_p[ft_idx - 4 : ft_idx + 3]


    #%% Loads sighting json file
    file_in = filez_sight[0].replace('\\', '/') #define input file name

    with open (file_in) as json_file:
            flightData = json.load(json_file)
            flights = flightData["aircraft"] #Assigns aircraft key to flights
    # Pick up starting and ending times of data recording.
            startUnix = flightData["tmin"]
            endUnix = flightData["tmax"]
            startTime = dt.datetime.fromtimestamp(startUnix) \
                .strftime('%d-%m-%Y %H:%M:%S')
            endTime = dt.datetime.fromtimestamp(endUnix) \
                .strftime('%d-%m-%Y %H:%M:%S')
    #        print(startTime) #not yet sure what time zone this is in.
    #        print(endTime)

            json_file.close() # Make sure the input file is closed
    # End with open (file_in) as json_file:

    #%% Loads track json files
    # Each track file has a structure as follows:
    #   [[node ID1, lat1, lon1, elev1], [node ID2, lat2, lon2, elev2], ...]
    track_data = {} # Dict structure to hold successive track node data
    # Markers to isolate track ID string
    l_mrk = 'Track-'
    r_mrk = '.json'

    # Now loop through the various track files
    for i_file in filez_track:
        file_trk = i_file.replace('\\', '/') #define input file name
        trk_id = file_trk[file_trk.index(l_mrk) + len(l_mrk) : \
                          file_trk.index(r_mrk)]
        with open (file_trk) as json_file:
                track_tmp = json.load(json_file)
                track_data[trk_id] = track_tmp # Add this track segment nodes
                json_file.close() # Make sure the input file is closed
        # End with open (file_in) as json_file:
    # End for i_file in filez_track:

    trk_keys = list(track_data) # Save a list of track segment keys

    #%% Read in DNL, flight concentration, lmax, and altitude file
    matrixData = []
    try:
        with open(file_p) as tsvFile:
            next(tsvFile) #skip headers
            next(tsvFile)
            fileReader = csv.DictReader(tsvFile, delimiter='\t')
            for row in fileReader:
                matrixData.append(dict(row))
            # End for row in fileReader:

            tsvFile.close() # Make sure input file is closed
        dnl_file_ok = True # Note that metric file found and loaded
        # End with open(file_p) as tsvFile:
    except:
        dnl_file_ok = False # No metric file found
    # End try... except:

    min_dnl = 50.0 # Minimum DNL value to include in overlay
    #max_dnl = 70.0 # Maximum dnl value to control color scaling
    max_dnl = 66.0 # Maximum dnl value to control color scaling
    #min_count = 1.05 # Minimum overflight count value (#/hr) to include in overlay
    min_count = 2.05 # Minimum overflight count value (#/hr) to include in overlay
    max_count = 8 # Maximum count value to control color scaling
    #min_lmax_cnt = 1.1 # Minimum lamx count value (#/hr) to include in overlay
    min_lmax_cnt = 2.05 # Minimum lamx count value (#/hr) to include in overlay
    max_lmax_cnt = 8.0 # Maximum lamx count value (#/hr) to include in overlay
    min_agl_count = 4.0 # Minimum overflight count value (#/hr) to include in overlay
    #min_agl_count = 3.0 # Minimum overflight count value (#/hr) to include in overlay
    min_ave_agl = 50.0 # Minimum average agl value to include in overlay
    max_ave_agl = 7000.0 # Maximum average agl value to include in overlay
    max_altitude = 14000 # Maximum altitude value to control color scaling

    #for matrix_node in matrixData:
    #    dnl_value = float(matrix_node['DNL 24 hr'])
    #    if dnl_value >= min_dnl:
    #        lat.append(float(matrix_node['Latitude']))
    #        lon.append(float(matrix_node['Longitude']))
    #        level.append(dnl_value)
    #    # End if dnl_value >= min_dnl
    ## End for matrix in matrixData:

    #%% This is a permanent list of landmarks; airports, waypoints and other
    landmarks = {'airports': [
                    {'code': 'KHWD',
                    'name': 'Hayward Executive',
                    'latitude': 37.6589285,
                    'longitude': -122.1217372,
                    'elevation': 52.1},
                    {'code': 'KNUQ',
                    'name': 'Moffett Federal Afld',
                    'latitude': 37.4161422,
                    'longitude': -122.0491311,
                    'elevation': 36.6},
                    {'code': 'KOAK',
                    'name': 'Metropolitan Oakland Intl',
                    'latitude': 37.72125,
                    'longitude': -122.2211389,
                    'elevation': 9.0},
                    {'code': 'KPAO',
                    'name': 'Palo Alto',
                    'latitude': 37.4611111,
                    'longitude': -122.1150556,
                    'elevation': 6.8},
                    {'code': 'KRHV',
                    'name': 'Santa Clara County',
                    'latitude': 37.3328611,
                    'longitude': -121.8198056,
                    'elevation': 135.4},
                    {'code': 'KSFO',
                    'name': 'San Francisco Intl',
                    'latitude': 37.6188056,
                    'longitude': -122.3754167,
                    'elevation': 13.1},
                    {'code': 'KSJC',
                    'name': 'San Jose Intl',
                    'latitude': 37.3629947,
                    'longitude': -121.9286206,
                    'elevation': 62.2},
                    {'code': 'KSQL',
                    'name': 'San Carlos',
                    'latitude': 37.5118611,
                    'longitude': -122.2495311,
                    'elevation': 5.5},
                    {'code': 'SUMED',
                    'name': 'SU Emergency Dept',
                    'latitude': 37.433875,
                    'longitude': -122.174511,
                    'elevation': 95.0},
                    {'code': 'VMCED',
                    'name': 'VMC Emergency Dept',
                    'latitude': 37.313718,
                    'longitude': -121.934491,
                    'elevation': 150.0},
                    {'code': 'KLVK',
                    'name': 'Livermore Municipal Airport',
                    'latitude': 37.6934,
                    'longitude': -121.8204,
                    'elevation': 400.0},
                    {'code': 'KHAF',
                    'name': 'Half Moon Bay Airport',
                    'latitude': 37.507997968,
                    'longitude': -122.500664664,
                    'elevation': 66.0}
                    ],

                'waypoints': [{
                    'code': 'AMEBY',
                    'name': 'AMEBY',
                    'latitude': 37.371828,
                    'longitude': -122.058100},
                    {'code': 'ARCHI',
                    'name': 'ARCHI ',
                    'latitude': 37.490806,
                    'longitude': -121.875556},
                    {'code': 'BRIXX',
                    'name': 'BRIXX ',
                    'latitude': 37.617844,
                    'longitude': -122.374528},
                    {'code': 'DUMBA',
                    'name': 'DUMBA',
                    'latitude': 37.503517,
                    'longitude': -122.096147},
                    {'code': 'EDDYY(2)',
                    'name': 'EDDYY(2)',
                    'latitude': 37.326444,
                    'longitude': -122.099722},
                    {'code': 'EDDYY(3)',
                    'name': 'EDDYY(3)',
                    'latitude': 37.374903,
                    'longitude': -122.119028},
                    {'code': 'FAITH',
                    'name': 'FAITH',
                    'latitude': 37.401217,
                    'longitude': -121.861900},
                    {'code': 'MENLO',
                    'name': 'MENLO ',
                    'latitude': 37.463694,
                    'longitude': -122.153667},
                    {'code': 'NARWL',
                    'name': 'NARWL',
                    'latitude': 37.274781,
                    'longitude': -122.079306},
                    {'code': 'SIDBY',
                    'name': 'SIDBY',
                    'latitude': 37.450711,
                    'longitude': -122.144747},
                    {'code': 'PIRAT',
                    'name': 'PIRAT',
                    'latitude': 37.257650,
                    'longitude': -122.863353},
                    {'code': 'CYMBL',
                    'name': 'CYMBL',
                    'latitude': 37.570881,
                    'longitude': -121.843631},
                    {'code': 'BRINY',
                    'name': 'BRINY',
                    'latitude': 37.304761,
                    'longitude': -122.661656},
                    {'code': 'ARGGG',
                    'name': 'ARGGG',
                    'latitude': 37.392422,
                    'longitude': -122.281631},
                    {'code': 'TRDOW',
                    'name': 'TRDOW',
                    'latitude': 37.493828,
                    'longitude': -121.985542},
                    {'code': 'ZORSA',
                    'name': 'ZORSA',
                    'latitude': 37.362961,
                    'longitude': -122.050661},
                    {'code': 'JESEN',
                    'name': 'JESEN',
                    'latitude': 37.294831,
                    'longitude': -121.975569}
                    ],
                'other': [{
                    'code': 'MJF',
                    'name': 'MJF',
                    'latitude': 37.442290,
                    'longitude': -122.140079},
                    {
                    'code': 'PFC',
                    'name': 'PFC',
                    'latitude': 37.472727,
                    'longitude': -122.17878},
                    {
                    'code': 'LAC',
                    'name': 'LAC',
                    'latitude': 37.436000,
                    'longitude': -122.128175},
                    {
                    'code': 'DG',
                    'name': 'DG',
                    'latitude': 37.402188,
                    'longitude': -122.118712},
                    {
                    'code': 'PFC',
                    'name': 'PFC',
                    'latitude': 37.472727,
                    'longitude': -122.17878},
                    {
                    'code': 'RH',
                    'name': 'RH',
                    'latitude': 37.390414,
                    'longitude': -122.078779},
                    {
                    'code': 'JJA',
                    'name': 'JJA',
                    'latitude': 37.413767,
                    'longitude': -122.161117},
                    {
                    'code': 'DP',
                    'name': 'DP',
                    'latitude': 37.462082,
                    'longitude': -122.128619},
                    {
                    'code': 'TCR',
                    'name': 'TCR',
                    'latitude': 37.450204,
                    'longitude': -122.143786},
                    {
                    'code': 'DCJ',
                    'name': 'DCJ',
                    'latitude': 37.444713,
                    'longitude': -122.155651},
                    {
                    'code': 'MXS',
                    'name': 'MXS',
                    'latitude': 37.437117,
                    'longitude': -122.139898}
                    ]}

    #%% Sets up keplergl dictionary: will later be converted to json
    #config dictionary contains default configuration data for kepler.gl
    currentTime = str(dt.datetime.now()) #used to timestamp the exported json
    keplergl =  {}                      #define kepler
    keplergl['datasets'] = []           #define dataset array
    dset_ordinal = 0 # Init ordinal ID for successive data sets

    #%% Here we make a dataset for sighting information
    sighting_ord = dset_ordinal # Remember the ordinal ID for sighting
    dset_ordinal += 1 # Bump to next value
    keplergl['datasets'].append({
                    "version" : "v1",
                    "data":
                        {
                        "id": sighting_id,
                        "label": adsb_flights, #name on kepler gui
                         "color" : [143, 47, 91],  #random rgb
                         #kepler's main data store, left blank here for setup.
                         "allData" : [],
                         #fields for "column" names: data array must correspond
                         #to this order.
                         "fields": [
                        {
                              "name": "icao",
                              "type": "string"
                        },
                        {
                              "name": "flight",
                              "type": "string"
                        },
                        {
                              "name": "aircraft type",
                              "type": "string"
                        },
                        {
                              "name": "route",
                              "type": "string"
                        },
                        {
                              "name": "latitude",
                              "type": "real"
                        },
                        {
                              "name": "longitude",
                              "type": "real"
                        },
                        {
                              "name": "altitude",
                              "type": "int"
                        },
                        {
                              "name": "segment",
                              "type": "int"
                        },
                        {
                              "name": "time",
                              "type": "time"
                        },
                        {
                              "name": "clock",
                              "type": "string"
                        },
                        {
                              "name": "arrive",
                              "type": "string"
                        },
                        {
                              "name": "depart",
                              "type": "string"
                        },
                        {
                              "name": "nxtlat",
                              "type": "real"
                        },
                        {
                              "name": "nxtlon",
                              "type": "real"
                        }
                    ]
                 }
            })

    #%% Here we make a dataset for airport data
    airport_ord = dset_ordinal # Remember the ordinal ID for airports
    dset_ordinal += 1 # Bump to next value
    keplergl['datasets'].append({  #append Airport data with blank data/field info
                    "version" : "v1",
                    "data": # Airport data
                        {
                        "id": airport_id,
                        "label": "airports", #name on kepler gui
                         "color" : [143, 47, 91],  #random rgb
                         #kepler's main data store, left blank here for setup.
                         "allData" : [],
                         #fields for "column" names: data array must correspond
                         #to this order.
                         "fields": [
                        {
                              "name": "code",
                              "type": "string"
                        },
                        {
                              "name": "name",
                              "type": "string"
                        },
                        {
                              "name": "latitude",
                              "type": "real"
                        },
                        {
                              "name": "longitude",
                              "type": "real"
                        }
                    ]
                 }
                })

    #%% Now add place for Waypoint data
    waypoint_ord = dset_ordinal # Remember the ordinal ID for waypoints
    dset_ordinal += 1 # Bump to next value
    keplergl['datasets'].append({
                    "version" : "v1",
                    "data":
                        {
                        "id": waypoint_id,
                        "label": "waypoints", #name on kepler gui
                         "color" : [143, 47, 91],  #random rgb
                         #kepler's main data store, left blank here for setup.
                         "allData" : [],
                         #fields for "column" names: data array must correspond
                         #to this order.
                         "fields": [
                        {
                              "name": "code",
                              "type": "string"
                        },
                        {
                              "name": "name",
                              "type": "string"
                        },
                        {
                              "name": "latitude",
                              "type": "real"
                        },
                        {
                              "name": "longitude",
                              "type": "real"
                        }
                    ]
                 }
            })

    #%% Add place for Other data
    other_ord = dset_ordinal # Remember the ordinal ID for others
    dset_ordinal += 1 # Bump to next value
    keplergl['datasets'].append({
                    "version" : "v1",
                    "data":
                        {
                        "id": other_id,
                        "label": "other", #name on kepler gui
                         "color" : [143, 47, 91],  #random rgb
                         #kepler's main data store, left blank here for setup.
                         "allData" : [],
                         #fields for "column" names: data array must correspond
                         #to this order.
                         "fields": [
                        {
                              "name": "code",
                              "type": "string"
                        },
                        {
                              "name": "name",
                              "type": "string"
                        },
                        {
                              "name": "latitude",
                              "type": "real"
                        },
                        {
                              "name": "longitude",
                              "type": "real"
                        }
                    ]
                 }
            })

    #%% Add place for Track data
    track_ord = dset_ordinal # Remember the ordinal ID for tracks
    dset_ordinal += 1 # Bump to next value
    keplergl['datasets'].append({
                    "version" : "v1",
                    "data":
                        {
                        "id": track_id,
                        "label": "track", #name on kepler gui
                         "color" : [143, 47, 91],  #random rgb
                         #kepler's main data store, left blank here for setup.
                         "allData" : [],
                         #fields for "column" names: data array must correspond
                         #to this order.
                         "fields": [
                        {
                              "name": "code",
                              "type": "string"
                        },
                        {
                              "name": "name",
                              "type": "string"
                        },
                        {
                              "name": "latitude",
                              "type": "real"
                        },
                        {
                              "name": "longitude",
                              "type": "real"
                        },
                        {
                              "name": "elevation",
                              "type": "integer"
                        }
                    ]
                 }
            })

    #%% Now add place for DNL data
    dnl_ord = dset_ordinal # Remember the ordinal ID for DNL values
    dset_ordinal += 1 # Bump to next value
    keplergl['datasets'].append({
                    "version" : "v1",
                    "data":
                        {
                        "id": dnl_id,
                        "label": "DNL", #name on kepler gui
                         "color" : [143, 47, 91],  #random rgb
                         #kepler's main data store, left blank here for setup.
                         "allData" : [],
                         #fields for "column" names: data array must correspond
                         #to this order.
                         "fields": [
                        {
                              "name": "latitude",
                              "type": "real"
                        },
                        {
                              "name": "longitude",
                              "type": "real"
                        },
                        {
                              "name": "24hr",
                              "type": "real"
                        },
                        {
                              "name": "18hr",
                              "type": "real"
                        },
                        {
                              "name": "maximum",
                              "type": "real"
                        },
                        {
                              "name": "00-06",
                              "type": "real"
                        },
                        {
                              "name": "06-12",
                              "type": "real"
                        },
                        {
                              "name": "12-18",
                              "type": "real"
                        },
                        {
                              "name": "18-24",
                              "type": "real"
                        },
                        {
                              "name": "scale_dnl",
                              "type": "real"
                        }
                    ]
                 }
            })

    #%% Now add place for overflight concentration data
    count_ord = dset_ordinal # Remember the ordinal ID for counts
    dset_ordinal += 1 # Bump to next value
    keplergl['datasets'].append({
                    "version" : "v1",
                    "data":
                        {
                        "id": count_id,
                        "label": "counts/hr", #name on kepler gui
                         "color" : [143, 47, 91],  #random rgb
                         #kepler's main data store, left blank here for setup.
                         "allData" : [],
                         #fields for "column" names: data array must correspond
                         #to this order.
                         "fields": [
                        {
                              "name": "latitude",
                              "type": "real"
                        },
                        {
                              "name": "longitude",
                              "type": "real"
                        },
                        {
                              "name": "24hr",
                              "type": "real"
                        },
                        {
                              "name": "18hr",
                              "type": "real"
                        },
                        {
                              "name": "maximum",
                              "type": "real"
                        },
                        {
                              "name": "00-06",
                              "type": "real"
                        },
                        {
                              "name": "06-12",
                              "type": "real"
                        },
                        {
                              "name": "12-18",
                              "type": "real"
                        },
                        {
                              "name": "18-24",
                              "type": "real"
                        },
                        {
                              "name": "scale_count",
                              "type": "real"
                        }
                    ]
                 }
            })

    #%% Now add place for overflight lmax data
    lmax_ord = dset_ordinal # Remember the ordinal ID for lmax data
    dset_ordinal += 1 # Bump to next value
    keplergl['datasets'].append({
                    "version" : "v1",
                    "data":
                        {
                        "id": lmax_id,
                        "label": "lmax >60dB/hr", #name on kepler gui
                         "color" : [143, 47, 91],  #random rgb
                         #kepler's main data store, left blank here for setup.
                         "allData" : [],
                         #fields for "column" names: data array must correspond
                         #to this order.
                         "fields": [
                        {
                              "name": "latitude",
                              "type": "real"
                        },
                        {
                              "name": "longitude",
                              "type": "real"
                        },
                        {
                              "name": "24hr",
                              "type": "real"
                        },
                        {
                              "name": "18hr",
                              "type": "real"
                        },
                        {
                              "name": "maximum",
                              "type": "real"
                        },
                        {
                              "name": "00-06",
                              "type": "real"
                        },
                        {
                              "name": "06-12",
                              "type": "real"
                        },
                        {
                              "name": "12-18",
                              "type": "real"
                        },
                        {
                              "name": "18-24",
                              "type": "real"
                        },
                        {
                              "name": "scale_lmax",
                              "type": "real"
                        }
                    ]
                 }
            })

    #%% Now add place for overflight agl data
    agl_ord = dset_ordinal # Remember the ordinal ID for agl data
    dset_ordinal += 1 # Bump to next value
    keplergl['datasets'].append({
                    "version" : "v1",
                    "data":
                        {
                        "id": agl_id,
                        "label": "agl", #name on kepler gui
                         "color" : [143, 47, 91],  #random rgb
                         #kepler's main data store, left blank here for setup.
                         "allData" : [],
                         #fields for "column" names: data array must correspond
                         #to this order.
                         "fields": [
                        {
                              "name": "latitude",
                              "type": "real"
                        },
                        {
                              "name": "longitude",
                              "type": "real"
                        },
                        {
                              "name": "Ave AGL",
                              "type": "real"
                        },
                        {
                              "name": "Std Dev AGL",
                              "type": "real"
                        },
                        {
                              "name": "scale_agl",
                              "type": "real"
                        }
                    ]
                 }
            })

    #%% basic kepler config settings below
    # Luca original color scheme
    #                  "colors": [
    #                    "#FFFFFF", #white
    #                    "#8cff00", #light green
    #                    "#00ff6a", #bright green
    #                    "#00ffd8", #sea green
    #                    "#ff00ff", #red purple
    #                    "#ff007b", #blue red
    #                    "#ff0000" #red

    keplergl['config'] = {
        "version": "v1",
        "config": {
          "visState": {
            "filters": [{
                "dataId": sighting_id,
                "id": time_filter_id,
                "name": "time",
                "type": "timeRange",
                "value": [
                  (startUnix), # * 1000
                  (endUnix) #kepler apparently uses millis
                ],
                "enlarged": True,
                "plotType": "histogram",
                "yAxis": None
                }],
    #%% The next sections add layers for airports, waypoints, tracks,
    # DNL distribution, overflight count distribution, and sightings
            "layers": [

    # First add a layer for airports (on top)
              {
                "id": airport_layer_id,
                "type": "point",
                "config": {
                  "dataId": airport_id,
                  "label": "Airports",
                  "color": [
    #                119,
    #                110,
    #                87
                      246,
                      209,
                      138,
                      255
                  ],
                  "columns": {
                    "lat": "latitude",
                    "lng": "longitude"
                  },
                  "isVisible": True,
                  "visConfig": {
                    "radius": 25.0,
                    "fixedRadius": False,
                    "opacity": 0.8,
                    "outline": False,
                    "thickness": 2,
                    "colorRange": {
                      "name": "Custom",
                      "type": "Custom",
                      "category": "Custom",
                      "colors": [
                        "#ffffff" #White
    #                    "#fefddc" #Yellowish white
                      ]
                    },
                    "radiusRange": [
                      0,
                      50
                    ],
                    "hi-precision": False
                  }
                },
                "visualChannels": {
                  "colorField": {
                    "name": "code",
                    "type": "string"
                  },
                  "colorScale": "quantize",
                  "sizeField": None,
                  "sizeScale": "linear"
                }
              },
    #%% Then add waypoint layer (next to top)
              { "id": waypoint_layer_id,
                "type": "point",
                "config": {
                  "dataId": waypoint_id,
                  "label": "Waypoints",
                  "color": [
    #                119,
    #                110,
    #                87
                      246,
                      209,
                      138,
                      255
                  ],
                  "columns": {
                    "lat": "latitude",
                    "lng": "longitude"
                  },
                  "isVisible": True,
                  "visConfig": {
                    "radius": 25.0,
                    "fixedRadius": False,
                    "opacity": 0.8,
                    "outline": False,
                    "thickness": 2,
                    "colorRange": {
                      "name": "Custom",
                      "type": "Custom",
                      "category": "Custom",
                      "colors": [
                        "#d6fda8" # Lt avocado
    #                    "#fa69f8" # Bright violet
    #                    "#42ff00" # Bright green
                      ]
                    },
                    "radiusRange": [
                      0,
                      50
                    ],
                    "hi-precision": False
                  }
                },
                "visualChannels": {
                  "colorField": {
                    "name": "code",
                    "type": "string"
                  },
                  "colorScale": "quantize",
                  "sizeField": None,
                  "sizeScale": "linear"
                }
              },
    #%% Then add "other" layer -- locations of involved people
              { "id": other_layer_id,
                "type": "point",
                "config": {
                  "dataId": other_id,
                  "label": "Others",
                  "color": [
                      246,
                      209,
                      138,
                      255
                  ],
                  "columns": {
                    "lat": "latitude",
                    "lng": "longitude"
                  },
                  "isVisible": False,
                  "visConfig": {
                    "radius": 25.0,
                    "fixedRadius": False,
                    "opacity": 0.8,
                    "outline": False,
                    "thickness": 2,
                    "colorRange": {
                      "name": "Custom",
                      "type": "Custom",
                      "category": "Custom",
                      "colors": [
                        "#ff0000" # Bright red
                      ]
                    },
                    "radiusRange": [
                      0,
                      50
                    ],
                    "hi-precision": False
                  }
                },
                "visualChannels": {
                  "colorField": {
                    "name": "code",
                    "type": "string"
                  },
                  "colorScale": "quantize",
                  "sizeField": None,
                  "sizeScale": "linear"
                }
              },
    #%% Then add track layer (next to top)
              { "id": track_layer_id,
                "type": "point",
                "config": {
                  "dataId": track_id,
                  "label": "Tracks",
                  "color": [
                      246,
                      209,
                      138,
                      255
                  ],
                  "columns": {
                    "lat": "latitude",
                    "lng": "longitude"
                  },
                  "isVisible": False,
                  "visConfig": {
                     "radius": 10.0,
                    "fixedRadius": False,
                    "opacity": 0.8,
                    "outline": False,
                    "thickness": 2,
                    "colorRange": {
                      "name": "Custom",
                      "type": "Custom",
                      "category": "Custom",
                      "colors": [
                        "#ffffff" # White
    #                    "#a8bffc", #lt blue
    #                    "#4276fc", #dark blue
    #                    "#5aff9e", #lt green
    #                    "#01cc55", #dark green
    #                    "#fbf825", #yellow
    #                    "#fda40a", #orange
    #                    "#f11f7d" #red
    #                    "#ff00ff" #red purple
                      ]
                    },
                    "radiusRange": [
                      0,
                      50
                    ],
                    "hi-precision": False
                  }
                },
                "visualChannels": {
                  "colorField": {
                    "name": "elevation",
                    "type": "integer"
                  },
                  "colorScale": "quantize",
                  "sizeField": None,
                  "sizeScale": "linear"
                }
              },
    #%% Add the DNL point layer
              {
                "id": dnl_pt_layer_id,
                "type": "point",
                "config": {
                  "dataId": dnl_id,
                  "label": "DNL",
                  "color": [
                      246,
                      209,
                      138,
                      255
                  ],
                  "columns": {
                    "lat": "latitude",
                    "lng": "longitude"
    #                "altitude": "count 24hr"
                  },
                  "isVisible": False,
                  "visConfig": {
                    "radius": 20.0,
                    "fixedRadius": False,
                    "opacity": 0.40,
                    "outline": False,
                    "thickness": 1,
                    "colorRange": {
                      "name": "Custom",
                      "type": "Custom",
                      "category": "Custom",
                      "colors": [
                        "#a8bffc", #lt blue
                        "#4276fc", #dark blue
                        "#5aff9e", #lt green
                        "#01cc55", #dark green
                        "#fbf825", #yellow
                        "#fda40a", #orange
                        "#f11f7d", #red
                        "#ff00ff" #red purple
                      ]
                    },
                    "radiusRange": [
                      0,
                      50
                    ],
                    "hi-precision": False
                  }
                },
                "visualChannels": {
                  "colorField": {
                    "name": "scale_dnl",
                    "type": "real"
                  },
                  "colorScale": "quantize",
                  "sizeField": None,
                  "sizeScale": "linear"
                }
              },
    #%% Next add the DNL Column layer
              {
                "id": dnl_hex_layer_id,
                "type": "hexagon",
                "config": {
                  "dataId": dnl_id,
                  "label": "DNL Column",
                  "color": [
                      246,
                      209,
                      138,
                      255
                  ],
                  "columns": {
                    "lat": "latitude",
                    "lng": "longitude",
                    "altitude": "scale_dnl"
                  },
                  "isVisible": False,
                  "visConfig": {
    #                "radius": 24.0,
    #                "fixedRadius": False,
                    "opacity": 0.16,
    #                "outline": False,
    #                "thickness": 2,
                    "worldUnitSize": 1.0,
    #                "resolution": 8,
                    "resolution": 15,
                    "colorRange": {
                      "name": "Custom",
                      "type": "Custom",
                      "category": "Custom",
                      "colors": [
                        "#a8bffc", #lt blue
                        "#4276fc", #dark blue
                        "#5aff9e", #lt green
                        "#01cc55", #dark green
                        "#fbf825", #yellow
                        "#fda40a", #orange
                        "#f11f7d", #red
                        "#ff00ff" #red purple
                      ]
                    },
    #                "radiusRange": [
    #                  0,
    #                  50
    #                ],
                    "coverage": 0.6,
                    "sizeRange": [
                        0,
                        100
                      ],
                     "percentile": [
                        0,
                        100
                        ],
                    "elevationPercentile": [
                        0,
                        100
                      ],
                    "elevationScale": 25.0,
                    "hi-precision": False,
                    "colorAggregation": "maximum",
    #                "sizeAggregation": "maximum",
                    "enable3d": False
                  },
                  "textLabel": {
                    "field": '',
                    "color": [
                      255,
                      255,
                      255
                      ],
                        "size": 50,
                        "offset": [
                            0,
                            0
                        ],
                        "anchor": "middle"
                    }
                },
                "visualChannels": {
                  "colorField": {
                    "name": "scale_dnl",
                    "type": "real"
                  },
                "colorScale": "quantize",
                  "sizeField": {
                    "name": "scale_dnl",
                    "type": "real"
                },
                "sizeScale": "linear"
                }
              },
    #%% Next add the DNL Heat layer
              {
                "id": dnl_heat_layer_id,
                "type": "heatmap",
                "config": {
                  "dataId": dnl_id,
                  "label": "DNL Heat",
                  "color": [
                      246,
                      209,
                      138,
                      255
                  ],
                  "columns": {
                    "lat": "latitude",
                    "lng": "longitude",
    #                "altitude": "dnl 18hr"
                  },
                  "isVisible": False,
                  "visConfig": {
                    "opacity": 0.5,
                    "colorRange": {
                      "name": "Custom",
                      "type": "Custom",
                      "category": "Custom",
                      "colors": [
                        "#a8bffc", #lt blue
                        "#4276fc", #dark blue
                        "#5aff9e", #lt green
                        "#01cc55", #dark green
                        "#fbf825", #yellow
                        "#fda40a", #orange
                        "#f11f7d", #red
                        "#ff00ff" #red purple
                      ]
                    },
                    "radius": 28.0
                  },
                  "textLabel": {
                    "field": '',
                    "color": [
                      255,
                      255,
                      255
                      ],
                        "size": 50,
                        "offset": [
                            0,
                            0
                        ],
                        "anchor": "middle"
                    }
                },
                "visualChannels": {
    #              "colorField": {
                  "weightField": {
                    "name": "scale_dnl",
                    "type": "real"
                  },
    #              "colorScale": "quantize",
    #              "sizeField": {
    #                "name": "scale_dnl",
    #                "type": "real"
    #            },
                "weightScale": "linear"
    #            "sizeScale": "linear"
                }
              },
    #%% Then add the overflight count concentration layer
              {
                "id": count_pt_layer_id,
                "type": "point",
                "config": {
                  "dataId": count_id,
                  "label": "Counts/Hr",
                  "color": [
    #                119,
    #                110,
    #                87
                      246,
                      209,
                      138,
                      255
                  ],
                  "columns": {
                    "lat": "latitude",
                    "lng": "longitude"
    #                "altitude": "count 24hr"
                  },
                  "isVisible": False,
                  "visConfig": {
                    "radius": 20.0,
                    "fixedRadius": False,
                    "opacity": 0.40,
                    "outline": False,
                    "thickness": 1,
                    "colorRange": {
                      "name": "Custom",
                      "type": "Custom",
                      "category": "Custom",
                      "colors": [
                        "#a8bffc", #lt blue
                        "#4276fc", #dark blue
                        "#5aff9e", #lt green
                        "#01cc55", #dark green
                        "#fbf825", #yellow
                        "#fda40a", #orange
                        "#f11f7d", #red
                        "#ff00ff" #red purple
                      ]
                    },
                    "radiusRange": [
                      0,
                      50
                    ],
                    "hi-precision": False
                  }
                },
                "visualChannels": {
                  "colorField": {
                    "name": "scale_count",
                    "type": "real"
                  },
                  "colorScale": "quantize",
                  "sizeField": None,
                  "sizeScale": "linear"
                }
              },
    #%% Next add the Count Column layer
              {
                "id": count_hex_layer_id,
                "type": "hexagon",
                "config": {
                  "dataId": count_id,
                  "label": "Count Column",
                  "color": [
                      246,
                      209,
                      138,
                      255
                  ],
                  "columns": {
                    "lat": "latitude",
                    "lng": "longitude",
                    "altitude": "scale_count"
                  },
                  "isVisible": False,
                  "visConfig": {
    #                "radius": 24.0,
    #                "fixedRadius": False,
                    "opacity": 0.16,
    #                "outline": False,
    #                "thickness": 2,
                    "worldUnitSize": 1.0,
    #                "resolution": 8,
                    "resolution": 15,
                    "colorRange": {
                      "name": "Custom",
                      "type": "Custom",
                      "category": "Custom",
                      "colors": [
                        "#a8bffc", #lt blue
                        "#4276fc", #dark blue
                        "#5aff9e", #lt green
                        "#01cc55", #dark green
                        "#fbf825", #yellow
                        "#fda40a", #orange
                        "#f11f7d", #red
                        "#ff00ff" #red purple
                      ]
                    },
    #                "radiusRange": [
    #                  0,
    #                  50
    #                ],
                    "coverage": 0.6,
                    "sizeRange": [
                        0,
                        100
                      ],
                     "percentile": [
                        0,
                        100
                        ],
                    "elevationPercentile": [
                        0,
                        100
                      ],
                    "elevationScale": 25.0,
                    "hi-precision": False,
                    "colorAggregation": "maximum",
    #                "sizeAggregation": "maximum",
                    "enable3d": False
                  },
                  "textLabel": {
                    "field": '',
                    "color": [
                      255,
                      255,
                      255
                      ],
                        "size": 50,
                        "offset": [
                            0,
                            0
                        ],
                        "anchor": "middle"
                    }
                },
              "visualChannels": {
                "colorField": {
                  "name": "scale_count",
                  "type": "real"
                },
                "colorScale": "quantize",
                "sizeField": {
                    "name": "scale_count",
                    "type": "real"
                },
                "sizeScale": "linear"
                }
              },
    #%% Next add the Count Heat layer
              {
                "id": count_heat_layer_id,
                "type": "heatmap",
                "config": {
                  "dataId": count_id,
                  "label": "Count Heat",
                  "color": [
                      246,
                      209,
                      138,
                      255
                  ],
                  "columns": {
                    "lat": "latitude",
                    "lng": "longitude",
    #                "altitude": "scale_count"
                  },
                  "isVisible": False,
                  "visConfig": {
                    "opacity": 0.5,
                    "colorRange": {
                      "name": "Custom",
                      "type": "Custom",
                      "category": "Custom",
                      "colors": [
                        "#a8bffc", #lt blue
                        "#4276fc", #dark blue
                        "#5aff9e", #lt green
                        "#01cc55", #dark green
                        "#fbf825", #yellow
                        "#fda40a", #orange
                        "#f11f7d", #red
                        "#ff00ff" #red purple
                      ]
                    },
                    "radius": 28.0
                  },
                  "textLabel": {
                    "field": '',
                    "color": [
                      255,
                      255,
                      255
                      ],
                        "size": 50,
                        "offset": [
                            0,
                            0
                        ],
                        "anchor": "middle"
                    }
                },
                "visualChannels": {
                  "weightField": {
                    "name": "scale_count",
                    "type": "real"
                  },
                "weightScale": "linear"
                }
              },
    #%% Then add the overflight Lmax count layer
              {
                "id": lmax_pt_layer_id,
                "type": "point",
                "config": {
                  "dataId": lmax_id,
                  "label": "Lmax >60 dB/Hr",
                  "color": [
    #                119,
    #                110,
    #                87
                      246,
                      209,
                      138,
                      255
                  ],
                  "columns": {
                    "lat": "latitude",
                    "lng": "longitude"
    #                "altitude": "count 24hr"
                  },
                  "isVisible": False,
                  "visConfig": {
                    "radius": 20.0,
                    "fixedRadius": False,
                    "opacity": 0.40,
                    "outline": False,
                    "thickness": 1,
                    "colorRange": {
                      "name": "Custom",
                      "type": "Custom",
                      "category": "Custom",
                      "colors": [
                        "#a8bffc", #lt blue
                        "#4276fc", #dark blue
                        "#5aff9e", #lt green
                        "#01cc55", #dark green
                        "#fbf825", #yellow
                        "#fda40a", #orange
                        "#f11f7d", #red
                        "#ff00ff" #red purple
                      ]
                    },
                    "radiusRange": [
                      0,
                      50
                    ],
                    "hi-precision": False
                  }
                },
                "visualChannels": {
                  "colorField": {
                    "name": "scale_lmax",
                    "type": "real"
                  },
                  "colorScale": "quantize",
                  "sizeField": None,
                  "sizeScale": "linear"
                }
              },
    #%% Next add the overflight Lmax count Column layer
              {
                "id": lmax_hex_layer_id,
                "type": "hexagon",
                "config": {
                  "dataId": lmax_id,
                  "label": "Lmax >60 dB Column",
                  "color": [
                      246,
                      209,
                      138,
                      255
                  ],
                  "columns": {
                    "lat": "latitude",
                    "lng": "longitude",
                    "altitude": "scale_lmax"
                  },
                  "isVisible": False,
                  "visConfig": {
    #                "radius": 24.0,
    #                "fixedRadius": False,
                    "opacity": 0.16,
    #                "outline": False,
    #                "thickness": 2,
                    "worldUnitSize": 1.0,
    #                "resolution": 8,
                    "resolution": 15,
                    "colorRange": {
                      "name": "Custom",
                      "type": "Custom",
                      "category": "Custom",
                      "colors": [
                        "#a8bffc", #lt blue
                        "#4276fc", #dark blue
                        "#5aff9e", #lt green
                        "#01cc55", #dark green
                        "#fbf825", #yellow
                        "#fda40a", #orange
                        "#f11f7d", #red
                        "#ff00ff" #red purple
                      ]
                    },
    #                "radiusRange": [
    #                  0,
    #                  50
    #                ],
                    "coverage": 0.6,
                    "sizeRange": [
                        0,
                        100
                      ],
                     "percentile": [
                        0,
                        100
                        ],
                    "elevationPercentile": [
                        0,
                        100
                      ],
                    "elevationScale": 25.0,
                    "hi-precision": False,
                    "colorAggregation": "maximum",
    #                "sizeAggregation": "maximum",
                    "enable3d": False
                  },
                  "textLabel": {
                    "field": '',
                    "color": [
                      255,
                      255,
                      255
                      ],
                        "size": 50,
                        "offset": [
                            0,
                            0
                        ],
                        "anchor": "middle"
                    }
                },
              "visualChannels": {
                "colorField": {
                  "name": "scale_lmax",
                  "type": "real"
                },
                "colorScale": "quantize",
                "sizeField": {
                    "name": "scale_lmax",
                    "type": "real"
                },
                "sizeScale": "linear"
                }
              },
    #%% Next add the overflight Lmax Count Heat layer
              {
                "id": lmax_heat_layer_id,
                "type": "heatmap",
                "config": {
                  "dataId": lmax_id,
                  "label": "Lmax >60 dB Heat",
                  "color": [
                      246,
                      209,
                      138,
                      255
                  ],
                  "columns": {
                    "lat": "latitude",
                    "lng": "longitude",
    #                "altitude": "scale_count"
                  },
                  "isVisible": False,
                  "visConfig": {
                    "opacity": 0.5,
                    "colorRange": {
                      "name": "Custom",
                      "type": "Custom",
                      "category": "Custom",
                      "colors": [
                        "#a8bffc", #lt blue
                        "#4276fc", #dark blue
                        "#5aff9e", #lt green
                        "#01cc55", #dark green
                        "#fbf825", #yellow
                        "#fda40a", #orange
                        "#f11f7d", #red
                        "#ff00ff" #red purple
                      ]
                    },
                    "radius": 28.0
                  },
                  "textLabel": {
                    "field": '',
                    "color": [
                      255,
                      255,
                      255
                      ],
                        "size": 50,
                        "offset": [
                            0,
                            0
                        ],
                        "anchor": "middle"
                    }
                },
                "visualChannels": {
                  "weightField": {
                    "name": "scale_lmax",
                    "type": "real"
                  },
                "weightScale": "linear"
                }
              },
    #%% Then add the average overflight altitude above ground level (AGL) layer
              {
                "id": agl_pt_layer_id,
                "type": "point",
                "config": {
                  "dataId": agl_id,
                  "label": "Ave AGL",
                  "color": [
    #                119,
    #                110,
    #                87
                      246,
                      209,
                      138,
                      255
                  ],
                  "columns": {
                    "lat": "latitude",
                    "lng": "longitude"
    #                "altitude": "scale_agl"
                  },
                  "isVisible": False,
                  "visConfig": {
                    "radius": 20.0,
                    "fixedRadius": False,
                    "opacity": 0.40,
                    "outline": False,
                    "thickness": 1,
                    "colorRange": {
                      "name": "Custom",
                      "type": "Custom",
                      "category": "Custom",
                      "colors": [
                        "#ff00ff", #red purple (0 - 2143 ft)
                        "#f11f7d", #red (2143 - 4286 ft)
                        "#fda40a", #orange (4286 - 6428 ft)
                        "#fbf825", #yellow (6428 - 8571 ft)
                        "#00ff6a", #bright green (8571 - 10714 ft)
                        "#4276fc", #dark blue (12857 - 15000 ft)
                        "#a8bffc"  #lt blue (10714 - 12857 ft)
                      ]
                    },
                    "radiusRange": [
                      0,
                      50
                    ],
                    "hi-precision": False
                  }
                },
                "visualChannels": {
                  "colorField": {
                    "name": "scale_agl",
                    "type": "real"
                  },
                  "colorScale": "quantize",
                  "sizeField": None,
                  "sizeScale": "linear"
                }
              },
    #%% Next add the AGL Column layer
              {
                "id": agl_hex_layer_id,
                "type": "hexagon",
                "config": {
                  "dataId": agl_id,
                  "label": "Ave AGL Column",
                  "color": [
                      246,
                      209,
                      138,
                      255
                  ],
                  "columns": {
                    "lat": "latitude",
                    "lng": "longitude",
                    "altitude": "scale_agl"
                  },
                  "isVisible": False,
                  "visConfig": {
    #                "radius": 24.0,
    #                "fixedRadius": False,
                    "opacity": 0.16,
    #                "outline": False,
    #                "thickness": 2,
                    "worldUnitSize": 1.0,
    #                "resolution": 8,
                    "resolution": 15,
                    "colorRange": {
                      "name": "Custom",
                      "type": "Custom",
                      "category": "Custom",
                      "colors": [
                        "#ff00ff", #red purple (0 - 2143 ft)
                        "#f11f7d", #red (2143 - 4286 ft)
                        "#fda40a", #orange (4286 - 6428 ft)
                        "#fbf825", #yellow (6428 - 8571 ft)
                        "#00ff6a", #bright green (8571 - 10714 ft)
                        "#4276fc", #dark blue (12857 - 15000 ft)
                        "#a8bffc"  #lt blue (10714 - 12857 ft)
                      ]
                    },
    #                "radiusRange": [
    #                  0,
    #                  50
    #                ],
                    "coverage": 0.6,
                    "sizeRange": [
                        0,
                        100
                      ],
                     "percentile": [
                        0,
                        100
                        ],
                    "elevationPercentile": [
                        0,
                        100
                      ],
                    "elevationScale": 25.0,
                    "hi-precision": False,
                    "colorAggregation": "maximum",
    #                "sizeAggregation": "maximum",
                    "enable3d": False
                  },
                  "textLabel": {
                    "field": '',
                    "color": [
                      255,
                      255,
                      255
                      ],
                        "size": 50,
                        "offset": [
                            0,
                            0
                        ],
                        "anchor": "middle"
                    }
                },
              "visualChannels": {
                "colorField": {
                  "name": "scale_agl",
                  "type": "real"
                },
                "colorScale": "quantize",
                "sizeField": {
                    "name": "scale_agl",
                    "type": "real"
                },
                "sizeScale": "linear"
                }
              },
    #%% Next add the AGL Heat layer
              {
                "id": agl_heat_layer_id,
                "type": "heatmap",
                "config": {
                  "dataId": agl_id,
                  "label": "Ave AGL Heat",
                  "color": [
                      246,
                      209,
                      138,
                      255
                  ],
                  "columns": {
                    "lat": "latitude",
                    "lng": "longitude",
    #                "altitude": "scale_agl"
                  },
                  "isVisible": False,
                  "visConfig": {
                    "opacity": 0.5,
                    "colorRange": {
                      "name": "Custom",
                      "type": "Custom",
                      "category": "Custom",
                      "colors": [
                        "#ff00ff", #red purple (0 - 2143 ft)
                        "#f11f7d", #red (2143 - 4286 ft)
                        "#fda40a", #orange (4286 - 6428 ft)
                        "#fbf825", #yellow (6428 - 8571 ft)
                        "#00ff6a", #bright green (8571 - 10714 ft)
                        "#4276fc", #dark blue (12857 - 15000 ft)
                        "#a8bffc"  #lt blue (10714 - 12857 ft)
                      ]
                    },
                    "radius": 28.0
                  },
                  "textLabel": {
                    "field": '',
                    "color": [
                      255,
                      255,
                      255
                      ],
                        "size": 50,
                        "offset": [
                            0,
                            0
                        ],
                        "anchor": "middle"
                    }
                },
                "visualChannels": {
                  "weightField": {
                    "name": "scale_agl",
                    "type": "real"
                  },
                "weightScale": "linear"
                }
              },
    #%% Add the sighting point layer
              {
                "id": sighting_pt_layer_id,
                "type": "point",
                "config": {
                  "dataId": sighting_id,
                  "label": adsb_sightings,
                  "color": [
    #                119,
    #                110,
    #                87
                      246,
                      209,
                      138,
                      255
                  ],
                  "columns": {
                    "lat": "latitude",
                    "lng": "longitude",
    #                "altitude": "altitude"
                    "altitude": ""
                  },
                  "isVisible": True,
                  "visConfig": {
                    "radius": 5.0,
                    "fixedRadius": False,
                    "opacity": 0.2,
                    "outline": False,
                    "thickness": 1,
                    "colorRange": {
                      "name": "Custom",
                      "type": "Custom",
                      "category": "Custom",
                      "colors": [
                        "#ff00ff", #red purple (0 - 2143 ft)
                        "#f11f7d", #red (2143 - 4286 ft)
                        "#fda40a", #orange (4286 - 6428 ft)
                        "#fbf825", #yellow (6428 - 8571 ft)
                        "#00ff6a", #bright green (8571 - 10714 ft)
                        "#4276fc", #dark blue (12857 - 15000 ft)
                        "#a8bffc"  #lt blue (10714 - 12857 ft)
                      ]
                    },
                    "radiusRange": [
                      0,
                      50
                    ],
                    "hi-precision": False
                  }
                },
                "visualChannels": {
                  "colorField": {
                    "name": "altitude",
                    "type": "integer"
                  },
                  "colorScale": "quantize",
                  "sizeField": None,
                  "sizeScale": "linear"
                }
              },
    #%% Add the sighting line layer
            {
              "id": sighting_line_layer_id,
              "type": "line",
              "config": {
                "dataId": sighting_id,
                "label": "Sightings Line",
                "color": [
                  137,
                  218,
                  193,
                  255
                ],
                "columns": {
                  "lat0": "latitude",
                  "lng0": "longitude",
                  "lat1": "nxtlat",
                  "lng1": "nxtlon"
                },
                "isVisible": False,
                "visConfig": {
                  "opacity": 0.3,
                  "thickness": 3,
                  "colorRange": {
                    "name": "Custom",
                    "type": "Custom",
                    "category": "Custom",
                    "colors": [
                        "#ff00ff", #red purple (0 - 2143 ft)
                        "#f11f7d", #red (2143 - 4286 ft)
                        "#fda40a", #orange (4286 - 6428 ft)
                        "#fbf825", #yellow (6428 - 8571 ft)
                        "#00ff6a", #bright green (8571 - 10714 ft)
                        "#4276fc", #dark blue (12857 - 15000 ft)
                        "#a8bffc"  #lt blue (10714 - 12857 ft)
                    ]
                  },
                  "sizeRange": [
                    0,
                    10
                  ],
                  "targetColor": '',
                  "hi-precision": False
                },
                "textLabel": {
                  "field": '',
                  "color": [
                    255,
                    255,
                    255
                  ],
                  "size": 50,
                  "offset": [
                    0,
                    0
                  ],
                  "anchor": "middle"
                }
              },
              "visualChannels": {
                "colorField": {
                  "name": "altitude",
                  "type": "integer"
                },
                "colorScale": "quantize",
                "sizeField": None,
                "sizeScale": "linear"
              }
            }
            ], # End of layer set-up

    #%% Now set up the interaction configuration
            "interactionConfig": {
              "tooltip": {
                "fieldsToShow": {
                  sighting_id: [ # Sighting data
                    "icao",
                    "flight",
                    "aircraft type",
                    "route",
                    "altitude",
                    "segment",
                    "clock",
                    "arrive",
                    "depart",
                    "latitude",
                    "longitude"
                  ],
                  airport_id: [ # Airport data
                    "code",
                    "name"
                  ],
                  waypoint_id: [ # Waypoint data
    #                "code",
                    "name"
                  ],
                  other_id: [ # Other data
    #                "code",
                    "name"
                  ],
                  track_id: [ # Track data
                    "code",
                    "name",
                    "latitude",
                    "longitude",
                    "elevation"
                  ],
                  dnl_id: [ # DNL data
                    "24hr",
                    "18hr",
                    "maximum",
                    "00-06",
                    "06-12",
                    "12-18",
                    "18-24",
                    "scale_dnl"
                  ],
                  count_id: [ # Count data
                    "24hr",
                    "18hr",
                    "maximum",
                    "00-06",
                    "06-12",
                    "12-18",
                    "18-24",
                    "scale_count"
                  ],
                  lmax_id: [ # Lmax data
                    "24hr",
                    "18hr",
                    "maximum",
                    "00-06",
                    "06-12",
                    "12-18",
                    "18-24",
                    "scale_lmax"
                  ],
                  agl_id: [ # AGL data
                    "Ave AGL",
                    "Std Dev AGL",
                    "scale_agl"
                  ]
                },
                "enabled": True
              },
              "brush": {
                "size": 0.5,
                "enabled": False
              }
            },
            "layerBlending": "normal",
            "splitMaps": []
          },
          "mapState": {
            "bearing": 0,
            "dragRotate": False,
            # 37.450204	-122.143786
    #        "latitude": 37.53824292597814,
    #        "longitude": -122.8121695747103,
            "latitude": 37.450204,
            "longitude": -122.143786,
            "pitch": 0,
    #        "zoom": 7.429932582298195,
            "zoom": 10.0,
            "isSplit": False
          },
          "mapStyle": {
            "styleType": "dark",
            "topLayerGroups": {},
            "visibleLayerGroups": {
              "label": True,
              "road": True,
              "border": False,
              "building": True,
              "water": True,
              "land": True
            },
            "mapStyles": {}
          }
        }
      }
    keplergl['info'] = {
                        "app": "kepler.gl",
                        "created_at": "" + currentTime + \
                        "GMT-0700 (Pacific Daylight Time)"
    }

    #%% This section loads each flight and structures it as a different
    # dataset for kepler.gl
    #for icao in flights:
    #    plane = flights[icao]
    #    metaData = plane[0]
    #    for segment in range(1, len(plane)): #don't include metadata
    #        for sighting in plane[segment][1]: #don't include segment HDR data
    #            epoch_loc = sighting['seen_pos'] # Local sighting time
    #            clock_str = dt.datetime.fromtimestamp(epoch_loc). \
    #                    strftime('%H:%M:%S')
    #            alt_val = max(0.0, sighting['altitude'])
    #            sightData = [
    #                    sighting['hex'], #icao
    #                    sighting['flight'], #flightID
    #                    metaData['ac_type'], # Aircraft type
    #                    metaData['route'], # Aircraft route
    #                    sighting['lat'], #latitude
    #                    sighting['lon'], #longitude
    #                    min(max_altitude, alt_val), #altitude
    #                    plane[segment][0]['segment'], #segment number
    #                    epoch_loc - time_offset, # UTC time
    #                    clock_str, # Readable clock time string
    #                    plane[segment][0]['destination'], #destination airport
    #                    plane[segment][0]['origin']
    #                    ]
    #
    # Clean incoming data by altitude and distance limits
    alt_limit = 15000 # Restriction on raw data altitude
    dist_limit = 100 # Restriction on raw data distance
    do_limits = True # Switch for limiting raw data

    for icao in flights:
        plane = flights[icao]
        metaData = plane[0]
        v_ac_type = metaData['ac_type'] # Copy aircraft type
        # Loop through flight segments
        for i_seg in range(1, len(plane)): #don't include metadata
            n_sightings = len(plane[i_seg][1]) # Number of sightings plus HDR
            last_sighting_idx = n_sightings - 1  # Index to last sighting
            seg_meta = plane[i_seg][0] # Segment meta data
            if 'route' in seg_meta:
                v_route = seg_meta['route']
            else:
                v_route = 'other'
            # End if 'route' in seg_meta:

             # Loop through sightings, but don't include segment HDR data.
            for i_sight in range(1, n_sightings):
                current = plane[i_seg][1][i_sight]
                # If imposing limits, see if sighting inside limits
                if do_limits and (current['altitude'] > alt_limit or \
                          current['distance'] > dist_limit):
                    continue # Outside limits, ignore it
                # End if do_limits and (current['altitude'] > alt_limit...

                # Valid sighting, set up position of next sighting for line plot
                if i_sight < last_sighting_idx:
                    next_sight = plane[i_seg][1][i_sight + 1]
                else:
                    next_sight = plane[i_seg][1][i_sight] # No more, dup last one

                # Time value for UTC and local
                epoch_loc = current['seen_pos'] # Local sighting time
                clock_str = dt.datetime.fromtimestamp(epoch_loc). \
                        strftime('%H:%M:%S') # Readable time

                # Altitude above sea level
                alt_val = max(0.0, current['altitude'])

                # Now flesh out the data for this sighting
                sightData = [
                        current['hex'], #icao
                        current['flight'], #flightID
                        v_ac_type, # Aircraft type
                        v_route, # Aircraft route
                        current['lat'], #latitude
                        current['lon'], #longitude
                        min(max_altitude, alt_val), # scale-limited altitude
    #                    alt_val,
                        plane[i_seg][0]['segment'], #segment number
                        epoch_loc - time_offset, # UTC time
                        clock_str, # Readable clock time string
                        plane[i_seg][0]['destination'], #destination airport
                        plane[i_seg][0]['origin'], #origin airport
                        next_sight['lat'], #next position latitude
                        next_sight['lon'] #next position longitude
                        ]
                keplergl['datasets'][sighting_ord]["data"]['allData'] \
                        .append(sightData)
            # End for i_sight in range(1, n_sightings):
        # End for i_seg in range(1, len(plane)):
    # End for icao in flights:

    #%% Now create the data structure for landmarks: airports, waypoints, and other
    for aprt_info in landmarks['airports']:
        aprt_data = [aprt_info['code'],
                     aprt_info['name'],
                     aprt_info['latitude'],
                     aprt_info['longitude']
                     ]
        keplergl['datasets'][airport_ord]["data"]['allData'].append(aprt_data)
    # End for aprt_info in landmarks['airports']:

    for waypt_info in landmarks['waypoints']:
        waypt_data = [waypt_info['code'],
                     waypt_info['name'],
                     waypt_info['latitude'],
                     waypt_info['longitude']
                     ]
        keplergl['datasets'][waypoint_ord]["data"]['allData'].append(waypt_data)
    # End for waypt_info in landmarks['waypoints']:

    for other_info in landmarks['other']:
        other_data = [other_info['code'],
                     other_info['name'],
                     other_info['latitude'],
                     other_info['longitude']
                     ]
        keplergl['datasets'][other_ord]["data"]['allData'].append(other_data)
    # End for other_info in landmarks['other']:

    #%% Now create the data structure for tracks/slices
    # Each node entry has the form ["id", lat, lon, elev]
    fake_elev = 0 # Use a fake elevation to determine dot color
    for trk_seg in trk_keys:
        seg_list = track_data[trk_seg]
        for i_seg in range(len(seg_list)):
            seg_tmp = [trk_seg, # Main track ID
                       seg_list[i_seg][0], # Track node (y,x)
                       seg_list[i_seg][1], # Track node latitude
                       seg_list[i_seg][2], # Track node longitude
                       fake_elev] # Fake elevation
            keplergl['datasets'][track_ord]["data"]['allData'].append(seg_tmp)
        # End for i_seg in range(len(seg_list)):

        fake_elev += 1 # Bump the fake_elev for the next track
    # End for trk_seg in trk_keys:

    #%% Create the data structure for DNL values. The indexes for available values
    # are: DNL 24 hr, DNL 0-6, DNL 6-12, DNL 12-18, DNL 18-24
    for dnl_info in matrixData:
        # Now compute needed derived values
        dnl_24hr = float(dnl_info['DNL 24 hr'])
        dnl_18hr = round(10 * m.log10((10**(float(dnl_info['DNL 6-12'])/10) + \
                         10**(float(dnl_info['DNL 12-18'])/10) + \
                         10**(float(dnl_info['DNL 18-24'])/10)) / 3), 1)
        dnl_max = max(dnl_24hr, dnl_18hr, \
                      float(dnl_info['DNL 0-6']), \
                      float(dnl_info['DNL 6-12']), \
                      float(dnl_info['DNL 12-18']), \
                      float(dnl_info['DNL 18-24']))

        # Check for out of range values -- ignore them
        if min(dnl_24hr, dnl_18hr, dnl_max) < min_dnl:
            continue # Pass this one if out of range
        # End if max(dnl_24hr, dnl_18hr, dnl_max) < min_dnl

        dnl_data = [
                    float(dnl_info['Latitude']),
                    float(dnl_info['Longitude']),
                    dnl_24hr,
                    dnl_18hr,
                    dnl_max,
                    float(dnl_info['DNL 0-6']),
                    float(dnl_info['DNL 6-12']),
                    float(dnl_info['DNL 12-18']),
                    float(dnl_info['DNL 18-24']),
    #                min(max_dnl, dnl_18hr)
                    min(max_dnl, dnl_max)
                    ]
        keplergl['datasets'][dnl_ord]["data"]['allData'].append(dnl_data)
    # End for dnl_info in matrixData:

    #%% Create the data structure for count values. The indexes for available
    # values are:
    # # 24 hr: 0.15, # 24 hr: 0.20, # 24 hr: 0.25, # 24 hr: 0.30, # 24 hr: 0.35,
    # # 24 hr: 0.40,
    # # 0-6: 0.15, # 0-6: 0.20, # 0-6: 0.25, # 0-6: 0.30, # 0-6: 0.35, # 0-6: 0.40,
    # # 6-12: 0.15, # 6-12: 0.20, # 6-12: 0.25, # 6-12: 0.30, # 6-12: 0.35,
    # # 6-12: 0.40,
    # # 12-18: 0.15, # 12-18: 0.20, # 12-18: 0.25, # 12-18: 0.30, # 12-18: 0.35,
    # # 12-18: 0.40,
    # # 18-24: 0.15, # 18-24: 0.20, # 18-24: 0.25, # 18-24: 0.30, # 18-24: 0.35,
    # # 18-24: 0.40
    for count_info in matrixData:
        # Compute needed derived values
        count_24hr = float(count_info['# 24 hr: 0.40'])
        count_18hr = round((float(count_info['# 6-12: 0.40']) +
                       float(count_info['# 12-18: 0.40']) +
                       float(count_info['# 18-24: 0.40'])) / 3, 1)
        count_max = max(count_24hr, count_18hr,
                      float(count_info['# 0-6: 0.40']),
                      float(count_info['# 6-12: 0.40']),
                      float(count_info['# 12-18: 0.40']),
                      float(count_info['# 18-24: 0.40']))

        # Check for out of range values -- ignore them
        if max(count_24hr, count_18hr, count_max) < min_count:
            continue # Pass this one if out of range
        # if max(count_24hr, count_18hr, count_max) < min_count

        count_data = [
                float(count_info['Latitude']),
                float(count_info['Longitude']),
                count_24hr,
                count_18hr,
                count_max,
                float(count_info['# 0-6: 0.40']),
                float(count_info['# 6-12: 0.40']),
                float(count_info['# 12-18: 0.40']),
                float(count_info['# 18-24: 0.40']),
                min(max_count, count_max)
                ]
        keplergl['datasets'][count_ord]["data"]['allData'].append(count_data)
    # End for density_info in matrixData:

    #%% Create the data structure for Lmax values. The indexes for available
    # values are:
    # Lmax50 24 hr, Lmax50 0-6, Lmax50 6-12, Lmax50 12-18, Lmax50 18-24,
    # Lmax55 24 hr, Lmax55 0-6, Lmax55 6-12, Lmax55 12-18, Lmax55 18-24,
    # Lmax60 24 hr, Lmax60 0-6, Lmax60 6-12, Lmax60 12-18, Lmax60 18-24,
    # Lmax65 24 hr, Lmax65 0-6, Lmax65 6-12, Lmax65 12-18, Lmax65 18-24
    for lmax_info in matrixData:
        # Compute needed derived values
        lmax_24hr = float(lmax_info['Lmax60 24 hr'])
        lmax_18hr = round((float(lmax_info['Lmax60 6-12']) +
                       float(lmax_info['Lmax60 12-18']) +
                       float(lmax_info['Lmax60 18-24'])) / 3, 1)
        lmax_max = max(lmax_24hr, lmax_18hr,
                      float(lmax_info['Lmax60 0-6']),
                      float(lmax_info['Lmax60 6-12']),
                      float(lmax_info['Lmax60 12-18']),
                      float(lmax_info['Lmax60 18-24']))

        # Check for out of range values -- ignore them
        if max(lmax_24hr, lmax_18hr, lmax_max) < min_lmax_cnt:
            continue # Pass this one if out of range
        # if max(lmax_24hr, lmax_18hr, lmax_max) < min_lmax_cnt

        lmax_data = [
                float(lmax_info['Latitude']),
                float(lmax_info['Longitude']),
                lmax_24hr,
                lmax_18hr,
                lmax_max,
                float(lmax_info['Lmax60 0-6']),
                float(lmax_info['Lmax60 6-12']),
                float(lmax_info['Lmax60 12-18']),
                float(lmax_info['Lmax60 18-24']),
                min(max_lmax_cnt, lmax_max)
                ]
        keplergl['datasets'][lmax_ord]["data"]['allData'].append(lmax_data)
    # End for lmax_info in matrixData:

    #%% Create the data structure for AGL values. The indexes for available
    # values are:
    # alt_ave: 0.15, alt_std_dev: 0.15, alt_ave: 0.20, alt_std_dev: 0.20,
    # alt_ave: 0.25, alt_std_dev: 0.25, alt_ave: 0.30, alt_std_dev: 0.30,
    # alt_ave: 0.35, alt_std_dev: 0.35, alt_ave: 0.40, alt_std_dev: 0.40
    for agl_info in matrixData:
        # Compute needed derived values
        elev_val = max(0.0, float(agl_info['Elev']))
        agl_val = max(0.0, round(float(agl_info['alt_ave: 0.40']) - elev_val, 1))
        agl_stdev_val = float(agl_info['alt_std_dev: 0.40'])
        scale_agl = min(agl_val, max_ave_agl)

        # Then see what the maximum count/hr is at this spot
        count_24hr = float(agl_info['# 24 hr: 0.40'])
        count_18hr = round((float(agl_info['# 6-12: 0.40']) +
                       float(agl_info['# 12-18: 0.40']) +
                       float(agl_info['# 18-24: 0.40'])) / 3, 1)
        count_max = max(24 * count_24hr, 18 * count_18hr,
                      6 * float(agl_info['# 0-6: 0.40']),
                      6 * float(agl_info['# 6-12: 0.40']),
                      6 * float(agl_info['# 12-18: 0.40']),
                      6 * float(agl_info['# 18-24: 0.40']))

        # Check for out of range values -- ignore them
        if agl_val < min_ave_agl or count_max < min_agl_count:
            continue # Pass this one if out of range
        # if agl_val < min_ave_agl:

        agl_data = [
                float(agl_info['Latitude']),
                float(agl_info['Longitude']),
                agl_val,
                agl_stdev_val,
                scale_agl
                ]
        keplergl['datasets'][agl_ord]["data"]['allData'].append(agl_data)
    # End for agl_info in matrixData:

    #%% Now create the output file path and write the kepler config/data file
    path_out = os.path.join(pathOut, short_date_str, out_folder) \
        .replace('\\', '/')
    r_str = file_in[file_in.index('/FA') + 1 : ]
    out_file_name_stem = r_str[0 : \
                               r_str.index('_Sightings.') + len('_Sightings.')] + \
                               'KeplerPointPlot.'
    #out_file_name_stem = 'FAA_FOIA.KeplerPointPlot.'
    file_out = path_out + out_file_name_stem + hex_pack_dist + '.' + \
                airport_str + '.' + short_date_str + '.json'
    # print(file_out) # Debug
    with open(file_out, 'w') as outfile:
         json.dump(keplergl, outfile)

if __name__ == "__main__":
    runkepler()