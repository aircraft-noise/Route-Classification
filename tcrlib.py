# -*- coding: utf-8 -*-
"""
Created on Mon Aug 28 14:49:25 2017

@author: TCR

Library of various routines useful in collecting and analyzing FlightAware
data.
"""
#import os
import sys
import math
import datetime as ut
#from datetime import timezone
import calendar as cal
import platform as pf
import time as tt
#import operator as op 
#from copy import deepcopy
import copy as cpy
#import socket as skt
import json
#import multiprocessing
#import subprocess

#%% =============================================================================
#  Function to filter raw FlightAware feeder live data and historical data
# =============================================================================
def filter_rec(json_rec, st_time, loc0, max_dist, feeder_id):
# =============================================================================
# The following attributes are required for filtering aircraft records:
# ['hex','flight','lat','lon','seen_pos','altitude','vert_rate','track','speed']
# In addition, 'altitude' must not be 'ground'. The record is transformed to a
# "standard" form in the order above.
# =============================================================================

    rec_labels = ['hex','flight','lat','lon','distance','seen_pos', \
                  'altitude','vert_rate','track','speed','feeder_id']
    rec_ret = {}
    lat0, lon0 = loc0
    
    x = json_rec
    # If "altitude", "lat", or "lon" are not in the record, return nil
    # New Dump1090: altitude = alt_baro (barometric altitude), or alt_geom
    # (GPS altitude); gs = speed; vert_rate = baro_rate (barometric vertical
    # rate), or geom_rate (GPS vertical rate)
    # If 'altitude' in x and 'lat' in x and 'lon' in x; assume dump1090 version
    # 0. If 'alt_baro' in x or 'alt_geom' in x and 'lat' in x and 'lon' in x;
    # assume dump1090 version 1:
    if 'altitude' in x and 'lat' in x and 'lon' in x:
        dump1090_v = 0 # Assume old dump1090 version here
    elif ('alt_baro' in x or 'alt_geom' in x) and 'lat' in x and 'lon' in x:
        dump1090_v = 1 # Assume new dump1090 version here
    else:
        return({}) # Bomb if essentials not present
    # End if 'altitude' in x ... elif...
    
    if dump1090_v == 1: # If new dump1090 version, convert to old key set
        if 'alt_geom' in x:
            x.update({'altitude': x['alt_geom']})
        else:
            x.update({'altitude': x['alt_baro']})
        # End if 'alt_geom' in x:
        
        if 'gs' in x:
            x.update({'speed': x['gs']}) # Set ground speed
        elif x['altitude'] == 'ground':
            x.update({'speed': 0}) # Set fake ground speed
        else:
#            print('gs key missing in: ', x)
            return({}) # Bomb if not present
        # End if 'gs' in x:
        
        # Try to use one of the vertical rate indicators
        if 'geom_rate' in x:
            x.update({'vert_rate': x['geom_rate']})
        elif 'baro_rate' in x:
            x.update({'vert_rate': x['baro_rate']})
        else:
            x.update({'vert_rate': 0})
#            print('geom_rate and baro_rate missing in: ', x)
            return({}) # If neither, bomb
        # End if 'geom_rate' in x:... elif...
    # End if dump1090_v == 1:
    
    # Now do common house cleaning...
    # If 'flight' key not present, add key with value 'Other'   
    if 'flight' not in x:
        x.update({'flight': 'Other'})
    # End if 'flight' not in x:
    
    # Add 'distance' field with default value 0
    x.update({'distance': 0})
    
    # Add feeder ID field
    x.update({'feeder_id': feeder_id})
    
    # Now check for all essential fields (old key set)
    for i_rec in rec_labels:
        if i_rec not in x: # If not present
            return({}) # Return null record
        else: # add its value to the return record
            rec_ret.update({i_rec: x[i_rec]})
    
    # Check if track point is too far from reference location
    dist = round(sph_distance((rec_ret['lat'], rec_ret['lon']), \
                                 (lat0, lon0)), 2)
    if max_dist > 0 and dist > max_dist: # If too far, bag it
        return({})
    else:
        rec_ret['distance'] = dist # Otherwise update the 0 entry
    # End if
    
    # Finally, update observation time based on interval to last seen
    rec_ret['seen_pos'] = round(st_time - rec_ret['seen_pos'], 1)
    
    return(rec_ret) # All done
# End def filter_rec


#%% =============================================================================
# "origin" and "destination" are "(lat (φ), long (λ))" pairs in degrees
# a = sin²(Δφ/2) + cos φ1 * cos φ2 * sin²(Δλ/2)
# c = 2 * asin(min(1, √a))
# d = radius * c
# =============================================================================
def sph_distance(origin, destination):
    # Convert lat/lon to radians and split out lat/lon
    lat1, lon1 = tuple(math.radians(p) for p in origin)
    lat2, lon2 = tuple(math.radians(p) for p in destination)
#    radius = 6369 # km
    radius = 3957.5 # mi
#    radius = 3439 # nm

    dlat = lat2-lat1
    dlon = lon2-lon1
    a = math.sin(dlat/2)**2 + \
        math.cos(lat1) * math.cos(lat2) * math.sin(dlon/2)**2
    c = 2 * math.asin(min(1, math.sqrt(a)))
    d = radius * c

    return(d)
# End def sph_distance


#%% =============================================================================
# The "closest approach" function, rca, for aircraft flight paths takes
# quartets of information specifying three points: two along the flight path
# and one a fixed observation point (presumably) off the flight path. Each of
# the points is characterized by a list (time, lat, long, altitude (ft)). The
# function returns a list for the point along the path which corresponds to
# the point of closest approach to the observation point (rca, t_rca, d_1_rca,
# alt_rca), where d_1_rca is the fractional distance between point 1 and point
# 2 where the rca is located. If the flight_pt1 or flight_pt2 tuple is empty,
# we just return a data set equal to the point supplied
# =============================================================================
def rca(flight_pt1, flight_pt2, obs_pt, obs_elev):
    radius = 3957.5 # Earth's radius in mi
    ft_in_mile = 5280 # Number of feet in a mile
    lat_obs, lon_obs = obs_pt
    # Compute the vector to the observation point
    pt_obs_scale = 1 + obs_elev/(ft_in_mile * radius) # And for obs pt
    pt_obs_cart = tuple(pt_obs_scale*p for p in cart_vector(obs_pt))
    
    # Check for special cases of no flight_ptn
    if flight_pt1 == () and flight_pt2 == (): # This is fatal news
        print ('Error in rca fct call, both arguments are null')
        return(()) # Return a null tuple
    elif flight_pt1 == (): # if flight_pt1 null, treat flight_pt2 as normal
        # Here we just return flight_pt2 data as the rca
        time_2, lat_2, lon_2, alt_2 = flight_pt2
        pt2_scale = 1 + alt_2/(ft_in_mile * radius) # Factor for pt 1 elevation
        pt2_cart = tuple(pt2_scale*p for p in cart_vector((lat_2, lon_2)))
        a_obs_2 = vector_len(vector_diff(pt2_cart, pt_obs_cart)) # obs to pt2 
        d_rca_obs = a_obs_2 # Set rca to pt1 line of sight
        t_rca, lat_rca, lon_rca, alt_rca = flight_pt2 # With other parameters
        # Then just return the params for flight_pt1
        return((d_rca_obs, t_rca, lat_rca, lon_rca, 0.0, alt_rca))
    elif flight_pt2 == (): # if flight_pt2 null, treat flight_pt1 as normal
        # Here we just return flight_pt1 data as the rca
        time_1, lat_1, lon_1, alt_1 = flight_pt1
        pt1_scale = 1 + alt_1/(ft_in_mile * radius) # Factor for pt 1 elevation
        pt1_cart = tuple(pt1_scale*p for p in cart_vector((lat_1, lon_1)))
        a_obs_1 = vector_len(vector_diff(pt1_cart, pt_obs_cart)) # obs to pt! 
        d_rca_obs = a_obs_1 # Set rca to pt1 line of sight
        t_rca, lat_rca, lon_rca, alt_rca = flight_pt1 # With other parameters
        # Then just return the params for flight_pt1
        return((d_rca_obs, t_rca, lat_rca, lon_rca, 0.0, alt_rca))
    # End if flight_pt1 == () and flight_pt2 == ()... elifs
    
    # Here we have a normal call, do the rca calculation. Start by splitting
    # out components of the flight tuples
    time_1, lat_1, lon_1, alt_1 = flight_pt1
    time_2, lat_2, lon_2, alt_2 = flight_pt2
        
    # Now compute the distances from the observation pt to the flight pts.
    # We do not use sperical distances because we are interested in the
    # straight line distance for working with sound propagation and energy
    # loss through the atmosphere. So, we create Cartesian vectors from the
    # center of the earth to the various points to compute vector distances.
    pt1_scale = 1 + alt_1/(ft_in_mile * radius) # Factor for pt 1 elevation
    pt1_cart = tuple(pt1_scale*p for p in cart_vector((lat_1, lon_1)))
    pt2_scale = 1 + alt_2/(ft_in_mile * radius) # and for pt 2
    pt2_cart = tuple(pt2_scale*p for p in cart_vector((lat_2, lon_2)))
    
    # Now compute the Cartesian distances (line of sight) between the various
    # points
    a_obs_1 = vector_len(vector_diff(pt1_cart, pt_obs_cart)) # obs to pt! 
    b_obs_2 = vector_len(vector_diff(pt2_cart, pt_obs_cart)) # obs to pt2
    c_1_2 = vector_len(vector_diff(pt2_cart, pt1_cart)) # pt! to pt2
    
# =============================================================================
#     OBSOLETE
#     a_obs_1 = sph_distance((lat_1, lon_1), (lat_obs, lon_obs))
#     b_obs_2 = sph_distance((lat_2, lon_2), (lat_obs, lon_obs))
#     # and the distance between the flight pts
#     c_1_2 = sph_distance((lat_1, lon_1), (lat_2, lon_2))
# =============================================================================
    # The 3 points (p1, p2, and obs) define a local plane, in which the obs pt
    # and the two flight pts form a triangle. We have the lengths of all three
    # sides; a, b, c, where c connects the flight pts, a connects the obs pt
    # with flight pt 1, and b connects the obs pt with flight pt 2. Let the
    # angles opposite to the sides be; α, β, ɣ. Then from trigonometry:
    #   cos α = (b^2 + c^2 - a^2)/2bc
    #   cos β = (a^2 + c^2 - b^2)/2ac
    #   cos ɣ = (a^2 + b^2 - c^2)/2ab
    
    if not (a_obs_1 == 0 or c_1_2 == 0): # If not a degenerate case
        # β = angle opposite side b, i.e., between sides a and c
        v_cosβ = (a_obs_1**2 + c_1_2**2 - b_obs_2**2)/(2 * a_obs_1 * c_1_2)
    else: # Note 0 problem on console and return useless value
#        print ('obs-a = '+str(a_obs_1)+', c-1-2 = '+str(c_1_2))
        return ((0, time_1, lat_1, lon_1, 1000, 0))
    d_rca_obs = a_obs_1 * math.sqrt(1 - v_cosβ**2) # a sinβ
    d_1_rca = a_obs_1 * v_cosβ
    fract_d_1 = d_1_rca/c_1_2 # rca loc along path as fraction of segment len
    
    # See if extrapolation called for, and keep rca estimate in bounds
    if fract_d_1 >= 0 and fract_d_1 <= 1:
        # In range, interpolate various associated quantities
        t_rca, lat_rca, lon_rca, alt_rca = \
            linear_interp(flight_pt1, flight_pt2, fract_d_1)
    elif fract_d_1 > 1: # If fract tries to extrapolate beyond pt2
        d_rca_obs = b_obs_2 # Set rca to pt2 line of sight
        t_rca, lat_rca, lon_rca, alt_rca = \
            linear_interp(flight_pt1, flight_pt2, 1.0) # With other parameters
    else: # If fract trying to extrapolate beyond pt1
        d_rca_obs = a_obs_1 # Set rca to pt1 line of sight
        t_rca, lat_rca, lon_rca, alt_rca = \
            linear_interp(flight_pt1, flight_pt2, 0.0) # With other parameters
    
    # All done, return values tuple
    return((d_rca_obs, t_rca, lat_rca, lon_rca, fract_d_1, alt_rca))
# End def rca


#%% =============================================================================
# Compute the dot product of two vector/lists (input arguments) and return
# a list with the dot product value and the angle (°) between the vectors. Note
# that the input vectors are not necessarily normalized unit vectors.
# =============================================================================
def dotproduct(v1, v2):
    dp = sum(p*q for p,q in zip(v1, v2)) # First, just do the dot product
    # Find lengths of input vectors
    vl1 = vector_len(v1)
    vl2 = vector_len(v2)
    if vl1 == 0 or vl2 == 0:
        print("Dot product angle undefined for 0 length vector")
        dpθ = 0
    else:
        # Then normalize the dp result to cos θ
        dpn = dp/(vl1 * vl2)
        # Account for precision errors
        if dpn > 1.0:
#            print("Dot product cos θ > 1", dpn)
            dpn = 1.0
        elif dpn < -1.0:
#            print("Dot product cos θ < -1", dpn)
            dpn = -1.0
#        print('dot product ', dpn)
        dpθ = math.degrees(math.acos(dpn)) # Calculate angle between in deg
    return((dp, dpθ))
# End def dotproduct


#%% =============================================================================
# Make a Cartesian vector out of a spherical vector specified by (lat1, lon1)
# where lat and lon are in degrees. Return the vector in the form (x, y, z).
# =============================================================================
def cart_vector(v1):
    radius = 3957.5 # Earth's radius in mi
    # First convert input degrees into radians & split out lat/lon
    lat1, lon1 = tuple(math.radians(p) for p in v1)
    # Compute the Cartesian vector components
    v1_cart = (math.cos(lat1) * math.cos(lon1), \
               math.cos(lat1) * math.sin(lon1), \
               math.sin(lat1))
    # Finally scale the vector to intersect the earth's surface
    v1_cart = vector_scale(v1_cart, radius)
    return(v1_cart)
# End def cart_vector


#%% =============================================================================
# Compute the vector sum of two vectors
# =============================================================================
def vector_sum(v1, v2):
    return(tuple(p+q for p,q in zip(v1, v2)))
# End def vector_sum


#%% =============================================================================
# Compute the vector difference between two vectors: v1 = v2 + diff
# =============================================================================
def vector_diff(v1, v2):
    return(tuple(p-q for p,q in zip(v1, v2)))
# End def vector_diff


#%% =============================================================================
# Compute the length of a vector
# =============================================================================
def vector_len(v):
    return(math.sqrt(sum(p*p for p in v)))
# End def vector_len


#%% =============================================================================
# Normalize a vector
# =============================================================================
def vector_normal(v):
    v_len = vector_len(v) # Compute vector length
    if v_len == 0.0:
        print("Trying to normalize zero-length vector")
        return((0)) #degenerate case
    else:
        return(tuple(p/v_len for p in v))
# End def vector_normal


#%% =============================================================================
# Scale a vector by a factor
# =============================================================================
def vector_scale(v, factor):
    return(tuple(p*factor for p in v))
# End def vector_scale


#%% =============================================================================
# Interpolate between two track/heading angles measured from north clockwise
# (in degrees) using a proportion factor, fract_12, to scale between pt 1 and
# pt 2 on the unit circle to an intermediate point, pt int.
# track_1 and track_2 are the track angles for pts 1 and 2, track_int is the
# interpolated track for pt int. The interpolation fraction, fract_12, runs
# from 0 to 1: fract_12 = 0 means use track_1 and fract_12 = 1 means use
# track_2.
# =============================================================================
def interp_trk(track_1, track_2, fract_12):
    # See if degenerate case
    if track_1 == track_2:
        return (track_1) # If so, just return the input value
    # First make unit vectors in the track directions
    v_1 = (math.sin(math.radians(track_1)), \
               math.cos(math.radians(track_1)))
    v_2 = (math.sin(math.radians(track_2)), \
               math.cos(math.radians(track_2)))
    # Then find partial scaled vector to the interpolated point between
    # sighting directions
    dp_v1_v2, d_theta_12 = dotproduct(v_1, v_2)
    if (track_1 < 180) and ((track_2 <= track_1) or \
        (track_2 >= (track_1 + 180))):
        d_theta_12 = -d_theta_12 # Track 2 counterclockwise from track 1
    elif (track_1 >= 180) and ((track_2 <= track_1) and \
          (track_2 >= ((track_1 + 180) % 360))):
        d_theta_12 = -d_theta_12 # Again track 2 counterclockwise from track 1
    # End if/elif track_1

    # Now interpolate the new angle between v_1 and v_2
    theta_int = track_1 + fract_12 * d_theta_12
    # And find the clockwise angle to the interpolated track
    if theta_int >= 0:
        theta_int = theta_int % 360
    else:
        theta_int += 360
    # End if v_int_x
    return(theta_int) # Return the result
# End def interp_trk


#%% =============================================================================
# Make an appropriate date string to describe the size of a sighting gap
# =============================================================================
def make_time_gap_str(delta_t):
    delta_m, delta_s = divmod(delta_t, 60)
    delta_h, delta_m = divmod(delta_m, 60)
    if delta_h > 0: # Here if gap longer than 1 hr
        return ('{:d}:{:02d}:{:02d}'.format(int(delta_h), \
                       int(delta_m), int(delta_s)) + ' hr')
    elif delta_m > 0: # Here if gap longer than 1 min
        return ('{:d}:{:02d}'.format(int(delta_m), \
                       int(delta_s)) + ' min')
    else: # Here if gap measured in seconds
        return ('{:d}'.format(int(delta_s)) + ' sec')
    # End if/elif/else
# End make_time_gap_str


#%% =============================================================================
# Compute the estimated Sound Exposure Level (SEL) for a given closest approach
# calculation. The estimate is based on the TCR model for overflight sound peak
# shape. The sound intensity function is a Lorentz distribution, depending on
# the intrinsic aircraft noise level (I0, which feeds the 1/r2 fall off),
# its velocity (v), its 3D distance of closest approach (rmin), and the
# atmospheric attenuation coefficient (α, approximating scattering, absorption,
# and refractive losses). The formula for total energy (SEL) under a noise peak
# is:
# 
#     E = π I0 e(- α rmin)/ (v rmin)
# =============================================================================
def compute_sel(rmin, v, altitude):
    knots_to_mph = 1.15077945 # Conversion of speed in knots to mph
#    ft_in_mile = 5280 # Number of feet in a mile
#    altitude_break = 0 # Where model params change for high/low altitudes
#    i0 = 8457595.8 # Intrinsic median noise emission constant for aircraft
#    alpha = 0.0004 # Atmospheric sound attenuation coefficient (per ft)
# Values < 1/2/18
#    altitude_break = 3000 # Where model params change for high/low altitudes
#    i0_high = 4.50e+10 # Median noise emission const for aircraft (per sec)
#    alpha_high = 3.0 # Atmospheric sound atten coef (per mi)
#    i0_low = 4.50e+10 # Median noise emission const for aircraft (per sec)
#    alpha_low = 3.0 # Atmospheric sound attenuation coefficient (per mi)
# Values > 1/2/18
#    altitude_break = 3000 # Where model params change for high/low altitudes
#    i0_high = 2.00E+10 # Median noise emission const for aircraft (per sec)
#    alpha_high = 1.2 # Atmospheric sound atten coef (per mi)
#    i0_low = 2.00E+10 # Median noise emission const for aircraft (per sec)
#    alpha_low = 1.2 # Atmospheric sound attenuation coefficient (per mi)
# Values > 1/16/18
#    altitude_break = 3000 # Where model params change for high/low altitudes
#    i0_high = 2.58732E+10 # Median noise emission const for aircraft (per sec)
#    alpha_high = 1.696152646 # Atmospheric sound atten coef (per mi)
    i0_low = 2.09941E+09 # Median noise emission const for aircraft (per sec)
    alpha_low = 0.372935332 # Atmospheric attenuation coefficient (per mi)
    
    # Values 9/7/18 (Fit to CI Leq sound peak w Doppler correction)
    altitude_break = 0 # Where model params change for high/low altitudes
#    i0_high = 8.3E+10 # Median noise emission const for aircraft (per sec)
    i0_high = 8.3E+9 # Median noise emission const SFO B&K data (per sec)
    alpha_high = 1.7 # Atmospheric sound atten coef (per mi)
#    alpha_mi = alpha * ft_in_mile # Convert alpha to attenuation per mile
#    knots_to_mps = knots_to_mph / 3600 # Convert knots to miles per second
    
    if rmin <= 0 or v <= 0:
        sel = 1 # Nonsense, but allows log10 w/o error
    elif altitude >= altitude_break: # High altitude case
        sel = i0_high * math.exp(-alpha_high * rmin) / \
                (v * knots_to_mph * rmin)
    else: # Low altitude case
        sel = i0_low * math.exp(-alpha_low * rmin) / \
                (v * knots_to_mph * rmin)
    return(sel) # And return it
# End def compute_sel


#%% =============================================================================
# Function to accumulate sums of SEL values for various time periods:
# 0:00 - 24:00; 0:00 - 6:00; 6:00 - 12:00; 12:00 - 18:00; & 18:00 - 24:00
# =============================================================================
def dnl_sums(dnl_tpl, sel, rel_time):
    dnl_24hr, dnl_1, dnl_2, dnl_3, dnl_4 = dnl_tpl # Break out sub-sums
    if rel_time < 0 or rel_time > 24 * 3600:
        print('SEL time {0} out of range for calculating DNL'.format(rel_time))
    elif rel_time <= (6 * 3600): # If in 1st quarter of the day
        dnl_24hr += 10 * sel # Bump the day total, with nighttime factor
        dnl_1 += 10 * sel # Bump 1st quarter total, with nighttime factor
    elif rel_time <= (12 * 3600): # If in 2nd quarter of the day
        if rel_time > (7 * 3600): # And after 7:00
            dnl_24hr += sel # Bump the day total
            dnl_2 += sel # Bump 2nd quarter total
        else: # Still need nighttime penalty
            dnl_24hr += 10 * sel # Bump the day total, with nighttime factor
            dnl_2 += 10 * sel # Bump 2nd quarter total, with nighttime factor
        # End if/else rel_time
    elif rel_time < (18 * 3600): # If in 3rd quarter of the day
        dnl_24hr += sel # Bump the day total
        dnl_3 += sel # Bump 3rd quarter total
    elif rel_time < (22 * 3600): # If in 4th quarter, but not nighttime yet
        dnl_24hr += sel # Bump the day total
        dnl_4 += sel # Bump 4th quarter total
    else:
        dnl_24hr += 10 * sel # Bump the day total, with nighttime factor
        dnl_4 += 10 * sel # Bump 4th quarter total, with nighttime factor
    # End if/elif.../else
    
    # Now return the updated tuple
    return((dnl_24hr, dnl_1, dnl_2, dnl_3, dnl_4))
# End def dnl_sums


#%% =============================================================================
# Function to accumulate counts of overflights for various rca ranges and time
# periods:
# rca: <= 1/3 mi; 2/3 mi; 1 mi; 1 1/3 mi; 1 2/3 mi; 2 mi
# time periods: 24-hr; 0:00 - 6:00; 6:00 - 12:00; 12:00 - 18:00; 18:00 - 24:00
# cnt_ary has the structure:
# {'24hr': [0, 0, 0, 0, 0, 0],
# '0-6': [0, 0, 0, 0, 0, 0],
# '6-12': [0, 0, 0, 0, 0, 0],
# '12-18': [0, 0, 0, 0, 0, 0],
# '18-24': [0, 0, 0, 0, 0, 0]}
# where each sextuplet holds counts for the rca distance levels above
# =============================================================================
def ovflght_cnts(cnt_ary, pt_dist, rel_time, ref_dist):
#    ref_dist = [0.15, 0.20, 0.25, 0.30, 0.35, 0.40]
    ref_time = {'0-6': 6*3600,
                '6-12': 12*3600,
                '12-18': 18*3600,
                '18-24': 24*3600}

    n_ref_dist = len(ref_dist)
    
    # First find what rca distance range is relevant
    i_rca = -1 # Code for value not set
    for i in range(n_ref_dist):
        if pt_dist <= ref_dist[i]:
            i_rca = i # This is the distance index to start with
            break
        # End if pt_dist <= ref_dist[i]:
    # End for i in range(len(ref_dist)):
    
    # If not in distance range, return updated input
    if i_rca == -1:
        return (cnt_ary) # if too big, don't count this one
    # End if i_rca == -1:
    
    # Now update the count tuple for the 24 hr count
    for i in range(i_rca, n_ref_dist):
        cnt_ary['24hr'][i] += 1
    # End for i in range(i_rca, n_ref_dist):
    
    # Then find which quarter of the day is appropriate
    time_keys = list(ref_time)
    for t_key in time_keys:
        if rel_time <= ref_time[t_key]:
            i_t_key = t_key
            break
        # End if rel_time <= ref_time[t_key]:
    # End for t_key in time_keys:
    
    # And update the count tuple for the right day quarter
    for i in range(i_rca, n_ref_dist):
        cnt_ary[i_t_key][i] +=1
    # End for i in range(i_rca, n_ref_dist):
    
    # Now return the updated structure
    return(cnt_ary)
# End def ovlght_cnts


#%% =============================================================================
# Function to accumulate counts of overflights for various rca ranges and time
# periods:
# rca: <= 1/3 mi; 2/3 mi; 1 mi; 1 1/3 mi; 1 2/3 mi; 2 mi
# time periods: 24-hr; 0:00 - 6:00; 6:00 - 12:00; 12:00 - 18:00; 18:00 - 24:00
# cnt_ary has the structure:
# {'24hr': [0, 0, 0, 0, 0, 0],
# '0-6': [0, 0, 0, 0, 0, 0],
# '6-12': [0, 0, 0, 0, 0, 0],
# '12-18': [0, 0, 0, 0, 0, 0],
# '18-24': [0, 0, 0, 0, 0, 0]}
# where each sextuplet holds counts for the rca distance levels above
# =============================================================================
def lmax_level_cnts(cnt_ary, pk_amp, rel_time):
    ref_levels = [50.0, 55.0, 60.0, 65.0]
    ref_time = {'0-6': 6*3600,
                '6-12': 12*3600,
                '12-18': 18*3600,
                '18-24': 24*3600}

    n_ref_levels = len(ref_levels)
    
    # First find what peak amplitude range is relevant
    i_amp = -1 # Code for value not set
    for i in range(n_ref_levels):
        if pk_amp >= ref_levels[i]:
            i_amp = i # This is the sound level index to start with
#            break
        # End if pk_amp <= ref_levels[i]:
    # End for i in range(len(ref_levels)):
    
    # If not in sound level range, return updated input
    if i_amp == -1:
        return (cnt_ary) # if too small, don't count this one
    # End if i_amp == -1:
    
    # Now update the count tuple for the 24 hr count
    for i in range(i_amp + 1):
        cnt_ary['24hr'][i] += 1
    # End for i in range(i_amp, n_ref_levels):
    
    # Then find which quarter of the day is appropriate
    time_keys = list(ref_time)
    for t_key in time_keys:
        if rel_time <= ref_time[t_key]:
            i_t_key = t_key
            break
        # End if rel_time <= ref_time[t_key]:
    # End for t_key in time_keys:
    
    # And update the count tuple for the right day quarter
    for i in range(i_amp + 1):
        cnt_ary[i_t_key][i] +=1
    # End for i in range(i_amp, n_ref_levels):
    
    # Now return the updated structure
    return(cnt_ary)
# End def ovlght_cnts


#%% =============================================================================
# Function to accumulate altitude statistice for various rca distances from a
# matrix node
# rca: <= ref_dist array values
# alt_ary has the structure:
# {'sum': [0.0, 0.0, 0.0, 0.0, 0.0, 0.0],
#  'sum_sqs': [0.0, 0.0, 0.0, 0.0, 0.0, 0.0]}
# where each sextuplet holds sums of altitudes and altitudes squared for the
# rca distance levels in ref_dist. These are 24-hour accumulations so the
# counts for computing average altitude and variance come from the count
# statistics acculated in the function ovlght_cnts
# =============================================================================
def alt_stats(alt_ary, pt_dist, rca_alt):
    ref_dist = [0.15, 0.20, 0.25, 0.30, 0.35, 0.40]
    n_ref_dist = len(ref_dist)
    
    # First find what rca distance range is relevant
    i_rca = -1 # Code for value not set
    for i in range(n_ref_dist):
        if pt_dist <= ref_dist[i]:
            i_rca = i # This is the distance index to start with
            break
        # End if pt_dist <= ref_dist[i]:
    # End for i in range(len(ref_dist)):
    
    # If beyond distance range, return the initial array
    if i_rca == -1:
        return (alt_ary)
    # End if i_rca == -1:
    
    # In range, so update the altitude statistics list
    for i in range(i_rca, n_ref_dist):
        alt_ary['sum'][i] += rca_alt
        alt_ary['sum_sqs'][i] += rca_alt**2
    # End for i in range(i_rca, n_ref_dist):
    
    # Finally return the updated structure
    return(alt_ary)
# End def alt_stats


#%% =============================================================================
# Function to linearly interpolate parameter values. Inputs are a pair of
# tuples, each representing measured data points bounding the
# interpolation. A third input gives the proportional distance between
# input 1 and input 2 to locate the median point whose value is to be
# estimated.
# =============================================================================
def linear_interp(tup1, tup2, fract):
        return(tuple(p+fract*(q-p) for p,q in zip(tup1, tup2)))
# End def linear_interp


#%% =============================================================================
# Function to format a string that will be added to the file of found points
# of closest approach for this observation point and date. rca_tuple contains
# all the parameters found and computed for the rca.
# =============================================================================
def fmt_rca_str(icao_code, flight_id, segment_n, rca_tuple):
    # First unpack the rca parameters
     rca_d, rca_t, rca_lat, rca_lon, rca_f, rca_alt, dpθ, rca_speed, rca_trk, \
         rca_snd_arr, rca_gnd_dist, rca_sel, rca_vert_rate = rca_tuple
     rca_t_str = ut.datetime.fromtimestamp(rca_t).strftime('%m/%d/%y %H:%M:%S')
     rca_snd_arr_str = ut.datetime.fromtimestamp(rca_snd_arr). \
         strftime('%H:%M:%S')
     ret_str = 'ICAO: ' + icao_code + ' (' + str(segment_n) + \
         ')\tFlight ID: ' + flight_id + '\t' + rca_t_str + \
         '\t%.2f' %rca_gnd_dist + '\t%.2f' %rca_d + '\t' + \
         str(round(rca_t, 1)) + '\t' + \
         str(round(rca_lat, 6)) + '\t' + str(round(rca_lon, 6)) + \
         '\t%.2f' %rca_f + '\t%.2f' %dpθ + '\t%.0f' %rca_alt + \
         '\t%.0f' %rca_speed + '\t%.0f' %rca_vert_rate + '\t%.0f' %rca_trk + \
         '\t' + rca_snd_arr_str + '\t%.6e' %rca_sel + '\n'
     
     # Return the result
     return(ret_str)

 # End def fmt_rca_str


#%% =============================================================================
# Function to update bounding coordinates of a box containing a given flight
# segment. This will allow faster filtering of segments when computing closest
# approach distances.
# =============================================================================
def update_box(sighting_rec, max_tuple, min_tuple):
    # First unpack the input parameters
    lat_max, lon_max = max_tuple
    lat_min, lon_min = min_tuple
    set_lat = sighting_rec['lat']
    set_lon = sighting_rec['lon']
    # Then update gps bounds; 0 initial value means value not set yet
    if lat_max == 0:
        lat_max = set_lat
        lat_min = set_lat
        lon_max = set_lon
        lon_min = set_lon
        return((lat_max, lon_max, lat_min, lon_min))
    # End if lon_max == 0
    
    # Here we update the individual gps limit params as needed
    if set_lat > lat_max:
        lat_max = set_lat
    if set_lat < lat_min:
        lat_min = set_lat
    if set_lon > lon_max:
        lon_max = set_lon
    if set_lon < lon_min:
        lon_min = set_lon
    
    # Now return the updated results
    return((lat_max, lon_max, lat_min, lon_min))

# End def update_box


#%% =============================================================================
#
#  Function to screen a json data structure containing lists of sighting data
#  ordered by aircraft icao codes. For each icao code, the structure contains
#  an attribute/value (dict) list of flight and sighting data, {xxx}, where
#  {xxx} has the structure:
#     {'icao-1: [{meta data}, [{segment data}, {Sighting info-1},
#        {Sighting info-2}, ...],
#     {'icao-2: [{meta data}, [{segment data}, {Sighting info-1}, ...],
#     {'icao-3: [...]}}}
# 
#     Where {meta data-i} contains descriptive information about this aircraft:
#         {"icao": "value", "tail #": "value", "ac_type": "value",
#           "#_segments": #}
# 
#     Where {Segment data-i} contains info about the next flight segment,
#        where segments are separated by gaps much longer than the sighting
#        interval:
#        {"segment": #, "gap": "time", "segment_start": UNIX time,
#         "segment_end": UNIX time, "flight": "id", 'gps_max': (lat, lon),
#         'gps_min': (lat, lon), 'origin': "airport code",
#         'destination': "airport code", '#_sightings': #}
# 
#     Where {Sighting info-i} is a sighting instance that has keys and values:
#         {"hex": "icao value", "flight": "value", "lat": value, "lon": value,
#          "distance": value, "seen_pos": value, "altitude": value,
#          "vert_rate": value, "track": value, "speed": value}
#     Sighting info-i may also have an interpolation key "interp": "y" to
#     signal that a missing sighting has been interpolated and added to the
#     sighting set.
# 
# =============================================================================
def check_json_data(data_struct):
    key_set = list(data_struct)
    for i_key in key_set:
        r_set = data_struct[i_key] # Split out this icao's data record
        icao_meta = r_set[0] # The icao meta data are in the first sublist
        n_segments = icao_meta['#_segments']
        if n_segments != len(r_set) - 1:
            print('json data check Warning: n_segments = {0}, but len(r_set)-1' 
                  ' = {1} in {2}'.format(str(n_segments), 
                      str(len(r_set)-1), icao_meta))
            sys.exit()
        # End if n_segments != len(r_set) - 1
        
        for j_seg in range(1, len(r_set)):
            seg_data = r_set[j_seg] # Data block for this segment
            seg_meta = seg_data[0] # Fetch the segment hdr data
            seg_sightings = seg_data[1] # And the list of sighting records
#            segment_number = seg_meta['segment']
            n_sightings = seg_meta['#_sightings']
            if n_sightings != len(seg_sightings):
                print('json data check Warning: n_sightings = {0}, but ' 
                      'len(seg_sightings)-1 = {1} in {2}' 
                      .format(str(n_sightings), str(len(seg_sightings)-1),
                              seg_meta))
                sys.exit()
            # End if n_sightings != len(seg_sightings) - 1
        # End for j_seg in range(1, len(r_set))
    # End for i_key in icao_keys
    
    print('Made it through json data check')
    return(True)
# End def check_json_data(data_struct):
    
def screen_sighting_data(json_data, obs_pt_r, date, dmax, alt_range, \
                         airport=None, log_str=None):
    # The arguments are defined as follows:
    #  json_data - The data structure with input data in the above format
    #  obs_pt_r - A tuple with the (lat, lon, elevation) of the observation pt
    #  date - UNIX format tuple of start and stop times for allowed data
    #         (target_date_st, target_date_end)
    #  dmax - The maximum ground distance (mi) from the observer for allowed
    #         sightings
    #  alt_range - A tuple of the minimum and maximum altitudes (ft) for
    #              allowed sightings
    #  airport - A list of airport names to include in listing, where a
    #            positive match is for either 'origin' or 'destination'. If
    #            an airport is prefixed with 'to', check only for
    #            'destinations'. If an airport is prefixed with 'from',
    #            check only for 'origins'. Prefixes should be attached to
    #            the airport name with a hyphen, i.e. 'to-KSFO' or 'from-KSFO'.
    #            If airport is empty, no airport screening is done.
    #  log_str - A string to accumulate diagnostic data for debugging. If the
    #           initial value is '', don't add anything
    
    # The following are nomenclature and key definitions of use (also see
    # above)
    # First the key structure of an ICAO header record
    # icao_meta_keys = ['icao', 'tail_#', 'ac_type', '#_segments']
    # Then the key structure of a flight segment header record
    # segment_keys = ['segment', 'gap', 'segment_start', 'segment_end', \
    #             'flight', '#_sightings', 'gps_max', 'gps_min', \
    #             'origin', 'destination']
    # Finally the key structure of the FlightAware sighting records
    # rec_keys = ['hex','flight','lat','lon', 'distance', 'los_distance', \
    #             'seen_pos', 'altitude', 'vert_rate', 'track', 'speed']

    # First deal with defaults
    if airport is None:
        airport = [] # Default is empty list
    # End if airport is None:
    if log_str is None:
        log_str = '' # Default is empty string
    # End if log_str is None:
    
    # Next some constants and variable initialization
    
    debug_sw = 0 # Turn off debugging for now
#    debug_sw = 1 # Turn on debugging for now
    ft_in_mile = 5280 # Number of feet in a mile
    calib_inc = 0.05 # Angle increment (deg) to relate angular increments in
                     # latitude and longitude to ground mile increments
    d_shadow = 1.0 # This is a fudge factor applied to dmax when screening
                   # sightings so that parts of tracks near the border can
                   # be used to locate more applicable pts of closest approach
    data_edit = {} # Place for edited tracks to return to caller
    
    # For this observation point, compute a bounding gps box with side 2 * dmax
    # This box will be used to speed the selection of flight segments
    # according to more detailed screening criteria (that are computing
    # intensive).
    lat_obs, lon_obs, elev_obs = obs_pt_r # Split out the obs pt params
    obs_pt = (lat_obs, lon_obs)
    altmin, altmax = alt_range # Allowed altitude range
    target_date_st, target_date_end = date # Allowed time range
    
    # Compute the ground distances corresponding to calibrated changes in the
    # gps coordinates at the observation pt
    d_lat_mi = 0.5 * sph_distance((lat_obs - calib_inc, lon_obs), \
                                     (lat_obs + calib_inc, lon_obs))
    d_lon_mi = 0.5 * sph_distance((lat_obs, lon_obs - calib_inc), \
                                     (lat_obs, lon_obs + calib_inc))
    # Then compute the gps angle increments to the sides of the bounding box
    d_lat_inc = calib_inc * dmax / d_lat_mi
    d_lon_inc = calib_inc * dmax / d_lon_mi
    
    # Finally compute the bounding box gps coordinates for the observer
    lat_obs_max = round(lat_obs + d_lat_inc, 6) # Top side
    lat_obs_min = round(lat_obs - d_lat_inc, 6) # Bottom side
    lon_obs_max = round(lon_obs + d_lon_inc, 6) # Right side
    lon_obs_min = round(lon_obs - d_lon_inc, 6) # Left side
    
    # Now we loop through the icao keys and screen the allowed flight segment
    # and sighting data, based on distance, altitude, and time criteria.
    
    # Get a list of all included icao keys
    icao_keys = list(json_data) # Fetch the list of tracked icao keys
    
    # Following are counters for various discard criteria
    discards_distance = 0
    discards_altitude = 0
    discards_time = 0
    
    #%% -----------------
    # This is for debugging, testing the consistency of the input json_data
    # -----------------
    # If we are in debug mode, check json_data integrity
    if debug_sw != 0 and check_json_data(json_data): 
#        for i_icao in icao_keys:
#            r_set = json_data[i_icao] # Split out this icao's data record
#            icao_meta = r_set[0] # The icao meta data are in the first sublist
#            n_segments = icao_meta['#_segments']
#            if n_segments != len(r_set) - 1:
#                print('Precheck Warning: n_segments = {0}, but len(r_set)-1' \
#                      ' = {1} in {2}'.format(str(n_segments), \
#                          str(len(r_set)-1), icao_meta))
#                sys.exit()
#            # End if n_segments != len(r_set) - 1
#            
#            for j_seg in range(1, len(r_set)):
#                seg_data = r_set[j_seg] # Data block for this segment
#                seg_meta = seg_data[0] # Fetch the segment hdr data
#                seg_sightings = seg_data[1] # And the list of sighting records
#                segment_number = seg_meta['segment']
#                n_sightings = seg_meta['#_sightings']
#                if n_sightings != len(seg_sightings):
#                    print('Precheck Warning: n_sightings = {0}, but ' \
#                          'len(seg_sightings)-1 = {1} in {2}' \
#                          .format(str(n_sightings), str(len(seg_sightings)-1),\
#                                  seg_meta))
#                    sys.exit()
                # End if n_sightings != len(seg_sightings) - 1
            # End for j_seg in range(1, len(r_set))
        # End for i_icao in icao_keys
        
        print('Made it through precheck of json_data')
    # End if debug_sw != 0
    
    #%% Here we normalize the list of airport origins and destinations to prepare
    # for screening. If an airport list entry is of the form 'to-xxxx', it is
    # converted to '+xxxx'; if 'from-xxxx', to '-xxxx'; and if no prefix, it
    # stays as 'xxxx'.
    airport_norm = []
    if airport != []:
        # If airport is not empty, normalize the search term forms.
        for i_aprt in airport:
            u_aprt = i_aprt.upper()
            if u_aprt.count('TO-') == 1:
                airport_norm.append('+' + u_aprt[3 :])
            elif u_aprt.count('FROM-') == 1:
                airport_norm.append('-' + u_aprt[5 :])
            else:
                airport_norm.append(u_aprt)
            # End if i_aprt.count('to-') == 1/elif...
        # End for i_aprt in airport 
    # End if airport != []:
#    print('Normalize: ', airport, airport_norm)
    
    #%% Now loop through all flight icaos and do the filtering
    for i_icao in icao_keys:
        r_set = json_data[i_icao] # Split out this icao's data record
        # The icao meta data are in the first sublist; make a fresh copy
#        icao_meta = deepcopy(r_set[0])
        icao_meta = cpy.deepcopy(r_set[0])
        # filtered_icao is a buffer for accumulating relevant sightings for
        # a given icao.
        filtered_icao = [icao_meta] # Clean storage place
        n_segments = icao_meta['#_segments']
        
        if n_segments != len(r_set) - 1:
            print('Warning: n_segments = {0}, but len(r_set)-1 = {1} in {2}' \
                  .format(str(n_segments), str(len(r_set)-1), icao_meta))
            sys.exit()
        # End if n_segments != len(r_set) - 1
        
        # Loop through the segments for this icao
        for j_seg in range(1, len(r_set)):
            seg_data = r_set[j_seg] # Data block for this segment
            # Fetch a clean copy of the segment hdr data
#            seg_meta = deepcopy(seg_data[0])
            seg_meta = cpy.deepcopy(seg_data[0])
            seg_sightings = seg_data[1] # And the sighting records
            segment_number = seg_meta['segment']
            n_sightings = seg_meta['#_sightings']
            if n_sightings != len(seg_sightings):
                print('Warning: n_sightings = {0}, but len(seg_sightings)-1' \
                      '= {1} in {2}'.format(str(n_sightings), \
                         str(len(seg_sightings)-1), seg_meta))
                sys.exit() # Stop for debugging
            # End if n_sightings != len(seg_sightings)
            
#            print('Apply: ', airport, airport_norm)
            if airport != []:
                # If airport is not empty, scan for hits on this segment to
                # be included.
                n_aprt_hits = 0 # Counter of hits
                for i_aprt in airport_norm:
                    # See if this specifies 'origin'
                    if i_aprt[0] == '-' and \
                            i_aprt[1 :] == seg_meta['origin']:
                        n_aprt_hits += 1 # Note we have a hit
                        break # No need to check further
                    elif i_aprt[0] == '+' and \
                            i_aprt[1 :] == seg_meta['destination']:
                        n_aprt_hits += 1 # Note we have a hit
                        break # No need to check further
                    elif i_aprt == 'UNKNOWN' and \
                            i_aprt == seg_meta['origin'].upper() and \
                            i_aprt == seg_meta['destination'].upper():
                        n_aprt_hits += 1 # Note we have a hit
                        break # No need to check further
                    elif i_aprt == seg_meta['origin'] or \
                            i_aprt == seg_meta['destination']:
                        n_aprt_hits += 1 # Note we have a hit
                        break # No need to check further
                    # End if i_aprt[0] == '-' / elif ...
                # End for i_aprt in airport_norm:
                
                # If we had no airport hits in this segment, ignore segment
                if n_aprt_hits == 0:
                    n_segments -= 1 # Decrement segment count & update things
                    icao_meta['#_segments'] = n_segments
                    filtered_icao[0] = icao_meta
                    continue
                # End if n_aprt_hits == 0:
            # End if airport != []:

            # filtered_segment is a buffer for filtered segment data and
            # We will need to check for altitude and proximity criteria in the
            # following to discard any beyond range for this observation point.
            filtered_segment = []
            
            # Split out some header data
#            seg_st_time = seg_meta['segment_start']
#            seg_end_time = seg_meta['segment_end']
#            seg_flight_id = seg_meta['flight']
#            seg_n_sightings = seg_meta['#_sightings']
            seg_lat_max, seg_lon_max = seg_meta['gps_max']
            seg_lat_min, seg_lon_min = seg_meta['gps_min']
#            seg_aprt_origin = seg_meta['origin']
#            seg_aprt_dest = seg_meta['destination']
            
            # First check if this segment is near enough to current obs pt
            if seg_lat_max < lat_obs_min or seg_lat_min > lat_obs_max or \
                    seg_lon_max < lon_obs_min or seg_lon_min > lon_obs_max:
                discards_distance += 1 # Note distance problem
                n_segments -= 1 # Decrement segment count
                icao_meta['#_segments'] = n_segments
                filtered_icao[0] = icao_meta # Clean storage place
                
                if log_str == '':
                    continue
                log_str += 'Segment/observer boxes disjoint for seg {9}: {0}\n' \
                    '\tSeg: gpsmin ({1}, {2}), gpsmax ({3}, {4})\n' \
                    '\tObs: gpsmin ({5}, {6}), gpsmax ({7}, {8})\n' \
                    .format(icao_meta, str(seg_lat_min), str(seg_lon_min), \
                           str(seg_lat_max), str(seg_lon_max), \
                           str(lat_obs_min), str(lon_obs_min), \
                           str(lat_obs_max), str(lon_obs_max), \
                           str(segment_number))
                continue # No overlap, just go to next segment
            # End if seg_lat_max < lat_obs_min...
            
            # This segment is relevant, loop through the set of sightings
            min_obs_dist = -1 # Place to find minimum obs to sighting distance
            for k_sght in range(len(seg_sightings)):
                s_set = seg_sightings[k_sght] # Next sighting record
                # Here we get ready to check on filter criteria
                seen_pt = (s_set['lat'], s_set['lon']) # lat/lon tuple
                alt_pt = s_set['altitude'] # Current sighting altitude
                time_pt = s_set['seen_pos'] # Current sighting seen time
                # Find ground distance to current observation point
                new_obs_dist = sph_distance(obs_pt, seen_pt)
                # Find line-of-sight distance (mi) to aircraft
                los_dist = math.sqrt(new_obs_dist**2 + \
                                     ((alt_pt - elev_obs )/ft_in_mile)**2)
                
                # See if this sighting is within bounds: distance, altitude,
                # and date/time
                if new_obs_dist > d_shadow * dmax: # Allow some dist leeway
                    discards_distance += 1
                    continue
                elif alt_pt > altmax or alt_pt < altmin:
                    discards_altitude += 1
                    continue
                elif time_pt < target_date_st or time_pt > target_date_end:
                    discards_time += 1
                    continue
                # End if new_obs_dist > dmax: elif...
                
                # Good sighting here, make a clean copy and update distance
                # and los_distance values
#                s_set = deepcopy(s_set)
                s_set = cpy.deepcopy(s_set)
                s_set['distance'] = new_obs_dist
                s_set['los_distance'] = los_dist
                
                # Find minimum observer to sighting distance
                if min_obs_dist == -1:
                    min_obs_dist = new_obs_dist
                elif new_obs_dist < min_obs_dist:
                    min_obs_dist = new_obs_dist
                
                # Seems OK, add the updated sighting to the filtered set
                filtered_segment.append(s_set)
            # End for k_sght in range(len(seg_sightings))
            
            # See if this track come close enough to observer
            if min_obs_dist == -1 or min_obs_dist >= dmax:
                discards_distance += 1 # No
                filtered_segment = [] # Kill segment sighting contents
            # End if min_obs_dist >= dmax:
            
            if filtered_segment == []: # If nothing found in last seg
                n_segments -= 1 # Decrease # of relevant segments
                icao_meta['#_segments'] = n_segments # Update icao_meta
                filtered_icao[0] = icao_meta # Save new count
                if log_str == '':
                    continue
                log_str += 'Discarded segment {0} in {1}, no valid sightings:'\
                '\n\t{2}\n'.format(str(segment_number), icao_meta, seg_meta)
                continue # Move on w/o saving anything
            # End if filtered_segment == []
            
            # Wrap up this set of filtered sightings
            sighting_count = len(filtered_segment)
            if sighting_count > 0: # If there are any sightings left
                seg_meta['#_sightings'] = sighting_count # Save what we have
                filtered_icao.append([seg_meta, filtered_segment]) # Add segment
            # End if sighting_count > 1
        
        # End for j_seg in range(1, len(r_set)):
        
        # Finally, if there are any data left for this segment, update the
        # icao entry in the output buffer with the new filtered sighting set.
        # If whole track discarded, note it
        if n_segments <= 0 or len(filtered_icao) <= 1:
            if log_str == '':
                continue
            log_str += 'Discarded entire icao track: {0}\n'.\
                format(icao_meta)
        else:
            data_edit[i_icao] = filtered_icao # Update edited entry
        
        # End if len(filtered_icao) == 1
    
    # End for i_icao in icao_keys
    
    # Now report the summary statistics for discards
    if discards_altitude != 0 or discards_distance != 0 or discards_time != 0:
        if log_str != '':
            log_str += 'Sighting discard statistics according to criteria: ' \
                'altitude {0}; distance {1}; time {2}\n' \
                .format(str(discards_altitude), str(discards_distance), \
                        str(discards_time))
        # End if log_str != ''
    # End if discards_altitude != 0 or ...
    
    # See if data structure to be returned is OK
    if debug_sw != 0 and check_json_data(data_edit): 
        print('Made it through post check of data_edit')
    # End if debug_sw != 0 and check_json_data(data_edit): 
    
    # And finally return the results: data_edit, log_str as a tuple
    return(data_edit, log_str)

# End def screen_sighting_data ...


#%% =============================================================================
# Routine to fetch a date in the format yymmdd, and return a date tuple.count
# =============================================================================
def get_target_date(input_date='NONE'):
    # Here we prompt for the target date if necessary (yymmdd) and check on
    # its validity. If input is from the keyboard, we loop until an acceptable
    # date is entered. If the date was passed in the call, we analyze it for
    # being acceptable. If the final date is OK, we return a date tuple from
    # yy, mm, dd. If the date (passed) has problems, we return -1.
    while True:
        # See if data value has been passed or needs to be input
        if input_date == 'NONE':
            target_date = input('Enter the target date (yymmdd): ')
        else:
            target_date = input_date
            
        if len(target_date) != 6: # Length must check out
            if input_date != 'NONE':
                return (-1) # If bad input from call and failed...
            else: # Print message and back to keyboard for another try
                print('Invalid target date: {0}'.format(target_date))
                continue # If bad keyboard input, try again
            # End if input_date == 'NONE':
        # End if len(target_date) != 6
        
        # Now split out the date components
        yy = '20' + target_date[0 : 2]
        mm = target_date[2 : 4]
        dd = target_date[4 : 6]
        if int(yy) > 2000 and \
                int(mm) >= 1 and int(mm) <= 12 and \
                int(dd) >= 1 and int(dd) <= 31:
            break # Probably good enough, carry on
        # End if int(yy) > 2016 and ...
        
        # Here still a problem
        print('Invalid target date: {0}'.format(target_date))
        if input_date != 'NONE':
            return (-1) # If bad input from call and failed...
        else:
            continue # If bad keyboard input, try again
        # End if input_date == 'NONE':
    # End while True:
    
    # Return the target date as a date tuple
    return (ut.date(int(yy),int(mm),int(dd)))
# End def get_target_date()


#%% =============================================================================
# Function to normalize a list of airport names and return the normalized list
# =============================================================================
def normal_airport(raw_name_list):
    # Allowed airport names
    local_airports = ['KSFO', 'KSQL', 'KPAO', 'KNUQ', 'KSJC', 'KRHV', 'KHWD', \
                  'KOAK', 'UNKNOWN']
    
    target_airports = [] # Place to store returned list
    for x in raw_name_list:
        # Normalize and check the airport name
        y = x.upper()
        y = y.replace(' ', '')
        y = y.replace(',', '')
        if y in local_airports:
            target_airports.append(y)
        else:
            print('Invalid local airport: {0}'.format(y))
            sys.exit()
        # End if y in local_airports:
    # End for x in raw_name_list:
    
    # If none specified, use the whole local airport list
#    if target_airports == []:
#        target_airports = local_airports
    # End if target_airports == []
    
    # Return the normalized list
    return (target_airports)
# End def normal_airport(raw_name_list):


#%% =============================================================================
# Routine to test if a string represents an integer
# =============================================================================
def test_int(s):
    try: 
        int(s)
        return (True)
    except ValueError:
        return (False)
# End def test_int(s):


#%% =============================================================================
# Routine to convert US aircraft identifiers: ICAO to/from Tail number
# =============================================================================
base9 = '123456789'  # The first digit (after the "N") is always one of these.
base10 = '0123456789' # The possible second and third digits are one of these.
# Note that "I" and "O" are never used as letters, to prevent confusion with
# "1" and "0"
base34 = 'ABCDEFGHJKLMNPQRSTUVWXYZ0123456789' 
icaooffset = 0xA00001 # The lowest possible number, N1, is this.
b1 = 101711 # basis between N1... and N2...
b2 = 10111 # basis between N10.... and N11....

def suffix(rem):
    """ Produces the alpha(numeric) suffix from a number 0 - 950 """
    if rem == 0:
        suf = ''
    else:
        if rem <= 600: #Class A suffix -- only letters.
            rem = rem - 1
            suf = base34[rem // 25]
            if rem % 25 > 0:
                suf = suf + base34[(rem % 25) - 1] # second class A letter, if present.
        else:  #rem > 600 : First digit of suffix is a number.  Second digit may be blank, letter, or number.
            rem = rem - 601
            suf = base10[rem // 35]
            if rem % 35 > 0:
                suf = suf + base34[(rem % 35) - 1]
    return suf
    
def enc_suffix(suf):
    """ Produces a remainder from a 0 - 2 digit suffix. 
    No error checking.  Using illegal strings will have strange results."""
    if len(suf) == 0:
        return 0
    r0 = base34.find(suf[0])
    if len(suf) == 1:
        r1 = 0
    else:
        r1 = base34.find(suf[1]) + 1
    if r0 < 24: # first char is a letter, use base 25
        return (r0 * 25 + r1 + 1)
    else:  # first is a number -- base 35.
        return (r0 * 35 + r1 - 239)   
    
def icao_to_tail(icao):
    if len(icao.rstrip()) != 6:
        return (-1)
    icao_int = int(icao.rstrip(), 16)
    if (icao_int < 0) or (icao_int > 0xadf7c7):
        return (-1)
    icao_int = icao_int - icaooffset
    d1 = icao_int // b1
    if d1 < 0 or d1 >= len(base9):
        return (-1)
#    print (str(d1))
    nnum = 'N' + base9[d1]
    r1 = icao_int % b1
    if r1 < 601:
        nnum = nnum + suffix(r1) # of the form N1ZZ
    else:
        d2 = (r1 - 601) // b2  # find second digit.
        if d2 < 0 or d2 >= len(base10):
            return (-1)
        nnum = nnum + base10[d2]
        r2 = (r1 - 601) % b2  # and residue after that
        if r2 < 601:  # No third digit. (form N12ZZ)
            nnum = nnum + suffix(r2)
        else:
            d3 = (r2 - 601) // 951 # Three-digits have extended suffix.
            if d3 < 0 or d3 >= len(base10):
                return (-1)
            r3 = (r2 - 601) % 951
            nnum = nnum + base10[d3] + suffix(r3)
    return (nnum)
    
def tail_to_icao(tail):
    if len(tail.rstrip()) <= 0:
        return (-1)
    tail_u = tail.upper()
    tail_u = tail_u.rstrip()
    if tail_u[0] != 'N':
        return (-1)
    icao_int = icaooffset
    icao_int = icao_int + base9.find(tail_u[1]) * b1
    if len(tail_u) == 2: # simple 'N3' etc.
        return (hex(icao_int).upper()[2 :])
    d2 = base10.find(tail_u[2])
    if d2 == -1: # Form N1A
        icao_int = icao_int + enc_suffix(tail_u[2:4])
        return (hex(icao_int).upper()[2 : ])
    else: # Form N11... or N111..
        icao_int = icao_int + d2 * b2 + 601
        try:
            d3 = base10.find(tail_u[3])
        except:
            return(-1) # Nothing there, bomb
        # End try:
        if d3 > -1: #Form N111 Suffix is base 35.
            icao_int = icao_int + d3 * 951 + 601
            icao_int = icao_int + enc_suffix(tail_u[4:6])
            return (hex(icao_int).upper()[2 : ])
        else:  #Form N11A
            icao_int = icao_int + enc_suffix(tail_u[3:5])
            return (hex(icao_int).upper()[2 : ])

#%% =============================================================================
# Routine to convert UTC date/time to local date/time. Input is a UTC date/time
#  string, and 'type' is a code indicating the order of date components:
#   'type' = 'ci' means UTC date/time like 2018/7/23 21:51:25.
#   'type' = 'us' means UTC date/time like 7/23/2018 21:51:25
# Return is the corresponding local time in UNIX epoch time, the local date
# string (e.g., 2018/9/5), and the local time string (e.g., 21:34:56).
# =============================================================================
def convert_utc_to_local(utc_str, type):
#    tm_dst_idx  = 8 # Index into time structure for DST flag
    # First clear any fractional seconds content
    try:
        gmt_str = utc_str[ : utc_str.rindex('.')]
    except:
        gmt_str = utc_str
    # End try:
    
    # Then set up the conversion format string
    if type == 'us':
        fmt_str = '%m/%d/%Y %H:%M:%S' # US style
    elif type == 'ci':
        fmt_str = '%Y/%m/%d %H:%M:%S' # Canadian style
    else:
        print('Unknown date/time type: {0}'.format(type))
        sys.exit() # Bughalt
    # End if type == 'us': ...
    
    # Get a date/time structure for the input GMT string
    dt_struct = tt.strptime(gmt_str, fmt_str)
    gmt_epoch = cal.timegm(dt_struct) # Convert to a GMT UNIX epoch time
    # Get a local date/time structure for the GMT UNIX epoch
    loc_dt_struct = tt.localtime(gmt_epoch)
#    print(loc_dt_struct)
    # Adjust time if DST is set
#    if loc_dt_struct[tm_dst_idx] == 1:
#        gmt_epoch += 3600
#        loc_dt_struct = tt.localtime(gmt_epoch)
    # End if loc_dt_struct[tm_dst_idx] == 1:
    # Convert to local UNIX epoch time
    loc_dt_unix = cal.timegm(loc_dt_struct)
    
    # Convert to a date/time string in local time zone
    loc_dt_str = tt.strftime('%Y/%m/%d %H:%M:%S', loc_dt_struct)
    # Split the date/time string into separate date and time strings
    vdate, vtime = loc_dt_str.split(' ')
    
    return (loc_dt_unix, vdate, vtime)

# **********************************

#%% ===========================================================================
# Routine to fetch OS type and return simple name
# =============================================================================
def get_os_type():
    os_name = pf.platform() # Get full os description
    return(os_name[ : os_name.index('-')].lower())
# End def get_os_type():


#%% ===========================================================================
# Routine to find FlightAware feeder device on local network. Works by finding
# source host IP address and iterating across the remaining local network
# addresses, trying to open the meta data source on port 8080. The function
# accepts a parameter specifying the IP address we think is correct.
# =============================================================================

# Utility routine to test if a given ip address is the feeder
def test_ip_adr(ip_try):
    #Useful constants for filtering observations
    http_get_ok = 200 # Response code for successful get request
    req_abrt = 2 # Response timeout (sec) for http request

    test_url = 'http://' + ip_try + ':8080/data/receiver.json'
    
    # Try to get the meta data
    try:
        response = req.get(test_url, timeout=req_abrt)
    except:
        return(False) # No reply so return nil
    # End try:
    
    # OK so far, see if we got usable json
    if response.status_code == http_get_ok: # If successful,
        try: # Try to decode the json
            response.json()
            response.close() # Close the connection
            return(True) # Return with our success
        except: # Problem here
            response.close() # Close the connection
            return(False) # Make another try
    # Here we got an unsuccessful HTTP response from feeder
    else:
        response.close() # Close the connection
        return(False) # Return failure
    # End if response.status_code == http_get_ok:
    
# End def test_ip_adr(ip_try):


#%% ===========================================================================
# Routine to get the network interface data structure (see sample below).
# It returns a list of
# active IP addresses
# 0) ['Iface: wlan0 Index: 3 HWAddr: B8:27:EB:50:CA:52:',
# 1) 'Addr:None Bcast:None Mask:None', 'MTU: 1500 Metric: 1 Txqueuelen: 1000',
# 2) 'Flags:',
# 3) '\tBroadcast address valid.',
# 4) '\tSupports multicast.',
# 5) ''],
# 0) ['Iface: eth0 Index: 2 HWAddr: B8:27:EB:05:9F:07:',
# 1) 'Addr:192.150.23.51 Bcast:192.150.23.255 Mask:255.255.255.0',
# 2) 'MTU: 1500 Metric: 1 Txqueuelen: 1000',
# 3) 'Flags:',
# 4) '\tInterface is up.', '\tBroadcast address
# valid.', '\tSupports multicast.', '\tResources allocated.', '']
# =============================================================================

def get_ip_info():
    os_sw = get_os_type()
    if os_sw == 'windows':
        import socket as skt  
        # Find our host name and IP address
        try:
            host_name = skt.gethostname()
            host_ip = skt.gethostbyname(host_name)
#            ip_base = host_ip[ : host_ip.rindex('.')] + '.'
        except:
            print('Error: Unable to get Windows Hostname and IP')
            sys.exit() # Bughlt
        # End try:
        
        return([host_ip]) # Got it, return as list
    # Now see if we are on a UNIX
    elif os_sw != 'unix' and os_sw != 'linux':
        print('Invalid OS ID: {0}'.format(os_sw))
        sys.exit() # Bughlt
    # End if os_sw == 'windows':...
    
    # Here we are onlinux, import needed package
    import pyiface as ni
    network_list = {} # Place to collect network information
    # Collect the list of net interface data structures
    try:
        networks = ni.getIfaces()
    except:
        print('Error: Unable to get Linux network interface status')
        sys.exit() # Bughlt
    # End try:

    # Loop through the list and extract key data elements, using the following
    # tags to parse the 
    net_name_tag = 'Iface: '
    adr_tag = '\nAddr:'
    state_tag = 'Interface is up.'
    
    for i_net in networks:
       tmp = str(i_net) # Convert the structure to a string
       # Isolate the network name
       tmp = tmp[tmp.index(net_name_tag) + len(net_name_tag) : ].lstrip(' ')
       net_name = tmp[ : tmp.index(' ')]
       # Isolate network address
       tmp = tmp[tmp.index(adr_tag) + len(adr_tag) : ].lstrip(' ')
       net_adr = tmp[ : tmp.index(' ')]
       # Isolate the network status
       if tmp.count(state_tag) > 0:
           net_state = 'active'
       else:
           net_state = 'off-line'
       # End if tmp.count('Interface is up.') > 0:
       
       # Enter this network in the master list
       network_list.update({net_name: [net_adr, net_state]})
    # End for i_net in networks:
    
    # Check for empty list and make a list of the keys
    # A sample of the network list:
    #   {net_name: [address_str, state], ...}
    # where state is either "active" or "off-line".
    # Also note that a dummy local network has the name "lo", which points to
    # the host and typically address '127.0.0.1", which we do not care about
    if network_list == {}:
        return([]) # If no network, return empty list
    else:
        network_keys = list(network_list) # find the list keys
    # End if network_list == {}:
    
    # Now compose the return network list
    ret_list = []
    for l_name in network_keys:
        l_adr, l_state = network_list[l_name]
        if l_name == 'lo' or l_state == 'off-line':
            continue
        else:
            ret_list.append(l_adr)
    # End for l_name in network_keys:
    
    # All done, return what we have
    return(ret_list)
# End def get_ip_info():


#%% Main testing routine
def find_fa_feeder(initial_ip=None):
    #Useful constants for filtering observations
    min_ip = 2 # Step over base IP
    max_ip = 254 # Stop short of the broadcast IP
    max_tries = 10 # Maximum # tries to find IP address (may be booting)
    try_delay = 3 # Delay (sec) between tries
    
    # Loop to find host IP address. This is needed so that if the machine
    # is just booting, the IP address might not be set yet.
    while max_tries > 0:
        # First find our host name and IP address
        try:
            host_ip_list = get_ip_info()
        except:
            print('Error: Unable to get our host IP information')
            sys.exit() # Bughlt
        # End try:
        
        # Now see if the host_ip_list has the expected content (a list
        # IP addresses corresponding to various network connections
        if host_ip_list == []: # Keep trying if empty
            print(max_tries, 'host_ip_list empty')
            max_tries -= 1
            continue
        # End if host_ip_list == 0:
        
        # Now check the IP list contents
        ip_base = ''
        for v_ip in host_ip_list:
            try:
                ip_base = v_ip[ : v_ip.rindex('.')] + '.'
                break # Seems OK, move on
            except:
                print(max_tries, v_ip, host_ip_list)
                continue # Go through the whole list
            # End try... except
        # End for v_ip in host_ip_list:
         
        # See if we are done
        if ip_base != '':
            break # Yes, move on
        else:
            max_tries -= 1 # Decrement # tries allowed
            tt.sleep(try_delay) # Wait a bit
            continue
        # End if ip_base != '':
    # End while max_tries > 0:
    
    # See if we failed
    if max_tries <= 0 or host_ip_list == []:
        return('') # Must not have an active network
    # End if max_tries <= 0:
    
    # See if a guess ip address is supplied
    if initial_ip != None and initial_ip not in host_ip_list:
        success = test_ip_adr(initial_ip) # If so, test it first
        if success == True:
            return(initial_ip) # Still there, return the value
        # End if success == True:
    # End if initial_ip != None and initial_ip not in host_ip_list:
    
    # No go; have to work to find the feeder if present
    success = False # Assume no success
    # Extract the base IP address: n.n.n. -- this assumes the host is on
    # only one network
#    ip_base = host_ip_list[0][ : host_ip_list[0].rindex('.')] + '.'
    # Now loop through possible IP addresses
    for i_adr in range(min_ip, max_ip):
        ip_try = ip_base + str(i_adr) # Next IP to try
        if ip_try in host_ip_list:
            continue # Ignore our own IP addresses
        else:
            success = test_ip_adr(ip_try)
            if success == True:
                return(ip_try)
            else:
                continue # No go, try the next IP
            # End if success == True:
        # End if ip_try in host_ip_list:
    # End for i_adr in range(min_ip, max_ip):
    
    # Here we must not have found the feeder
    return('') # Couldn't find it

# End def find_fa_feeder():


#%% ===========================================================================
# Routine to fetch the contents of a json type configuration file
# =============================================================================
def get_config_file(config_path):
    try:
        with open(config_path, 'r') as f_in:
            config_data = json.loads(f_in.read()) # Unpack the file
            f_in.close() # Done reading this file
            return(config_data)
    except:
        print('Error: cannot find .config file')
        return({}) # Return null dict
# End def get_config_file(config_path):


#%% ===========================================================================
# Routine to write the contents of a json type configuration file
# =============================================================================
def write_config_file(config_path, config_contents):
    try:
        with open(config_path, 'w') as f_out:
            json.dump(config_contents, f_out) # Unpack the file
            f_out.close() # Done reading this file
            return(True) # Indicate success
    except:
        print('Error: cannot write .config file')
        return(False) # Indicate failure
# End def write_config_file(config_path, config_contents):

