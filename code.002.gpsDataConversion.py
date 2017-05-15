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
import utm # library for UTM projection map conversion

from scipy.spatial import distance
import numpy as np
import scipy as sp
import pandas as pd
import os
my_plotly_api_key = os.environ.get('MY_PLOTLY_API_KEY')
# setting up a key:
# in Terminal:
# export MY_PLOTLY_API_KEY = 'DHAHH3DSAD43D' (EXAMPLE)

import plotly
plotly.tools.set_credentials_file(username='agu3rra', api_key=my_plotly_api_key) # setting up credentials; Plotly is an online service.
import plotly.plotly as py # import graphics library
import plotly.graph_objs as go

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

def geo2car (lat,lon,ele):
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

# Create a Cartesian Coordinates dataframe
dfUTM = pd.DataFrame([]) # initialize new dataframe
for rowIndex, row in dfGPS.iterrows(): #Iterating thru elements in dataframe
    point = utm.from_latlon(row['latitude'],row['longitude']) # convert to UTM coordinates
    pointUTM = pd.Series(dict(
                            x=point[0],
                            y=point[1],
                            z=row['elevation'],
                            zoneNumber=point[2],
                            zoneLetter=point[3]))
    dfUTM = dfUTM.append(pointUTM, ignore_index=True) # append newly converted data to dataframe

# add x_rel, y_rel, z_rel coordinates relative position.
dfUTM['x_rel'] = dfUTM['x'] - dfUTM['x'].min()
dfUTM['y_rel'] = dfUTM['y'] - dfUTM['y'].min()
dfUTM['z_rel'] = dfUTM['z'] - dfUTM['z'].min()
dfUTM.to_csv('gpsDataUTM.csv',index=False) # save to file

#Plotting data
x = dfUTM[['x']].values
y = dfUTM[['y']].values
z = dfUTM[['z']].values

trace1 = go.Scatter3d(
    x=x,
    y=y,
    z=z,
    mode='markers',
    marker=dict(
        size=5,
        line=dict(
            color='rgba(217, 217, 217, 0.14)',
            width=0.5
        ),
        opacity=0.8
    )
)

data = [trace1]
layout = go.Layout(
    margin=dict(
        l=0,
        r=0,
        b=0,
        t=0
    )
)
fig = go.Figure(data=data, layout=layout)
py.iplot(fig, filename='simple-3d-scatter')
