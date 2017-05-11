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
#import pandas as pd

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
    return radians*180/m/pi

def calculateV (lat):
    # Return v for the given latitude in degrees
    latRad = deg2rad(lat) # converts to radians
    return a/m.sqrt(1-e2*m.pow(m.sin(latRad),2))

def geo2cat (pointG):
    # Returns point in Cartesian coordinates given its Geographic coordinates
    # data returned in a tuple

    #parsing input tuple
    lat = pointG[0] # latitude in degrees
    lon = pointG[1] # longitude in degrees
    alt = pointG[2] # elevation above sea level in meters

    v = calculateV(lat)

    latRad = deg2rad(lat)
    lonRad = deg2rad(lon)
    z = (v*(1-e2)+alt)*m.sin(latRad)
    y = (v+alt)*m.cos(latRad)*m.sin(lonRad)
    x = (v+alt)*m.cos(latRad)*m.cos(lonRad)

    pointC = (x,y,z)
    return pointC # returns point in Cartesian coordinates

# ----- # ----- # ----- # ----- # ----- # ----- # ----- # ----- # ----- # -----
# Test code for distance measurements and conversion from Geographic to
# Cartesian Coordinates

# point1=(-24.9361993186,-51.3906013593,883.16)
# point2=(-24.9356264155,-51.3912779465,882.69)
# pa = geo2cat(point1)
# pb = geo2cat(point2)
#
# dst = distance.euclidean(pa,pb)
# print(dst)

# ----- # ----- # ----- # ----- # ----- # ----- # ----- # ----- # ----- # -----
# MAIN CODE

# Reading data from CSV file and placing it on a numpy array
