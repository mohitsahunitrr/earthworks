# HEADER
# Title: Python Earthworks
# Author: Andre Guerra (agu3rra@gmail.com)
# Date: May 10th 2017
# --
# Description:
# This program implements volume calculations for earthing works in engineering
# Inputs:
# 1. gpx data from GPS collected on the field. It must contain latitude, longitude and elevation
# 2. Reference plane: Determine the coordiantes that define a reference plane to be leveled.
# Outputs:
# 1. Cut and fill volumes required;
# 2. Graphical output showing the generated surface based on the survey data.
# 3. Graphical output of the reference plane used
# ----- # ----- # ----- # ----- # ----- # ----- # ----- # ----- # ----- # -----
# Imports
import math as m # math library
from scipy.spatial import distance
import numpy as np
import scipy as sp
import pandas as pd

#import plotly # import graphics library
#plotly.tools.set_credentials_file(username='agu3rra', api_key='b6WWbmeqKfYxPkQJBnw8') # setting up credentials; Plotly is an online service.
import matplotlib.pyplot as plt
import pylab
from mpl_toolkits.mplot3d import Axes3D

# ----- # ----- # ----- # ----- # ----- # ----- # ----- # ----- # ----- # -----
# Global variables
a = 6378137.0 # semi-major axis a using WGS84 standard (World Geodetic System)
b = 6356752.314245 # semi-minor axis b using WGS84 standard
f = (a-b)/a # first flattening of the Earth taken into account
e2 = 2*f-m.pow(f,2) # e squared parameter

# ----- # ----- # ----- # ----- # ----- # ----- # ----- # ----- # ----- # -----
# Functions
def deg2rad (degrees):
    # Converts from degrees to radians
    return degrees*m.pi/180

def rad2deg (radians):
    # Converts from radians to degrees
    return radians*180/m.pi

def calculateV (lat):
    # Return v for the given latitude in degrees
    latRad = deg2rad(lat) # converts to radians
    return a/m.sqrt(1-e2*m.pow(m.sin(latRad),2))

def geo2cat (lat,lon,ele):
    # Returns point in Cartesian coordinates given its Geographic coordinates
    # Data returned in Pandas Series form

    v = calculateV(lat)

    latRad = deg2rad(lat)
    lonRad = deg2rad(lon)
    z = (v*(1-e2)+ele)*m.sin(latRad)
    y = (v+ele)*m.cos(latRad)*m.sin(lonRad)
    x = (v+ele)*m.cos(latRad)*m.cos(lonRad)

    pointC = pd.Series(dict(x=x, y=y, z=z))
    return pointC # returns point in Cartesian coordinates

# ----- # ----- # ----- # ----- # ----- # ----- # ----- # ----- # ----- # -----
# Test code for distance measurements and conversion from Geographic to
# Cartesian Coordinates

# pa = geo2cat(-24.9361993186,-51.3906013593,883.16)
# pb = geo2cat(-24.9356264155,-51.3912779465,882.69)
#
# dst = distance.euclidean(pa,pb)
# print(dst)
# print(pa)
# print(pb)

# ----- # ----- # ----- # ----- # ----- # ----- # ----- # ----- # ----- # -----
# MAIN CODE

# Reading data from CSV file and placing it on a numpy array
dfGPS = pd.read_csv('gpsData.csv', sep=',') # import csv data into pandas dataframe

# Add Cartesian coordinates to data frame
#print(dfGPS[['latitude','longitude','elevation']].apply(geo2cat))
#dfGPS['x'], dfGPS['y'], dfGPS['z'] = geo2cat(dfGPS['latitude'], dfGPS['longitude'], dfGPS['elevation'])
dfGPS['x'], dfGPS['y'], dfGPS['z'] = geo2cat(dfGPS['latitude'], dfGPS['longitude'], dfGPS['elevation'])
print(dfGPS.head(3))

# Plotting data
# fig1 = pylab.figure()
# ax = Axes3D(fig1)
# x = dfGPS[['latitude']]
# y = dfGPS[['longitude']]
# z = dfGPS[['elevation']]
#
#
# ax.scatter(x,y,z)
# plt.show()
