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

# Calculate volume of earth from the lowest measured point
