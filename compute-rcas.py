# -*- coding: utf-8 -*-
"""
Created on Tue Sep  5 15:06:34 2017

@author: TCR
"""
import sys
import os
os.chdir('/Users/aditeyashukla/Documents/MONA/Route-Classification/') # Get to proper starting dir
import tkinter as tk
from tkinter import filedialog
import json
import math
import tcrlib as tcr
import time as tt
import datetime as ut
import Classify_routes as classify
#from copy import deepcopy

# =============================================================================
# This program reads assembled and filtered FlightAware sighting data and
# outputs a tab-separated (Excel-compatible) file of closest approach
# parameters for flight sightings close to a given observation location. We
# assume the input json file of sightings is grouped in sequence according to
# flight ICAO ids. Output file names use a base string input by the user with
# the form path/name-stem.yymmdd.

# This defines the list of airport origins and destinations to be included
# in the analysis of rcas from sightings. Airport origin, 'from-xxxx';
# destination, 'to-xxxx'; either origin or destination, 'xxxx'. Include
                        # all sightings if list is empty
airport_list = []

# Following are key points to assign airport origin/destination from rcas
#obs_list = [('SFO Approach Bay', t, 0),
#            ('SFO Depart Mid', 37.655673, -122.350902, 0),
#            ('SFO Depart W', 37.649624, -122.444802, 0),
#            ('SJC Approach SE', 37.319608, -121.880048, 0),
#            ('SJC Depart NW', 37.384070, -121.952794, 0)]

#obs_list = [('PAO Approach SE', 37.443466, -122.097752, 0),
#            ('PAO Depart NW', 37.465845, -122.120131, 0),
#            ('SQL Approach SE', 37.496174, -122.231122, 0),
#            ('SQL Depart NW', 37.526063, -122.265626, 0)]

#obs_list = [('PAO Bay', 37.463661, -122.097795, 0),
#            ('SQL Bair', 37.521547, -122.224567, 0)]

#obs_list = [('Charleston Gardens PA', 37.419890, -122.110223, 17)]

#obs_list = [('RHV S', 37.312846, -121.816957, 0),
#            ('RHV N', 37.341785, -121.839960, 0)]

#obs_list = [('HWD SE', 37.653828, -122.094216, 0),
#            ('HWD W', 37.651970, -122.128001, 0)]

#obs_list = [('OAK Approach SE', 37.667875, -122.147847, 0),
#            ('OAK Depart NW', 37.759685, -122.272565, 0)]

#obs_list = [('New SFO Approach Bay', 37.571794, -122.240496, 0)]

#obs_list = [('NUQ Approach SE', 37.371766, -122.026278, 0)]

#obs_list = [('SIDBY SFO Approach NW', 37.450711, -122.144722, 25)]

#obs_list = [('DUMBA SFO Approach W', 37.503517, -122.096147, 0)]

#obs_list = [('NUQ Depart NW', 37.428937, -122.055723, 0)]

#obs_list = [('New SJC NW', 37.397808, -121.963053, 0)]

#obs_list = [('FAITH', 37.401217, -121.861900, 135)]

# Flights from KSJC over Palo Alto
#obs_list = [('Page Mill & El Camino', 37.423034, -122.142057, 37)]

# Margaret Spak
#obs_list = [('Sta Margarita & Gilbert; MP', 37.4602603, -122.1629987, 46),
#            ('Tevis Pl; PA', 37.450204, -122.143786, 26)]

# TCR Tevis home
obs_list = [('Tevis Pl; PA', 37.450204, -122.143786, 26),
            ('SIDBY SFO Approach SE', 37.450711, -122.144722, 25),
            ('EDDYY(2)', 37.326444,   -122.099722, 958.8),
            ('EDDYY(3)', 37.374903,   -122.119028, 206.5),
            ('NARWL', 37.274781,   -122.079306, 778.0),
            ('OBS_1', 36.967737, -121.959109, 49.2),
            ('OBS_2', 37.115215, -122.016728, 738.2),
            ('BRINY',   37.304761, - 122.661656, 0.0),
            ('ARGGG',   37.392422, - 122.281631, 2183.3),
            ('PIRAT',  37.257650,   -122.863353, 0.0),
            ('FRELY', 37.510053, -121.795325, 1339),
            ('CEDES', 37.55082, -121.6246, 3110.2),
            ('FLOWZ', 37.592519, -121.264750, 95),
            ('ARCHI', 37.490806, -121.875556, 2146.5),
            ('LOZIT', 37.899325, -122.673194, 0),
            ('BDEGA', 37.823025, -122.5922, 0),
            ('CORKK', 37.733589, -122.49755, 52.5),
            ('BRIXX', 37.617844, -122.374528, 6.6)
            ]

# Don Jackson & TCR home
#obs_list = [('Tevis Pl; PA', 37.450204, -122.143786, 26),
#            ('845 Waverley', 37.444713, -122.155651, 49)]

# Luca Bommarito home
#obs_list = [('Johnson Ave; LA', 37.218400, -121.969301, 455)]

# Jon Zweig home
#obs_list = [('365 Colorado, PA', 37.430536, -122.134891, 24)]

#obs_list = [('Tevis Pl; PA', 37.450204, -122.143786, 26),
#            ('Mt View; RH', 37.390414, -122.078779, 30),
#            ('Foster City', 37.558550, -122.271080, 7),
#            ('San Jose', 37.3393900,  -121.8949600, 82)]
#obs_list = [('Foster City', 37.558550, -122.271080, 7),
#            ('San Jose', 37.3393900,  -121.8949600, 82),
#            ('San Tomas & Hwy 101', 37.381846, -121.963942, 32),
#            ('Tevis Pl; PA', 37.450204, -122.143786, 26)]
# Following is a list where TCR made sound monitor measurements 2015 - 2017
#obs_list = [('Clara & Louis; PA', 37.435897, -122.120822, 8),
#            ('Emerson & Kingsley; PA', 37.439779, -122.154523, 45),
#            ('Glenbrook & Los Palos; PA', 37.4048192, -122.1239675, 72),
#            ('La Para; PA', 37.412298, -122.133168, 53),
#            ('Larsens Landing; LA', 37.402188, -122.118712, 74),
#            ('Lincoln & Martin; PA', 37.45133, -122.1469, 28),
#            ('Lindenwood; Atherton', 37.472727, -122.17878, 34),
#            ('Mayfield Ave; SU', 37.413767, -122.161117, 191),
#            ('Palo Alto High School', 37.435996, -122.155690, 51),
#            ('Quail Ln & Robleda; LA', 37.376109, -122.126702, 209),
#            ('Rosewood & Ross; PA', 37.436, -122.128175, 13),
#            ('Sta Margarita & Gilbert; MP', 37.4602603, -122.1629987, 46),
#            ('Sunrise Dr & Skywood; Woodside', 37.393563, -122.261553, 1223),
#            ('Tevis Pl; PA', 37.450204, -122.143786, 26),
#            ('Waverley & Marion; PA', 37.43134, -122.13533, 23),
#            ('Wisteria & OConnor; EPA', 37.462082, -122.128619, 7),
#            ('Woodland & Menalto; MP', 37.457964, -122.15282, 43),
#            ('Waverley St; PA', 37.444679, -122.155651, 49)]
            
# Following is a list of observation points we compute stats for regularly
#obs_list = [('Atherton', 37.46133, -122.19774, 60),
#            ('Belle Haven School EPA', 37.476962, -122.161135, 20),
#            ('Belmont', 37.520210, -122.275800, 36),
#            ('Belmont (Pulgas)', 37.507066, -122.290833, 193),
#            ('Campbell', 37.287170, -121.949960, 200),
#            ('Cupertino', 37.3230000, -122.0321800, 236),
#            ('East Palo Alto', 37.46883, -122.14108, 20),
#            ('Foster City', 37.558550, -122.271080, 7),
#            ('Hillsborough', 37.559339, -122.35143, 216),
#            ('Ladera', 37.399444, -122.197222, 315),
#            ('Los Altos Hills', 37.371390, -122.137605, 292),
#            ('Los Altos', 37.3852183, -122.1141298, 157),
#            ('Mountain View', 37.390294, -122.082276, 105),
#            ('Palo Alto', 37.444606, -122.159891, 61),
#            ('Portola Valley', 37.384110, -122.235240, 463),
#            ('Redwood City', 37.485220, -122.236350, 20),
#            ('San Carlos', 37.507160, -122.260520, 30),
#            ('San Jose', 37.3393900,  -121.8949600, 82),
#            ('San Jose State Univ', 37.335626,  -121.881981, 85),
#            ('Santa Clara', 37.354110, -121.955240, 72),
#            ('Stanford University', 37.424107, -122.166077, 98),
#            ('Sunnyvale', 37.371233, -122.037403, 121),
#            ('Tevis Pl PA', 37.45005, -122.14405, 26),
#            ('Woodside', 37.447261, -122.242768, 292)]

# These are the sites where SFO has installed B&K sound monitors
#obs_list = [('Rinconada Library', 37.445307, -122.139311, 22),
#            ('Gamble Garden', 37.439826, -122.147788, 36),
#            ('Hoover Park', 37.429498, -122.128478, 18),
#            ('Tevis Place', 37.449959, -122.144194, 25)]

# These are new sites to check out rca distributions
#obs_list = [('SU Emergency Dept', 37.433875, -122.174511, 95),
#            ('VMC Emergency Dept', 37.313718, -121.934491, 150.0),
#            ('San Francisco Intl', 37.6188056, -122.3754167, 13.1)]

# Set mode switch to accommodate unique handling of computing rcas
mode_sw = 'rcas'
# Definition of nearness (miles from observation point) and altitude limits
# (ft) for considering tracks when computing closest approach
dmax = 5 # Max allowed ground distance (mi) from observation point
altmax = 15000 # Definition of maximum altitude allowed (ft) for rca
altmin = 10 # Minimum altitude allowed (ft)

# First, make a top-level tkinter instance - hide it since it is ugly and big.
root = tk.Tk()
root.withdraw()

# Make it almost invisible - no decorations, 0 size, top left corner.
root.overrideredirect(True)
root.geometry('0x0+80+50')

# Show window again and lift it to top so it can get focus,
# otherwise dialogs will end up behind the terminal.
root.deiconify()
root.lift()
root.focus_force()


# Now actually get the input file name from the user
json_filez = filedialog.askopenfilename(parent=root,
                        title='Choose an input sighting json file')

#Then fetch the output path and base name with format path/xxx.yymmdd
while True:
    ofile_name0 = filedialog.asksaveasfilename(parent=root,
                        title='Specify output file name stem (xxx.yymmdd)')
    # Make sure the suffix defines a date of the day being processed
    target_date = ofile_name0[ofile_name0.rindex('.') + 1 :]
    if len(target_date) != 6: # Length must be OK
        print('Invalid target date: {0}'.format(target_date))
        continue
    # End if len(target_date) != 6
    
    # Now split out the date components
    yy = '20' + target_date[0 : 2]
    mm = target_date[2 : 4]
    dd = target_date[4 : 6]
    if int(yy) > 16 and \
            int(mm) >= 1 and int(mm) <= 12 and \
            int(dd) >= 1 and int(dd) <= 31:
        break # Probably good enough, carry on
    # End if int(yy) > 16 and ...
    
    # Here still a problem
    print('Invalid target date: {0}'.format(target_date))
    continue
# End while True:
    
target_tuple = ut.date(int(yy),int(mm),int(dd))
target_date_st = tt.mktime(target_tuple.timetuple()) # UNIX version
target_date_end = target_date_st + 24 * 3600 # UNIX version
print('Date: {0}; Start: {1}, End: {2}'.format(target_date, \
      round(target_date_st, 1), round(target_date_end, 1)))

# Get rid of the top-level instance once to make it actually invisible.
root.destroy()

# =============================================================================

# The json file contains FlightAware sighting data covering a period coded
# in the file name and in json format. The format is as follows:
# {"tmin": n, "tmax": n, "maxdist": n, "dnear": n, "altmax": n,
#  "aircraft": {filtered_icao_record}.
# The json leading data information terms are defined as:
#   "tmin": n - Lowest sighting time in set
#   "tmax": n - Greatest sighting time in set
#   "maxdist": n - Maximum distance allowed for included sightings
#   "dnear": n - Maximum ground distance for estimating closest approach
#   "altmax": n - Maximum altitude for estimating closest approach

# Each {filtered_icao_record} has the structure:
# filtered_icao_record = {'icao-1': [{icao meta data-1},
#   [{segment 0 hdr}, [{sighting 0}, {sighting 1},... {sighting n}]],
#   [{segment 1 hdr}, [{sighting 0}, {sighting 1},... {sighting n}]],
#   ...
#   [{segment n hdr}, [{sighting 0}, {sighting 1},... {sighting n}]]],
#   'icao-2': [{icao meta data-2},
#   [{segment 0 hdr}, [{sighting 0}, {sighting 1},... {sighting n}]],
#   ...}
#
# Each {icao meta data-i} contains aircraft descriptive information:
#   {"icao": "value", "tail #": "value", "ac_type": "value"}
#
# Each {Segment data-i} contains info about the next flight segment. For a
# given icao, segments are separated from the input sighting stream by gaps
# much longer than the sighting interval:
#   {"segment": #, "gap": 0.0, "segment_start": epoch time, "segment_end":
#       epoch time, "flight": "id"}
#
# Within a given flight segment, each {Sighting info-i} is a sighting instance
# that has keys and values:
#   {"hex": "icao value", "flight": "value", "lat": value, "lon": value,
#    "distance": value, "seen_pos": value, "altitude": value,
#    "vert_rate": value, "track": value, "speed": value}
# {Sighting info-i} may also have an interpolation key "interp": "y" to
# signal that a missing sighting has been interpolated and added to the
# sighting set.

# =============================================================================

struct_labels = ['tmin', 'tmax', 'maxdist', 'dnear', 'altmax', 'dtsample', \
                 'aircraft']
rec_keys = ['hex','flight','lat','lon','distance', 'los_distance','seen_pos', \
              'altitude','vert_rate','track','speed']
interp_keys = ['lat', 'lon', 'distance', 'los_distance', 'seen_pos', \
              'altitude', 'vert_rate', 'track', 'speed']
meta_keys = ['icao', 'tail #', 'ac_type']
segment_keys = ['segment', 'gap', 'segment_start', 'segment_end', \
                'flight']

radius = 3957.5 # Earth's radius in mi
ft_in_mile = 5280 # Number of feet in a mile
interp_limit = 1 # Maximum number of interpolations between sightings
#rca_f_max = 1.0 # Maximum extrapolation distance about center pt to find rca
rca_f_max = 1.5 # Maximum extrapolation distance about center pt to find rca
v_sound = 1125/ft_in_mile # mi/sec; 343 m/sec, 1,125 ft/sec (at 68 °F)
dnl_mark = '$xx$' # Place holder in rca_str for DNL values

# Now read in specified accumulated sighting json record
with open(json_filez, 'r') as f_in:
    f_struct = json.loads(f_in.read()) # f_struct contains unpacked file
    f_in.close() # Done reading this file

# Then parse out the various fields of this structure and set limits
tmin = f_struct['tmin'] # Minimum time in assembled group
tmax = f_struct['tmax'] # Maximum time in assembled group
# Adjust tmin/tmax to the specified time limits of this run
tmin = max(target_date_st, tmin)
tmax = min(target_date_end, tmax)

# Maximum ground distance from feeder included in data set
maxdist = f_struct['maxdist']
if dmax > f_struct['dnear']: # d_near compatible?
    print ('dmax in input json file less than spec for' \
           'this rca run; reducing dmax from {0} to {1}' \
           .format(str(dmax), str(f_struct['dnear'])))
    dmax = f_struct['dnear'] # No pick lower value
# End if dmax
if altmax > f_struct['altmax']: # altmax compatible?
    print ('altmax in input json file less than spec for' \
           'this rca run; reducing altmax from {0} to {1}' \
           .format(str(altmax), str(f_struct['altmax'])))
    altmax = f_struct['altmax'] # No pick lower value
# End if altmax

# We also collect counts of overflights within various rca ranges and
# times of day: <= 0.15 mi; 0.2 mi; 0.25 mi; 0.3 mi; 0.35 mi; 0.4 mi
# 24-hr; 0:00 - 6:00; 6:00 - 12:00; 12:00 - 18:00; 18:00 - 24:00
ref_dist = [0.15, 0.20, 0.25, 0.30, 0.35, 0.40]
ref_dist_ref = 0.30 # Circle radius with area ~ square 0.5 mi on a side

# Compute area scale factors from circles with ref_dist radii to
# the area of a square 1/2 mile on side
area_scale = []
for i in range(len(ref_dist)):
    area_scale.append((ref_dist_ref/ref_dist[i])**2)
# End for i in range(len(ref_dist))

# Here at the top level we loop through the observation points
for i_obs in range(len(obs_list)):
    # Set up some params for this observation point
    name_obs, lat_obs, lon_obs, elev_obs = obs_list[i_obs] # Split out obs data
    obs_pt = (lat_obs, lon_obs)
    obs_pt_r = (lat_obs, lon_obs, elev_obs)
    name_obs_nosp = '.' + name_obs.replace(' ', '_') # Form for file names
    start_time = tt.time() # Note start time for this observer
    
    # Initialize the tuple holding what will be the DNL computations for this
    # observation point: 0:00 - 24:00; 0:00 - 6:00; 6:00 - 12:00;
    # 12:00 - 18:00; & 18:00 - 24:00
    dnl_tuple = (0.0, 0.0, 0.0, 0.0, 0.0) # Initialize for each matrix node
    
    # Initialize the attribute/value pair array that will contain the
    # overflight counts as a function of day interval and distance from the
    # observer point (see ref_dist above for distance intervals)
    oflght_cnts = {'24hr': [0, 0, 0, 0, 0, 0],
                   '0-6': [0, 0, 0, 0, 0, 0],
                   '6-12': [0, 0, 0, 0, 0, 0],
                   '12-18': [0, 0, 0, 0, 0, 0],
                   '18-24': [0, 0, 0, 0, 0, 0]}
    
    # Init the logging string
#    log_str = 'Log data for discarded tracks\n\n'
    log_str = ''
    # Make the date string part of output file names
    odate_str = ut.datetime.fromtimestamp(target_date_st).strftime('%Y%m%d')
    
    # Here we screen the input sighting data set for those flight segments
    # and sightings that are close enough to the observation point, and have
    # allowable altitudes, times, etc.
    # First make a clean and independent copy of the sighting data
    data_edit = {} # Place for edited tracks
#    data_work = {}
#    data_work = deepcopy(data_buffer)
    # The following is to make a clean copy of data_buffer. This could be done
    # using deepcopy, but it is very slow -- about 2x slower than just
    # re-reading the json file from disk.
    # So, now re-read the specified accumulated sighting json record
#    with open(json_filez, 'r') as f_in:
#        f_struct = json.loads(f_in.read()) # f_struct contains unpacked file
#        f_in.close() # Done reading this file
    # This is the full source of sighting details
    data_buffer = f_struct['aircraft']
    data_edit, log_str = tcr.screen_sighting_data(data_buffer, obs_pt_r, \
                              (target_date_st, target_date_end), dmax, \
                              (altmin, altmax), airport_list, log_str)
    
    # Prepare to compute the rca data for this observation point.
    # Init the tab-separated rca file header. In rca-hdr, 'dnl_mark' marks a
    # spot where we will enter DNL data after calculations are complete.
    rca_hdr = 'Closest approaches at {0} (lat: {1}, long: {2}, elevation: '\
        '{3}), {4}\nFlights within {5} miles and {6} < altitude < {7}' \
        ' feet\n'.format(name_obs, str(lat_obs), str(lon_obs), str(elev_obs), \
             odate_str, str(dmax), str(altmin), str(altmax))
    rca_hdr += dnl_mark + '\nicao (seg #)\tFlight_ID\tDate/Time' \
        '\tGnd Dist\trca_dist\trca_time\trca_lat\trca_lon\trca_fract' \
        '\tdp_theta\trca_alt\trca_speed\trca_vert_rate\trca_trk' \
        '\trca_snd_arr\tSEL\n'
    rca_str = '' # This is where the actual rca data are collected as computed
    
    # Loop through the icao keys to compute rcas. In the following code,
    # r_set has this format for a given icao key:
    # [{meta data}, {segment data 1}, {Sighting info-1}, {Sighting info-2},...,
    # {segment data 2}, {Sighting info-1}, {Sighting info-2}, ...]
    
    icao_keys = list(data_edit) # Fetch the latest list of track icao keys
    for i_icao in icao_keys:
        r_set = data_edit[i_icao] # Meta/segment/sighting data for given icao
        icao_meta = r_set[0] # Meta info for this icao
        # First save some stuff from the meta data record
        tail_no = icao_meta['tail_#']
        aircraft_type = icao_meta['ac_type']
        n_icao_segments = icao_meta['#_segments'] # Number of segments
        
        # Now run through the segment sets, starting after each segment header,
        # and then process each set of sighting data to calculate rcas. For
        # each segment we characterize the track into 4 categories:
        #   1) Single sighting in segment. Take that point as the rca. Note
        #       that this is a special case of 2) below.
        #   2) Sightings monotonic, increasing or decreasing distance. Take
        #       the closest point as the rca.
        #   3) Single point (distance valley) of closest approach. Compute
        #       the interpolated best estimate.
        #   4) Multiple closest approach sub-segments, separated by
        #       subsegments of increasing distance from the observer
        for j_seg in range(1, len(r_set)):
            seg_data = r_set[j_seg] # Data block for this segment
            seg_meta = seg_data[0] # Fetch the segment hdr data
            seg_sightings = seg_data[1] # And the list of sighting records
            
            # Extract some descriptive data elements
            segment_id = seg_meta['segment'] # Segment number
            gap_len = seg_meta['gap']
            t_segment_start = seg_meta['segment_start']
            odate1_str = ut.datetime.fromtimestamp(t_segment_start) \
                .strftime('%m/%d/%y %H:%M:%S')
            flight_id = seg_meta['flight'] # Segment flight_id
            
            # Init some calculation variables for this segment
            rca_d_min = 0 # Minimum rca_d found so far
            rca_trend = 0
            min_rca = () # Get ready to find a point of closest approach
            # Ptr to sightings spanning rca_min not set
            old_sight_ptr = new_sight_ptr = -1
            
            # Make a 1st pass through the set of sightings for this segment
            # to see what kind of track we are dealing with.
            # Init some parameters to record what we find:
            pca_min = [] # List of minimum distance points
            pca_max = [] # List of maximum distance points
            # Initial value of trend/slope parameter: 0 means not set; pos
            # means distance increasing; neg means distance decreasing.
            pca_trend = 0
            # Extremum sighting los so far in subsegment; max or min depends
            # on pca_trend sign
            pca_los_last = 0
            
            # Now map out the segment topography
            for k_sght in range(len(seg_sightings)):
                s_set = seg_sightings[k_sght] # Next sighting record
                los_s = s_set['los_distance']
                if k_sght == 0: # Get things started on the 1st sighting
                    k_los_last = k_sght # Save los ptrs
                    pca_los_last = los_s
                    continue # Move to next sighting
                # End if k_sght == 0
                
                # Here we have the second and later sightings
                if pca_trend == 0: # If unsure reset values and look for trend
                    if los_s < pca_los_last: # If getting closer
                        pca_trend = -1 # Save downward trend
                    elif los_s > pca_los_last: # If getting farther
                        pca_trend = +1 # Save upward trend
                    else: # Values equal here, can't make a decision
                        continue
                    # End if los_s < pca_los_last ... elifs
                    
                    # Update stuff before moving on
                    k_los_last = k_sght # Update ptr
                    pca_los_last = los_s # Reset extremum
                    continue # Move to next sighting
                # End if pca_trend == 0
                
                # Here things have an on-going negative trend
                if pca_trend < 0: # If here on a downward slope
                    if los_s > pca_los_last: # If now getting farther
                        # Save the valley location (ptr, min)
                        pca_min.append((k_los_last, pca_los_last))
                        pca_trend = +1 # Set new upward trend
                    else: # Keep  looking for real valley
                        pass
                    # End if los_s > pca_los_last: # If now getting farther
                    
                    # Update stuff before moving on
                    pca_los_last = los_s # Update extremum
                    k_los_last = k_sght # Update ptr
                    continue # Move to next sighting
                # End if pca_trend < 0
                
                # Here things have an on-going postive trend
                if pca_trend > 0:
                    if los_s < pca_los_last: # If we have the peak
                        # Save the peak location (ptr, min)
                        pca_max.append((k_los_last, pca_los_last))
                        pca_trend = -1 # Set new downward trend
                    else: # Keep  looking for real peak
                        pass
                    # End if los_s < pca_los_last ... elifs
                    
                    # Update stuff before moving on
                    pca_los_last = los_s # Update extremum
                    k_los_last = k_sght # Save min ptr
                    continue # Move to next sighting
                # End if pca_trend > 0
            # End for k_sght in range(len(seg_sightings)):
            
            # Here we have the segment topography with some number of maximum
            # and/or minimum distances from the observer. Make sure they are
            # consistent with each other.
            if not abs(len(pca_min) - len(pca_max)) <= 1:
                print('Warning: sighting topography inconsistent for ICAO: ' \
                      '{0} -- Segment: {1}'.format(icao_meta, seg_meta))
                sys.exit()
            # End if not abs(len(pca_min) ...
            
            # Looks OK so produce the relevant rca values. If we have a segment
            # with only a monotonic set of distances to the observer, we
            # compute an rca for the point closest to the observer. If we have
            # any valleys, we compute an rca for each valley and ignore the
            # peaks. If we have a single peak, we compute two rcas, one for
            # each monotonic track leading to and from the peak.
            # FIRST we deal with the pure monotonic case...
            if len(pca_min) == 0 and len(pca_max) == 0:
                # Here we have a monotonic track
                if pca_trend <= 0:
                    # Here things were flat or getting closer, use the last
                    # sighting as the rca.
                    s_set_1 = seg_sightings[-1]
                else: # Here we're getting farther, use the 1st sighting as rca
                    s_set_1 = seg_sightings[0]
                # End if pca_trend <= 0
                
                # Split out the sighting component values
                time_s_1 = s_set_1['seen_pos']
                d_s_1 = s_set_1['distance']
                los_s_1 = s_set_1['los_distance']
                alt_s_1 = s_set_1['altitude']
                trk_s_1 = s_set_1['track']
                speed_s_1 = s_set_1['speed']
                vert_rate_s_1 = s_set_1['vert_rate']
                lat_s_1 = s_set_1['lat']
                lon_s_1 = s_set_1['lon']
                
                # Fill out the rca pt data
                rca_tpl = tcr.rca((time_s_1, lat_s_1, lon_s_1, alt_s_1), \
                           (), obs_pt, elev_obs)
                rca_d, rca_t, rca_lat, rca_lon, rca_f, rca_alt = rca_tpl
                rca_snd_arr = rca_t + rca_d/v_sound
                rca_gnd_dist = d_s_1
                
                # Here's something of an assumption that the segment sightings
                # outside the dmax zone are regular and nearly linear
                rca_sel = tcr.compute_sel(rca_d, speed_s_1, rca_alt)
                
                # Now set the best rca and output it
                min_rca = rca_tpl + (90.0, speed_s_1, trk_s_1, \
                             rca_snd_arr, d_s_1, rca_sel, vert_rate_s_1)
                
                # Format and output last rca data as needed
                if mode_sw != 'rca-map':
                    rca_str += tcr.fmt_rca_str(i_icao, flight_id, \
                                   segment_id, min_rca)
                    if mode_sw == 'airport':
                        rca_str = rca_str[: -2] # Lose trailing \n
                    # End if mode_sw == 'airport':
                # End if mode_sw != 'rca-map':
                
                # Update the running SEL sums for DNL calculations
                dnl_tuple = tcr.dnl_sums(dnl_tuple, rca_sel, rca_t - tmin)
                # The update the overflight counts
                oflght_cnts = tcr.ovflght_cnts(oflght_cnts, rca_gnd_dist, \
                                               rca_t - tmin, ref_dist)
                
                continue # And continue on to the next segment
            # End if len(pca_min) == 0 and len(pca_max) == 0:
            
            # NEXT we deal with case of one or more valleys, computing an rca
            # for each valley.
            if len(pca_min) > 0:
                for i_valley in range(len(pca_min)):
                    # 1st find the ptr to the sighting just before the min
                    k_idx_l = max(0, pca_min[i_valley][0] - 1)
                    # 2nd find the ptr to the sighting just after the min
                    k_idx_r = min(len(seg_sightings) - 1, \
                                   pca_min[i_valley][0] + 1)
                    rca_d_min = 0 # Init to find the nearest rca
                    
                    # Now compute the best rca around the current valley
                    for j_idx in range(k_idx_l, k_idx_r):
                        # Set a P1,P2 pair to compute the next rca
                        s_set_1 = seg_sightings[j_idx] # 1st sighting record
                        time_s_1 = s_set_1['seen_pos']
                        d_s_1 = s_set_1['distance']
                        los_s_1 = s_set_1['los_distance']
                        alt_s_1 = s_set_1['altitude']
                        trk_s_1 = s_set_1['track']
                        speed_s_1 = s_set_1['speed']
                        vert_rate_s_1 = s_set_1['vert_rate']
                        lat_s_1 = s_set_1['lat']
                        lon_s_1 = s_set_1['lon']
                        time_str_1 = ut.datetime.fromtimestamp(time_s_1). \
                            strftime('%m/%d/%y %H:%M:%S')
                        
                        s_set_2 = seg_sightings[j_idx + 1] # 2nd sighting
                        time_s_2 = s_set_2['seen_pos']
                        d_s_2 = s_set_2['distance']
                        los_s_2 = s_set_2['los_distance']
                        alt_s_2 = s_set_2['altitude']
                        trk_s_2 = s_set_2['track']
                        speed_s_2 = s_set_2['speed']
                        vert_rate_s_2 = s_set_2['vert_rate']
                        lat_s_2 = s_set_2['lat']
                        lon_s_2 = s_set_2['lon']
                        time_str_2 = ut.datetime.fromtimestamp(time_s_2). \
                            strftime('%m/%d/%y %H:%M:%S')
                        
                        # Then compute this rca
                        rca_tpl = tcr.rca( \
                                      (time_s_1, lat_s_1, lon_s_1, alt_s_1), \
                                      (time_s_2, lat_s_2, lon_s_2, alt_s_2), \
                                      obs_pt, elev_obs)
                        # And split out the components
                        rca_d, rca_t, rca_lat, rca_lon, rca_f, rca_alt = \
                            rca_tpl
                        
                        # Check if scale factor is reasonable
                        if abs(rca_f - 0.5) <= rca_f_max:
                            # Good one here, see if rca is better
                            if rca_d_min == 0 or rca_d < rca_d_min:
                                rca_d_min = rca_d
                            # End if rca_d_min == 0 or rca_d < rca_d_min:
                        # End if abs(rca_f - 0.5) > rca_f_max
                    
                    # End for j_idx in range(k_idx_l, k_idx_r):
                    
                    # See if any of the rca calculations were OK
                    if rca_d_min == 0:
                        # Here the interpolations were wonky.
#                        print('Warning: no good rca_f found for {0}, segment' \
#                              ' {1}, at sighting {2}' \
#                              .format(icao_meta, seg_meta, \
#                                      str(pca_min[i_valley][0])))
                        # So just use the valley pt with minimum los
                        s_set_1 = seg_sightings[pca_min[i_valley][0]]
                        
                        # Split out the sighting component values
                        time_s_1 = s_set_1['seen_pos']
                        d_s_1 = s_set_1['distance']
                        los_s_1 = s_set_1['los_distance']
                        alt_s_1 = s_set_1['altitude']
                        trk_s_1 = s_set_1['track']
                        speed_s_1 = s_set_1['speed']
                        vert_rate_s_1 = s_set_1['vert_rate']
                        lat_s_1 = s_set_1['lat']
                        lon_s_1 = s_set_1['lon']
                        
                        # Fill out the rca pt data
                        rca_tpl = tcr.rca((time_s_1, lat_s_1, lon_s_1, \
                                   alt_s_1), (), obs_pt, elev_obs)
                        rca_d, rca_t, rca_lat, rca_lon, rca_f, rca_alt = \
                                rca_tpl
                        rca_snd_arr = rca_t + rca_d/v_sound
                        rca_gnd_dist = d_s_1
                        
                        # Here's something of an assumption that the segment
                        # sightings outside the dmax zone are regular and
                        # nearly linear
                        rca_sel = tcr.compute_sel(rca_d, speed_s_1, rca_alt)
                        
                        # Now set the best rca and output it
                        min_rca = rca_tpl + (90.0, speed_s_1, trk_s_1, \
                                     rca_snd_arr, d_s_1, rca_sel, \
                                     vert_rate_s_1)
                    else:
                        # Here we have the best rca estmate for the current
                        # valley.  Compute the other components of this rca...
                        # Time the sound will be heard at observer
                        rca_snd_arr = rca_t + rca_d/v_sound
                        # Interpolate ground dist, speed, & vert_rate at rca
                        rca_gnd_dist = round(tcr.sph_distance((rca_lat, \
                                           rca_lon), obs_pt), 2)
                        rca_speed, rca_vert_rate = tcr.linear_interp( \
                                             (speed_s_1, vert_rate_s_1), \
                                             (speed_s_2, vert_rate_s_2), rca_f)
                        # Finally compute the estimated SEL for the aircraft
                        rca_sel = tcr.compute_sel(rca_d, rca_speed, rca_alt)
                        
                        # As a computation check, find angle between the vector
                        # from the obs pt to the rca pt and the vector between
                        # sighting pt 1 and pt 2.
                        # Make Cartesian vectors to the key points
                        r_1 = tcr.vector_scale( \
                                   tcr.cart_vector((lat_s_1, lon_s_1)), \
                                   (1 + alt_s_1/(ft_in_mile * radius)))
                        r_2 = tcr.vector_scale( \
                                   tcr.cart_vector((lat_s_2, lon_s_2)), \
                                   (1 + alt_s_2/(ft_in_mile * radius)))
                        r_obs = tcr.cart_vector((lat_obs, lon_obs))
                        r_rca = tcr.vector_scale( \
                                    tcr.cart_vector((rca_lat, rca_lon)), \
                                    (1 + rca_alt/(ft_in_mile * radius)))
                        # Then compute key interpoint vectors
                        v_12 = tcr.vector_diff(r_2, r_1)
                        v_obs_rca = tcr.vector_diff(r_rca, r_obs)
                        # And finally find the angle between them via dot product
                        dp, dpθ = tcr.dotproduct(v_12, v_obs_rca)
                        # Then estimate the track direction (angle measured
                        # clockwise from polar north).
                        rca_trk = tcr.interp_trk(trk_s_1, trk_s_2, rca_f)
                        
                        # And save them in the data tuple
                        min_rca = rca_tpl + (dpθ, rca_speed, rca_trk, \
                                     rca_snd_arr, rca_gnd_dist, rca_sel, \
                                     rca_vert_rate)
                    #End if rca_d_min == 0
                    
                    # Format and output last rca data as needed
                    if mode_sw != 'rca-map':
                        rca_str += tcr.fmt_rca_str(i_icao, flight_id, \
                                       segment_id, min_rca)
                        if mode_sw == 'airport':
                            rca_str = rca_str[: -2] # Lose trailing \n
                        # End if mode_sw == 'airport':
                    # End if mode_sw != 'rca-map':
                    
                    # Update the running SEL sums for DNL calculations
                    dnl_tuple = tcr.dnl_sums(dnl_tuple, rca_sel, rca_t - tmin)
                    # The update the overflight counts
                    oflght_cnts = tcr.ovflght_cnts(oflght_cnts, rca_gnd_dist, \
                                               rca_t - tmin, ref_dist)
                    
                # End for i_valley in range(len(pca_min)):
                
                continue # move on to next segment
            # End if len(pca_min) > 0:
            
            # Here we should have a single peak, where the distance to the
            # peak sighting is bigger than the distances for the rest of the
            # track. We will assume rcas to exist at the two sides of the peak
            # at the extremes of the segment sightings.
            # First make sure we haven't screwed up...
            if len(pca_max) != 1:
                print('Warning: sighting topography inconsistent for ICAO: ' \
                      '{0} -- Segment: {1}'.format(icao_meta, seg_meta))
                sys.exit()
            # End if len(pca_max) != 1:
            
            # First do the earliest part of the track
            s_set_1 = seg_sightings[0]
            
            # Split out the sighting component values
            time_s_1 = s_set_1['seen_pos']
            d_s_1 = s_set_1['distance']
            los_s_1 = s_set_1['los_distance']
            alt_s_1 = s_set_1['altitude']
            trk_s_1 = s_set_1['track']
            speed_s_1 = s_set_1['speed']
            vert_rate_s_1 = s_set_1['vert_rate']
            lat_s_1 = s_set_1['lat']
            lon_s_1 = s_set_1['lon']
            
            # Fill out the rca pt data
            rca_tpl = tcr.rca((time_s_1, lat_s_1, lon_s_1, alt_s_1), \
                       (), obs_pt, elev_obs)
            rca_d, rca_t, rca_lat, rca_lon, rca_f, rca_alt = rca_tpl
            rca_snd_arr = rca_t + rca_d/v_sound
            rca_gnd_dist = d_s_1
            
            # Here's something of an assumption that the segment sightings
            # outside the dmax zone are regular and nearly linear
            rca_sel = tcr.compute_sel(rca_d, speed_s_1, rca_alt)
            
            # Now set the best rca and output it
            min_rca = rca_tpl + (90.0, speed_s_1, trk_s_1, \
                         rca_snd_arr, d_s_1, rca_sel, vert_rate_s_1)
            
            # Format and output last rca data as needed
            if mode_sw != 'rca-map':
                rca_str += tcr.fmt_rca_str(i_icao, flight_id, \
                               segment_id, min_rca)
                if mode_sw == 'airport':
                    rca_str = rca_str[: -2] # Lose trailing \n
                # End if mode_sw == 'airport':
            # End if mode_sw != 'rca-map':
            
            # Update the running SEL sums for DNL calculations
            dnl_tuple = tcr.dnl_sums(dnl_tuple, rca_sel, rca_t - tmin)
            # The update the overflight counts
            oflght_cnts = tcr.ovflght_cnts(oflght_cnts, rca_gnd_dist, \
                                           rca_t - tmin, ref_dist)
            
            # Then do the last part of the track
            s_set_1 = seg_sightings[-1]
            
            # Split out the sighting component values
            time_s_1 = s_set_1['seen_pos']
            d_s_1 = s_set_1['distance']
            los_s_1 = s_set_1['los_distance']
            alt_s_1 = s_set_1['altitude']
            trk_s_1 = s_set_1['track']
            speed_s_1 = s_set_1['speed']
            vert_rate_s_1 = s_set_1['vert_rate']
            lat_s_1 = s_set_1['lat']
            lon_s_1 = s_set_1['lon']
            
            # Fill out the rca pt data
            rca_tpl = tcr.rca((time_s_1, lat_s_1, lon_s_1, alt_s_1), \
                       (), obs_pt, elev_obs)
            rca_d, rca_t, rca_lat, rca_lon, rca_f, rca_alt = rca_tpl
            rca_snd_arr = rca_t + rca_d/v_sound
            rca_gnd_dist = d_s_1
            
            # Here's something of an assumption that the segment sightings
            # outside the dmax zone are regular and nearly linear
            rca_sel = tcr.compute_sel(rca_d, speed_s_1, rca_alt)
            
            # Now set the best rca and output it
            min_rca = rca_tpl + (90.0, speed_s_1, trk_s_1, \
                         rca_snd_arr, d_s_1, rca_sel, vert_rate_s_1)
            
            # Format and output last rca data as needed
            if mode_sw != 'rca-map':
                rca_str += tcr.fmt_rca_str(i_icao, flight_id, \
                               segment_id, min_rca)
                if mode_sw == 'airport':
                    rca_str = rca_str[: -2] # Lose trailing \n
                # End if mode_sw == 'airport':
            # End if mode_sw != 'rca-map':
            
            # Update the running SEL sums for DNL calculations
            dnl_tuple = tcr.dnl_sums(dnl_tuple, rca_sel, rca_t - tmin)
            # The update the overflight counts
            oflght_cnts = tcr.ovflght_cnts(oflght_cnts, rca_gnd_dist, \
                                           rca_t - tmin, ref_dist)
            
#            continue # Move on to the next segment
            
        # End for j_seg in range(1, len(r_set)):
        
    # End for i_icao loop -- do the next icao key relative to this obs pt
    
    # Before we output the data for this observation point, compute the final
    # DNLs and proximate counts
    dnl_24hr, dnl_1, dnl_2, dnl_3, dnl_4 = dnl_tuple # Split out summed SELs
    # and convert them to energy to second
    if dnl_24hr > 0:
        dnl_24hr = 10 * math.log10(dnl_24hr / (24 * 3600))
    if dnl_1 > 0:
        dnl_1 = 10 * math.log10(dnl_1 / (6 * 3600))
    if dnl_2 > 0:
        dnl_2 = 10 * math.log10(dnl_2 / (6 * 3600))
    if dnl_3 > 0:
        dnl_3 = 10 * math.log10(dnl_3 / (6 * 3600))
    if dnl_4 > 0:
        dnl_4 = 10 * math.log10(dnl_4 / (6 * 3600))
    
    # Then make a string to edit into the output rca text header
    dnl_str = f'{name_obs}\t{round(dnl_24hr, 1)}\t{round(dnl_1, 1)}\t' + \
        f'{round(dnl_2, 1)}\t{round(dnl_3, 1)}\t{round(dnl_4, 1)}'
    
    # Now normalize the overflight counts w/r to time interval and std area
    time_keys = list(oflght_cnts) # Get the key names for the segment data
    for i_key in time_keys:
        for j_cnt in range(len(oflght_cnts[i_key])):
            # Normalize oflght_cnts by time and distance to per-hour, per
            # half-mile square values
            if i_key == '24hr':
                dnl_str += '\t' + \
                  str(round(oflght_cnts[i_key][j_cnt] * \
                            area_scale[j_cnt]/ 24, 1))
            else:
                dnl_str += '\t' + \
                  str(round(oflght_cnts[i_key][j_cnt] * \
                            area_scale[j_cnt]/ 6, 1))
        # End for j_cnt in range(len(oflght_cnts[i_seg])):
    # End for i_key in time_keys:
    
    rca_hdr = rca_hdr.replace(dnl_mark, dnl_str) # And do the edit
    rca_str = rca_hdr + rca_str # Finish the string of rcas
    # Make the closest approach file name and write what we have
    ofile_name = ofile_name0 + name_obs_nosp +'.rca.txt'
    with open(ofile_name, 'w') as f_out:
        f_out.write(rca_str)
        f_out.close # Done, close ouput file
    
    # Make the text file name and write what we have
#    ofile_name = ofile_name0 + name_obs_nosp + '.text.txt'
#    with open(ofile_name, 'w') as f_out:
#        f_out.write(print_str)
#        f_out.close # Done, close ouput file
    
    # Make the log file name and write what we have
    if log_str != '':
        ofile_name = ofile_name0 + name_obs_nosp + '.log.txt'
        with open(ofile_name, 'w') as f_out:
            f_out.write(log_str)
            f_out.close # Done, close ouput file
        # End with open(ofile_name, 'w') as f_out:
    # End if log_str != '':
    
    end_time = tt.time() # Note end time for this observer
    print('Done computing rcas for {0}  ({1} seconds)'.format(name_obs, \
          round(end_time - start_time, 1)))

# End for i_obs

print('\nDone computing rcas for all observation points')
print('\nStarting classification module')
target_date_input = input('Enter the target date (yymmdd): ')
classify.sightingReader(target_date_input)