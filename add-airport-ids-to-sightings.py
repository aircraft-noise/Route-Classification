# -*- coding: utf-8 -*-
"""
Created on Tue Sep  5 15:06:34 2017

@author: TCR
"""
#import sys
import os
os.chdir('/Users/aditeyashukla/Downloads/tcr-python-expts/') # Get to proper starting dir
#import tkinter as tk
#from tkinter import filedialog
import sys
import glob as ll
import json as simplejson
import math
import tcrlib as tcr
import time as tt
import datetime as ut
#from copy import deepcopy

# =============================================================================
# This routine performs the condition tests for an rca at given airport arrival
# or departure check point. The cond_set is a dict structure that includes
# maximum and minimum values for keys: 'track', 'track_hi', 'track_low',
# 'lon', 'alt', and 'vrate'. The routine returns True if the conditions pass
# or False if they do not.
# =============================================================================
def apply_conditions(cond_set, rca_data):
    # Here we break out the components of the condition dict. There is a
    # special case for the 'track' key: if an arrival or departure is near
    # N, the track value may range from 0 to nn or from nn to 360. For this
    # case, there is no 'track' key, but the two ranges about 0 are given by
    # 'track_hi' and 'track_low'.
    if 'track' in cond_set:
        track_min, track_max = cond_set['track']
    else:
        track_hi_min, track_hi_max = cond_set['track_hi']
        track_low_min, track_low_max = cond_set['track_low']
    # End if 'track' in cond_set:
    lat_min, lat_max = cond_set['lat']
    lon_min, lon_max = cond_set['lon']
    alt_min, alt_max = cond_set['alt']
    vrate_min, vrate_max = cond_set['vrate']

    # Here we break out the components of the rca_data tuple
    rca_d, rca_t, rca_lat, rca_lon, rca_f, rca_alt, rca_ang, rca_speed, \
        rca_trk, rca_snd_arr, rca_gnd_dist, rca_sel, rca_vert_rate = rca_data
    
    # Now we apply the conditions
    if 'track' in cond_set: # Do this if 'track" = usual case
        if rca_trk >= track_min and rca_trk <= track_max and \
                rca_lat >= lat_min and rca_lat <= lat_max and \
                rca_lon >= lon_min and rca_lon <= lon_max and \
                rca_alt >= alt_min and rca_alt <= alt_max and \
                rca_vert_rate >= vrate_min and rca_vert_rate <= vrate_max:
            return(True) # This matches the approach/departure conditions
        else:
            return(False) # Not an approach/departure rca
        # End if rca_trk >= track_min...
    else: # Do this if 'track_hi/low" spans 360/0
        if ((rca_trk >= track_hi_min and rca_trk <= track_hi_max) or \
                (rca_trk >= track_low_min and rca_trk <= track_low_max)) and \
                rca_lat >= lat_min and rca_lat <= lat_max and \
                rca_lon >= lon_min and rca_lon <= lon_max and \
                rca_alt >= alt_min and rca_alt <= alt_max and \
                rca_vert_rate >= vrate_min and rca_vert_rate <= vrate_max:
            return(True) # This matches the approach/departure conditions
        else:
            return(False) # Not an approach/departure rca
        # End if rca_trk >= track_min...
# End def apply_conditions(cond_set, rca_data):
    

# =============================================================================
# This routine computes whether or not a given rca represents an approach or
# departure for one of the local airports: KSFO, KSQL, KPAO, KNUQ, KSJC, KRHV,
# KHWD, and KOAK.
# The criteria for whether or not a given rca represents an approach or
# departure for each airport are derived from statistical cluster charts for
# each approach and departure path. The criteria include, gps range, altitude
# range, heading range, vertical velocity, etc. as needed. Because the criteria
# are indiosyncratic for specific airport configurations, the following code is
# basically a decision tree for each airport in sequence. Once a match is found,
# the airport code and a to/from code are returned as a tuple to the caller.
# If no match is found, an empty tuple is returned.
# =============================================================================
def check_airport(airport_obs_name, rca_data):
    # Here is a list of the canonical airport check obs point names
#    airport_chk = ['SFO Bay', 'SFO N', 'SFO W', \
#                   'SJC NW-SE', 'SJC Depart NW-SE']
    # Here is a list of known airport approach/depart OK conditions
    sfo_approach_bay_conds = {'track': (260, 360), 'lat': (37.54, 37.61), \
                     'lon': (-122.35, -122.15), 'alt': (10, 5000), \
                     'vrate': (-5000, -50)}
    sfo_approach_SIDBY_conds = {'track': (270, 360), 'lat': (37.37, 37.53), \
                     'lon': (-122.25, -122.05), 'alt': (2700, 6000), \
                     'vrate': (-6000, -50)}
    sfo_approach_DUMBA_conds = {'track': (270, 325), 'lat': (37.5, 37.58), \
                     'lon': (-122.125, -122.06), 'alt': (3400, 6000), \
                     'vrate': (-6000, -50)}
    sfo_depart_mid_W_conds = {'track': (280, 360), 'lat': (37.63, 37.72), \
                      'lon': (-122.45, -122.25), 'alt': (100, 10000), \
                      'vrate': (50, 7000)}
    sfo_depart_mid_E_conds = {'track': (0, 90), 'lat': (37.63, 37.72), \
                      'lon': (-122.45, -122.25), 'alt': (100, 10000), \
                      'vrate': (50, 7000)}
    sfo_depart_W_conds = {'track': (280, 320), 'lat': (37.62, 37.69), \
                     'lon': (-122.54, -122.37), 'alt': (1000, 4500), \
                     'vrate': (100, 5000)}
    sjc_approach_SE_conds = {'track': (290, 350), 'lat': (37.3, 37.35), \
                     'lon': (-121.9, -121.85), 'alt': (10, 2000), \
                     'vrate': (-5000, -50)}
    sjc_depart_SE_conds = {'track': (100, 170), 'lat': (37.3, 37.34), \
                      'lon': (-121.9, -121.85), 'alt': (1800, 10000), \
                      'vrate': (100, 5000)}
    sjc_approach_NW_conds = {'track': (110, 170), 'lat': (37.37, 37.42), \
                      'lon': (-121.98, -121.92), 'alt': (10, 3000), \
                      'vrate': (-5000, -50)}
    sjc_depart_NW_conds = {'track': (280, 360), 'lat': (37.38, 37.42), \
                      'lon': (-122, -121.93), 'alt': (800, 6000), \
                      'vrate': (100, 5000)}
    sjc_depart_NW_SE_conds = {'track': (120, 160), 'lat': (37.4, 37.47), \
                      'lon': (-121.97, -121.85), 'alt': (3000, 7000), \
                      'vrate': (100, 5000)}
    pao_SE_pao_arr_conds = {'track': (280, 360), 'lat': (37.43, 37.46), \
                     'lon': (-122.11, -122.08), 'alt': (0, 1500), \
                     'vrate': (-5000, -50)}
    pao_SE_pao_dep_conds = {'track': (1135, 170), 'lat': (37.43, 37.46), \
                     'lon': (-122.11, -122.08), 'alt': (100, 3000), \
                     'vrate': (50, 5000)}
    pao_NW_pao_arr_conds = {'track': (100, 170), 'lat': (37.45, 37.49), \
                     'lon': (-122.14, -122.11), 'alt': (0, 1500), \
                     'vrate': (-5000, -50)}
    pao_NW_pao_dep_conds = {'track': (300, 360), 'lat': (37.45, 37.49), \
                     'lon': (-122.14, -122.11), 'alt': (0, 1500), \
                     'vrate': (50, 2000)}
    pao_Bay_pao_arr_conds = {'track': (0, 360), 'lat': (37.44, 37.49), \
                     'lon': (-122.13, -122.08), 'alt': (0, 1000), \
                     'vrate': (-5000, -50)}
    pao_Bay_pao_dep_conds = {'track': (0, 360), 'lat': (37.44, 37.49), \
                     'lon': (-122.13, -122.09), 'alt': (10, 2000), \
                     'vrate': (50, 3000)}
    sql_SE_sql_arr_conds = {'track': (280, 340), 'lat': (37.48, 37.52), \
                     'lon': (-122.25, -122.2), 'alt': (0, 2000), \
                     'vrate': (-5000, -50)}
    sql_SE_sql_dep_conds = {'track': (100, 160), 'lat': (37.48, 37.52), \
                     'lon': (-122.25, -122.2), 'alt': (0, 4000), \
                     'vrate': (50, 5000)}
    sql_NW_sql_arr_conds = {'track': (100, 160), 'lat': (37.51, 37.54), \
                     'lon': (-122.27, -122.25), 'alt': (0, 1500), \
                     'vrate': (-5000, -50)}
    sql_NW_sql_dep_conds = {'track': (270, 360), 'lat': (37.51, 37.54), \
                     'lon': (-122.28, -122.25), 'alt': (0, 2000), \
                     'vrate': (50, 5000)}
    sql_Bair_sql_arr_conds = {'track': (20, 340), 'lat': (37.49, 37.54), \
                     'lon': (-122.26, -122.21), 'alt': (0, 2000), \
                     'vrate': (-5000, -50)}
    sql_Bair_sql_dep_conds = {'track': (20, 340), 'lat': (37.49, 37.54), \
                     'lon': (-122.26, -122.21), 'alt': (0, 3000), \
                     'vrate': (100, 6000)}
    nuq_approach_SE_conds = {'track': (320, 360), 'lat': (37.36, 37.39), \
                     'lon': (-122.04, -122.02), 'alt': (0, 3000), \
                     'vrate': (-5000, -50)}
    nuq_depart_NW_conds = {'track_hi': (320, 360), 'track_low': (0, 80), \
                     'lat': (37.42, 37.46), 'lon': (-122.07, -122.03), \
                     'alt': (1000, 4000), 'vrate': (0, 5000)}
    oak_SE_oak_arr_conds = {'track': (280, 360), 'lat': (37.64, 37.68), \
                     'lon': (-122.18, -122.14), 'alt': (0, 3000), \
                     'vrate': (-5000, -50)}
    oak_SE_sfo_dep_conds = {'track': (40, 80), 'lat': (37.7, 37.74), \
                     'lon': (-122.21, -122.15), 'alt': (4500, 8000), \
                     'vrate': (2000, 6000)}
    oak_SE_hwd_arr_conds = {'track': (270, 360), 'lat': (37.64, 37.72), \
                     'lon': (-122.15, -122.12), 'alt': (0, 3000), \
                     'vrate': (-5000, 100)}
    oak_SE_hwd_dep_conds = {'track': (0, 270), 'lat': (37.62, 37.72), \
                     'lon': (-122.15, -122.12), 'alt': (0, 3000), \
                     'vrate': (-5000, 100)}
    oak_NW_oak_dep_conds = {'track': (260, 360), 'lat': (37.72, 37.8), \
                     'lon': (-122.37, -122.26), 'alt': (500, 8000), \
                     'vrate': (400, 5000)}
    oak_NW_sfo_dep_conds = {'track': (260, 360), 'lat': (37.72, 37.8), \
                     'lon': (-122.37, -122.26), 'alt': (500, 8000), \
                     'vrate': (400, 5000)}
    hwd_SE_hwd_arr_conds = {'track': (260, 360), 'lat': (37.64, 37.67), \
                     'lon': (-122.12, -122.07), 'alt': (0, 1100), \
                     'vrate': (-5000, -50)}
    hwd_SE_hwd_dep_conds = {'track': (80, 180), 'lat': (37.62, 37.67), \
                     'lon': (-122.12, -122.07), 'alt': (1100, 3000), \
                     'vrate': (20, 4000)}
    hwd_SE_oak_arr_conds = {'track': (260, 360), 'lat': (37.62, 37.645), \
                     'lon': (-122.13, -122.07), 'alt': (1500, 3500), \
                     'vrate': (-5000,-50)}
    hwd_W_hwd_arr_conds = {'track': (270, 360), 'lat': (37.6, 37.67), \
                     'lon': (-122.13, -122.05), 'alt': (0, 1000), \
                     'vrate': (-5000, -50)}
    hwd_W_oak_arr_conds = {'track': (280, 360), 'lat': (37.64, 37.67), \
                     'lon': (-122.14, -122.12), 'alt': (1000, 3000), \
                     'vrate': (-5000, -50)}
    rhv_S_rhv_arr_conds = {'track': (300, 360), 'lat': (37.29, 37.38), \
                     'lon': (-121.82, -121.74), 'alt': (0, 3000), \
                     'vrate': (-5000, -50)}
    rhv_S_rhv_dep_conds = {'track': (120, 170), 'lat': (37.26, 37.38), \
                     'lon': (-121.82, -121.74), 'alt': (0, 3000), \
                     'vrate': (50, 1500)}
    rhv_S_sjc_arr_conds = {'track': (300, 360), 'lat': (37.27, 37.34), \
                     'lon': (-121.9, -121.83), 'alt': (0, 3000), \
                     'vrate': (-5000, -50)}
    rhv_S_sjc_dep_conds = {'track': (120, 150), 'lat': (37.26, 37.34), \
                     'lon': (-121.9, -121.82), 'alt': (2000, 7000), \
                     'vrate': (1000, 5000)}
    rhv_N_rhv_arr_conds = {'track': (120, 160), 'lat': (37.34, 37.38), \
                     'lon': (-121.84, -121.80), 'alt': (0, 2500), \
                     'vrate': (-5000, -50)}
    rhv_N_rhv_dep_conds = {'track': (300, 360), 'lat': (37.33, 37.38), \
                     'lon': (-121.84, -121.80), 'alt': (0, 4000), \
                     'vrate': (50, 1000)}
    rhv_N_sjc_arr_conds = {'track': (300, 360), 'lat': (37.28, 37.35), \
                     'lon': (-121.93, -121.85), 'alt': (0, 2000), \
                     'vrate': (-5000, -50)}
    rhv_N_sjc_dep_conds = {'track': (120, 160), 'lat': (37.28, 37.36), \
                     'lon': (-121.93, -121.84), 'alt': (2000, 5000), \
                     'vrate': (500, 5000)}
    sumed_dep_conds = {'track': (0, 360), 'lat': (37.43, 37.445), \
                     'lon': (-122.187, -122.17), 'alt': (25, 1500), \
                     'vrate': (20, 1500)}
    sumed_arr_conds = {'track': (0, 360), 'lat': (37.42, 37.446), \
                     'lon': (-122.187, -122.10), 'alt': (0, 900), \
                     'vrate': (-1500, 0)}
    vmced_dep_conds = {'track': (0, 360), 'lat': (37.31, 37.32), 
                     'lon': (-121.94, -121.93), 'alt': (20, 900), 
                     'vrate': (20, 1200)}
    vmced_arr_conds = {'track': (0, 360), 'lat': (37.31, 37.32), 
                     'lon': (-121.94, -121.93), 'alt': (20, 900), 
                     'vrate': (-1500, 0)}
    
    # Here we break out the components of the rca_data tuple
#    rca_d, rca_t, rca_lat, rca_lon, rca_f, rca_alt, rca_ang, rca_speed, \
#        rca_trk, rca_snd_arr, rca_gnd_dist, rca_sel, rca_vert_rate = rca_data
    
    # Now make an approach/depart decision based on case criteria. These are
    # the airports we currently analyze:
    # ('SFO Bay', 'SFO N', 'SFO W', 'SJC SE',
    # 'SJC Depart NW', 'PAO SE', 'PAO Depart NW')

    if airport_obs_name == 'SFO Bay':
        # Here we check the bay (NW) approach to SFO
        if apply_conditions(sfo_approach_bay_conds, rca_data) == True:
            return(('to', 'KSFO'))
        else:
            return(()) # Not an approach rca
        # End if airport_obs_name == ...
    
    if airport_obs_name == 'SFO SIDBY':
        # Here we check the flights over SIDBY approach to SFO
        if apply_conditions(sfo_approach_SIDBY_conds, rca_data) == True:
            return(('to', 'KSFO'))
        else:
            return(()) # Not an approach rca
        # End if airport_obs_name == ...
    
    if airport_obs_name == 'SFO DUMBA':
        # Here we check the flights over DUMBA approach to SFO
        if apply_conditions(sfo_approach_DUMBA_conds, rca_data) == True:
            return(('to', 'KSFO'))
        else:
            return(()) # Not an approach rca
        # End if airport_obs_name == ...
    
    elif airport_obs_name == 'SFO N':
        # Here we check the n-branch (N & NNE & NE) bay departures from SFO
        if apply_conditions(sfo_depart_mid_W_conds, rca_data) == True:
            return(('from', 'KSFO'))
        elif apply_conditions(sfo_depart_mid_E_conds, rca_data) == True:
            return(('from', 'KSFO'))
        else:
            return(()) # Not an approach rca
        # End if airport_obs_name == ...
    
    elif airport_obs_name == 'SFO W':
        # Here we check the W departures from SFO
        if apply_conditions(sfo_depart_W_conds, rca_data) == True:
            return(('from', 'KSFO'))
        else:
            return(()) # Not an approach rca
        # End if airport_obs_name == ...
    
    elif airport_obs_name == 'SJC SE':
        # Here we check the SE approach to SJC
        if apply_conditions(sjc_approach_SE_conds, rca_data) == True:
            return(('to', 'KSJC'))
        elif apply_conditions(sjc_depart_SE_conds, rca_data) == True:
            return(('from', 'KSJC'))
        else:
            return(()) # Not an approach rca
        # End if airport_obs_name == ...
    
    elif airport_obs_name == 'SJC NW':
        # Here we check the NW approach to SJC
        if apply_conditions(sjc_approach_NW_conds, rca_data) == True:
            return(('to', 'KSJC'))
        elif apply_conditions(sjc_depart_NW_conds, rca_data) == True:
            return(('from', 'KSJC'))
        elif apply_conditions(sjc_depart_NW_SE_conds, rca_data) == True:
            return(('from', 'KSJC'))
        else:
            return(()) # Not a approach rca
        # End if airport_obs_name == ...
    
    elif airport_obs_name == 'PAO SE':
        # Here we check the SE approach to PAO
        if apply_conditions(pao_SE_pao_arr_conds, rca_data) == True:
            return(('to', 'KPAO'))
        elif apply_conditions(pao_SE_pao_dep_conds, rca_data) == True:
            return(('from', 'KPAO'))
        else:
            return(()) # Not an approach rca
        # End if airport_obs_name == ...
    
    elif airport_obs_name == 'PAO NW':
        # Here we check the NW departure from PAO
        if apply_conditions(pao_NW_pao_arr_conds, rca_data) == True:
            return(('to', 'KPAO'))
        elif apply_conditions(pao_NW_pao_dep_conds, rca_data) == True:
            return(('from', 'KPAO'))
        else:
            return(()) # Not an approach rca
        # End if airport_obs_name == ...
    
    elif airport_obs_name == 'PAO Bay':
        # Here we check the NW departure from PAO
        if apply_conditions(pao_Bay_pao_arr_conds, rca_data) == True:
            return(('to', 'KPAO'))
        elif apply_conditions(pao_Bay_pao_dep_conds, rca_data) == True:
            return(('from', 'KPAO'))
        else:
            return(()) # Not an approach rca
        # End if airport_obs_name == ...
    
    elif airport_obs_name == 'SQL SE':
        # Here we check the SE approach to PAO
        if apply_conditions(sql_SE_sql_arr_conds, rca_data) == True:
            return(('to', 'KSQL'))
        elif apply_conditions(sql_SE_sql_dep_conds, rca_data) == True:
            return(('from', 'KSQL'))
        else:
            return(()) # Not an approach rca
        # End if airport_obs_name == ...
    
    elif airport_obs_name == 'SQL NW':
        # Here we check the NW departure from PAO
        if apply_conditions(sql_NW_sql_arr_conds, rca_data) == True:
            return(('to', 'KSQL'))
        elif apply_conditions(sql_NW_sql_dep_conds, rca_data) == True:
            return(('from', 'KSQL'))
        else:
            return(()) # Not an approach rca
        # End if airport_obs_name == ...
    
    elif airport_obs_name == 'SQL Bair':
        # Here we check the NW departure from PAO
        if apply_conditions(sql_Bair_sql_arr_conds, rca_data) == True:
            return(('to', 'KSQL'))
        elif apply_conditions(sql_Bair_sql_dep_conds, rca_data) == True:
            return(('from', 'KSQL'))
        else:
            return(()) # Not an approach rca
        # End if airport_obs_name == ...
    
    elif airport_obs_name == 'NUQ SE':
        # Here we check the NW departure from PAO
        if apply_conditions(nuq_approach_SE_conds, rca_data) == True:
            return(('to', 'KNUQ'))
        else:
            return(()) # Not an approach rca
        # End if airport_obs_name == ...
    
    elif airport_obs_name == 'NUQ NW':
        # Here we check the NW departure from PAO
        if apply_conditions(nuq_depart_NW_conds, rca_data) == True:
            return(('from', 'KNUQ'))
        else:
            return(()) # Not a depart rca
        # End if airport_obs_name == ...
    
    elif airport_obs_name == 'OAK SE':
        # Here we check the SE approach to KOAK
        if apply_conditions(oak_SE_oak_arr_conds, rca_data) == True:
            return(('to', 'KOAK'))
        elif apply_conditions(oak_SE_sfo_dep_conds, rca_data) == True:
            return(('from', 'KSFO'))
        elif apply_conditions(oak_SE_hwd_arr_conds, rca_data) == True:
            return(('to', 'KHWD'))
        elif apply_conditions(oak_SE_hwd_dep_conds, rca_data) == True:
            return(('from', 'KHWD'))
        else:
            return(()) # Not an approach rca
        # End if airport_obs_name == ...
    
    elif airport_obs_name == 'OAK NW':
        # Here we check the NW departure from KOAK
        if apply_conditions(oak_NW_oak_dep_conds, rca_data) == True:
            return(('from', 'KOAK'))
        elif apply_conditions(oak_NW_sfo_dep_conds, rca_data) == True:
            return(('from', 'KSFO'))
        else:
            return(()) # Not a depart rca
        # End if airport_obs_name == ...
    
    elif airport_obs_name == 'HWD SE':
        # Here we check the SE approach to KOAK
        if apply_conditions(hwd_SE_hwd_arr_conds, rca_data) == True:
            return(('to', 'KHWD'))
        elif apply_conditions(hwd_SE_hwd_dep_conds, rca_data) == True:
            return(('from', 'KHWD'))
        elif apply_conditions(hwd_SE_oak_arr_conds, rca_data) == True:
            return(('to', 'KOAK'))
        else:
            return(()) # Not an approach rca
        # End if airport_obs_name == ...
    
    elif airport_obs_name == 'HWD W':
        # Here we check the NW departure from KOAK
        if apply_conditions(hwd_W_hwd_arr_conds, rca_data) == True:
            return(('to', 'KHWD'))
        elif apply_conditions(hwd_W_oak_arr_conds, rca_data) == True:
            return(('to', 'KOAK'))
        else:
            return(()) # Not a depart rca
        # End if airport_obs_name == ...
    
    elif airport_obs_name == 'RHV S':
        # Here we check the SE approach to KOAK
        if apply_conditions(rhv_S_rhv_arr_conds, rca_data) == True:
            return(('to', 'KRHV'))
        elif apply_conditions(rhv_S_rhv_dep_conds, rca_data) == True:
            return(('from', 'KRHV'))
        elif apply_conditions(rhv_S_sjc_arr_conds, rca_data) == True:
            return(('to', 'KSJC'))
        elif apply_conditions(rhv_S_sjc_dep_conds, rca_data) == True:
            return(('from', 'KSJC'))
        else:
            return(()) # Not an approach rca
        # End if airport_obs_name == ...
    
    elif airport_obs_name == 'RHV N':
        # Here we check the NW departure from KOAK
        if apply_conditions(rhv_N_rhv_arr_conds, rca_data) == True:
            return(('to', 'KRHV'))
        elif apply_conditions(rhv_N_rhv_dep_conds, rca_data) == True:
            return(('from', 'KRHV'))
        elif apply_conditions(rhv_N_sjc_arr_conds, rca_data) == True:
            return(('to', 'KSJC'))
        elif apply_conditions(rhv_N_sjc_dep_conds, rca_data) == True:
            return(('from', 'KSJC'))
        else:
            return(()) # Not a depart rca
        # End if airport_obs_name == ...
    
    elif airport_obs_name == 'SUMED':
        # Here we check the NW departure from KOAK
        if apply_conditions(sumed_arr_conds, rca_data) == True:
            return(('to', 'SUMED'))
        elif apply_conditions(sumed_dep_conds, rca_data) == True:
            return(('from', 'SUMED'))
        else:
            return(()) # Not a depart rca
        # End if airport_obs_name == ...
    
    elif airport_obs_name == 'VMCED':
        # Here we check the NW departure from KOAK
        if apply_conditions(vmced_arr_conds, rca_data) == True:
            return(('to', 'VMCED'))
        elif apply_conditions(vmced_dep_conds, rca_data) == True:
            return(('from', 'VMCED'))
        else:
            return(()) # Not a depart rca
        # End if airport_obs_name == ...
    
    else: # Cannot recognize the airport/direction here
        print('Check_Airport: cannot recognize {0}'.format(airport_obs_name))
        return(()) # End of possibilities, return null
    # End if airport_obs_name in ('some known category'):

#End def check_airport(airport_obs_name, rca_data):


# =============================================================================
# This routine expects a tuple for an approach or departure from a subject
# airport ('to' or 'from', airport ID), and looks for the place in the master
# sighting structure (corresponding to segment_id in the filtered sighting 
# data) to update the airport information for a flight segment
# =============================================================================

def update_airport_info(r_set_m, chk_tple, segment_id):
    # split out the chk_tple content
    orig_or_dest, airport_code = chk_tple
    
    # Find the segment index in the master sighting list (r_set_m)
    j_seg_m_hit = -1 # Init index we are looking for
    for j_seg_m in range(1, len(r_set_m)):
        if r_set_m[j_seg_m][0]['segment'] == segment_id:
            j_seg_m_hit = j_seg_m # Found it, note it & quit
            break
        # End if r_set_m[j_seg_m][0]['segment']...
    # End for j_seg_m in...
    
    # Check for an error
    if j_seg_m_hit == -1: # If no hit found, bad news
        print('Fatal error, cannot find segment {0} in {1}' \
              .format(segment_id, r_set_m))
        sys.exit() # BUGHLT
    # End if j_seg_m_hit == -1
    
    # Here we can find the master segment, update the master airport data
    if orig_or_dest == 'to':
        if r_set_m[j_seg_m_hit][0]['destination'] == 'unknown':
            r_set_m[j_seg_m_hit][0]['destination'] = airport_code
        # End if r_set_m[j_seg_m_hit][0]['destination'] != 'unknown':
    else:
        if r_set_m[j_seg_m_hit][0]['origin'] == 'unknown':
            r_set_m[j_seg_m_hit][0]['origin'] = airport_code
        # End if r_set_m[j_seg_m_hit][0]['origin'] != 'unknown':
    # End if orig_or_dest == 'to':
    
    return()
# End def update_airport_info
    

# =============================================================================
# This program reads assembled and filtered FlightAware sighting data and
# outputs a tab-separated (Excel-compatible) file of closest approach
# parameters for flight sightings close to a given observation location. We
# assume the input json file of sightings is grouped in sequence according to
# flight ICAO ids. Output file names use a base string input by the user with
# the form path/name-stem.yymmdd.

#obs_list = [('SJC Depart NW-SE', 37.394070, -121.972794, 0)] # Offset from path

obs_list = [('SFO Bay', 37.571794, -122.240496, 0),
            ('SFO SIDBY', 37.450711, -122.144722, 0),
            ('SFO DUMBA', 37.503517, -122.096147, 0),
            ('SFO N', 37.655673, -122.350902, 0),
            ('SFO W', 37.649624, -122.444802, 0),
            ('SJC SE', 37.319608, -121.880048, 0),
            ('SJC NW', 37.397808, -121.963053, 0),
            ('PAO SE', 37.443466, -122.097752, 0),
            ('PAO NW', 37.465845, -122.120131, 0),
            ('PAO Bay', 37.463661, -122.097795, 0),
            ('SQL SE', 37.496174, -122.231122, 0),
            ('SQL NW', 37.526063, -122.265626, 0),
            ('SQL Bair', 37.521547, -122.224567, 0),
            ('NUQ SE', 37.371766, -122.026278, 0),	
            ('NUQ NW', 37.428937, -122.055723, 0),
            ('OAK SE', 37.667875, -122.147847, 0),
            ('OAK NW', 37.759685, -122.272565, 0),
            ('HWD SE', 37.653828, -122.094216, 0),
            ('HWD W', 37.651970, -122.128001, 0),
            ('RHV S', 37.312846, -121.816957, 0),
            ('RHV N', 37.341785, -121.839960, 0),
            ('SUMED', 37.433875, -122.174511, 0),
            ('VMCED', 37.313718, -121.934491, 0)]

# These are the paths to the input assembled sighting file and the output
# file with updated airport origin/destination information
path_in = '/Users/aditeyashukla/Downloads/tcr-python-expts/'
#path_out = 'C:/Users/TCR/Dropbox/FlightAware/Data Sets by Date'
file_name_stem = 'FA_Sightings.'
obs_folder = 'Airport to-from'


# Definition of nearness (miles from observation point) and altitude limits
# (ft) for considering tracks when computing closest approach
dmax = 5 # Max allowed ground distance (mi) from observation point
altmax = 10000 # Definition of maximum altitude allowed (ft) for rca
altmin = 10 # Minimum altitude allowed (ft)

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
print ('Program to add airport to/from data for {0} into an assembled' \
       ' sighting set'.format(str(target_tuple)))

# Now compute the bounding dates for the day in UNIX epoch format
target_date_st = tt.mktime(target_tuple.timetuple()) # UNIX version
target_date_end = target_date_st + 24 * 3600 # UNIX version
target_date_str = ut.datetime.fromtimestamp(target_date_st). \
                    strftime('%Y%m%d')[2 :]

print('Date: {0}; Start: {1}, End: {2}'.format(target_date_str, \
          str(round(target_date_st, 1)), str(round(target_date_end, 1))))

# Now make the input file name and see if it is there
io_file_stem = os.path.join(path_in, target_date_str, file_name_stem + \
                      target_date_str).replace('\\', '/')
ofile_name0 = io_file_stem
obs_ofile_name0 = os.path.join(path_in, target_date_str, obs_folder, \
                       file_name_stem + target_date_str).replace('\\', '/')
json_file_list = ll.glob(io_file_stem + '.json.txt')
if json_file_list == []: # Quit if nothing found
    print('No sighting json file found for {0}'.format(target_date_str))
    sys.exit()
else:
    json_filez = json_file_list[0]
# End if json_file_list == []

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
#   {"icao": "value", "tail #": "value", "ac_type": "value",
#    "#_segments": value}
# Each {Segment data-i} contains info about the next flight segment. For a
# given icao, segments are separated from the input sighting stream by gaps
# much longer than the sighting interval:
#   {"segment": #, "gap": len, "segment_start": epoch time, "segment_end":
#       epoch time, "flight": "id", "#_sightings": #, 
#       "gps_max": [37.598101, -122.013802],
#       "gps_min": [37.108278, -122.330375],
#       "origin": "unknown", "destination": "unknown"}
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
# Now work to set the expected time between sighting sets (sec)

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

# Now we read in a master copy of the sighting data json file. This will be
# used to store permanent changes to the json file, i.e., the to/from airports
# for various sighting segments as they are detected. After all the processing
# this master file will be written to parallel the raw sighting file.
with open(json_filez, 'r') as f_in:
    master_struct = json.loads(f_in.read())
    f_in.close() # Done reading this file
# This is the full master source of sighting details
master_buffer = master_struct['aircraft']
# In order to change the content of any flight segment meta information in the
# master data structure, the indexing is as follows:
#  master_buffer['icao #'][1 - seg sets][n - seg #][0 - seg meta]['dict index']
# In particular, in this analysis, we will update values for "origin": and
# "destination": in the segment meta information

# Here at the top level we loop through the observation points
for i_obs in range(len(obs_list)):
    # Set up some params for this observation point
    name_obs, lat_obs, lon_obs, elev_obs = obs_list[i_obs] # Split out obs data
    obs_pt = (lat_obs, lon_obs)
    obs_pt_r = (lat_obs, lon_obs, elev_obs)
    name_obs_nosp = '.' + name_obs.replace(' ', '_') # Form for file names
    start_time = tt.time() # Note start time for this observer
    n_to = n_from = 0 # Init counters for this observation pt
    
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
    log_str = 'Log data for discarded tracks\n\n'
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
    with open(json_filez, 'r') as f_in:
        f_struct = json.loads(f_in.read()) # f_struct contains unpacked file
        f_in.close() # Done reading this file
    # This is the full source of sighting details
    data_buffer = f_struct['aircraft']
    data_edit, log_str = tcr.screen_sighting_data(data_buffer, obs_pt_r, \
                              (target_date_st, target_date_end), dmax, \
                              (altmin, altmax), [], log_str)
    
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
    # Loop through the icao keys to format sighting data for printing
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
            airport_name = 'Unknown' # Init airport name for this segment
            
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
                # End if pca_trend <= 0:
                
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
                
                # Format and output last rca data (w/o trailing \n)
                rca_str += tcr.fmt_rca_str(i_icao, flight_id, \
                                   segment_id, min_rca)[: -2]
                
                # Here we check to see if this is an approach/departure for
                # one of the local airports
                chk_tple = check_airport(name_obs, min_rca)
                if chk_tple != (): # If OK, update the airport info in master
                    r_set_m = master_buffer[i_icao]
                    update_airport_info(r_set_m, chk_tple, segment_id)
                    dir_type, airport_name = chk_tple
                    if dir_type == 'to':
                        n_to += 1 # Count arrivals
                    else:
                        n_from += 1 # And departures
                # End if chk_tple != ():
                
                # Add local airport name to rca_str output
                rca_str += '\tlocal airport {0}\n'.format(airport_name)
                
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
                    
                    # Finish formating and output the rca data for this valley
                    rca_str += tcr.fmt_rca_str(i_icao, flight_id, \
                                       segment_id, min_rca)[: -2]
                    
                    # Here we check to see if this is an approach/departure for
                    # one of the local airports
                    chk_tple = check_airport(name_obs, min_rca)
                    if chk_tple != (): # If OK, update airport info in master
                        r_set_m = master_buffer[i_icao]
                        update_airport_info(r_set_m, chk_tple, segment_id)
                        dir_type, airport_name = chk_tple
                        if dir_type == 'to':
                            n_to += 1 # Count arrivals
                        else:
                            n_from += 1 # And departures
                    # End if chk_tple != ():
                    
                    # Add local airport name to rca_str output
                    rca_str += '\tlocal airport {0}\n'.format(airport_name)
                    
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
            
            # Format and output last rca data
            rca_str += tcr.fmt_rca_str(i_icao, flight_id, \
                               segment_id, min_rca)[: -2]
            
            # Here we check to see if this is an approach/departure for
            # one of the local airports
            chk_tple = check_airport(name_obs, min_rca)
            if chk_tple != (): # If OK, update the airport info in master
                r_set_m = master_buffer[i_icao]
                update_airport_info(r_set_m, chk_tple, segment_id)
                dir_type, airport_name = chk_tple
                if dir_type == 'to':
                    n_to += 1 # Count arrivals
                else:
                    n_from += 1 # And departures
            # End if chk_tple != ():
            
            # Add local airport name to rca_str output
            rca_str += '\tlocal airport {0}\n'.format(airport_name)
            
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
            
            # Format and output last rca data
            rca_str += tcr.fmt_rca_str(i_icao, flight_id, \
                               segment_id, min_rca)[: -2]
            
            # Here we check to see if this is an approach/departure for
            # one of the local airports
            chk_tple = check_airport(name_obs, min_rca)
            if chk_tple != (): # If OK, update the airport info in master
                r_set_m = master_buffer[i_icao]
                update_airport_info(r_set_m, chk_tple, segment_id)
                dir_type, airport_name = chk_tple
                if dir_type == 'to':
                    n_to += 1 # Count arrivals
                else:
                    n_from += 1 # And departures
            # End if chk_tple != ():
            
            # Add local airport name to rca_str output
            rca_str += '\tlocal airport {0}\n'.format(airport_name)
            
            # Update the running SEL sums for DNL calculations
            dnl_tuple = tcr.dnl_sums(dnl_tuple, rca_sel, rca_t - tmin)
            # The update the overflight counts
            oflght_cnts = tcr.ovflght_cnts(oflght_cnts, rca_gnd_dist, \
                                           rca_t - tmin, ref_dist)
            
#            continue # Move on to the next segment
            
        # End for j_seg in range(1, len(r_set)):
    
    # End for i_icao loop -- data for next icao key
    
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
    ofile_name = obs_ofile_name0 + name_obs_nosp +'.rca.txt'
    with open(ofile_name, 'w') as f_out:
        f_out.write(rca_str)
        f_out.close # Done, close ouput file
    
    # Make the log file name and write what we have
    ofile_name = obs_ofile_name0 + name_obs_nosp + '.log.txt'
    with open(ofile_name, 'w') as f_out:
        f_out.write(log_str)
        f_out.close # Done, close ouput file
    
    end_time = tt.time() # Note end time for this observer
    print('Done computing rcas for {0}, {1} arrivals, {2} departures  '\
              '({3} seconds)'.format(name_obs, str(n_to), str(n_from), \
                round(end_time - start_time, 1)))

# End for i_obs

# Make the master json file name and write what we have changed
json_filez_out = ofile_name0 + '.airport_ids.json.txt'
with open(json_filez_out, 'w') as f_out:
    json.dump(master_struct, f_out)
    f_out.write('\n')
    f_out.close # Done, close ouput file

print('\nDone computing rcas for all observation points')
