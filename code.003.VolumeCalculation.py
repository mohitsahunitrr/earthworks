# Imports
import pandas as pd
import numpy as np
import scipy as sp
import os
my_plotly_api_key = os.environ.get('MY_PLOTLY_API_KEY') # retrive api_key from operating system
import plotly
plotly.tools.set_credentials_file(username='agu3rra', api_key=my_plotly_api_key) # setting up credentials; Plotly is an online service.
import plotly.plotly as py # import graphics library
import plotly.graph_objs as go

# Data loading
dfCoordinates = pd.read_csv('gpsDataUTM.csv') # reads data into dataframe

#-----#-----#-----#-----#-----#-----#-----#-----#-----#-----#-----#-----#-----#
# Calculate volume of earth from the lowest measured point
# Idea: generate training set to a Neural Network and treat it as a regression problem

# Part 1: Generate training set
# Idea: generate a set of mathematical surface functions z=f(x,y) that go by
# close to the points we're getting from GPS. Use these funcitons to generate a
# set of (x,y,z) points and a double integral to calculate the exact valume of
# the solid delimited by it.

# Better idea: maybe the model can generelize from general space, no need to actually find functions that have values close to our sample set.
# The only remaining challenge is to select only a subset of points that match the input data size (random selection)

# generate mathematical surface functions that have values within the [0:*_max] range
x = np.linspace(0.0,50.0,num=200) # generate linear space for x values
y = np.linspace(0.0,50.0,num=200)
xGrid, yGrid = np.meshgrid(x,y) # generate mesh grid for plotting sample data

z1 = xGrid+yGrid # defining a plane
#z2 = np.sin(xGrid**2 + yGrid**2) / (xGrid**2 + yGrid**2) #
z3 = xGrid**2 + yGrid**2 + 2*xGrid*yGrid - 1
