# Update on 23.MAY.2017:
# As the Machine Learning approach is taking to long to generate a usable dataset, I've decided to go on a different path to compute volume:
# >> Group point 3 at a time, buid a triangular mesh, cast a shadow on the xy plane (z=0) and calcule que volume of the generated solid using a double integral

# Imports
import math as m
import pandas as pd
import numpy as np
import scipy as sp
import os
from scipy import integrate
import random

# Imports for plotting
my_plotly_api_key = os.environ.get('MY_PLOTLY_API_KEY') # retrive api_key from operating system
import plotly
plotly.tools.set_credentials_file(username='agu3rra', api_key=my_plotly_api_key) # setting up credentials; Plotly is an online service.
import plotly.plotly as py # import graphics library
import plotly.graph_objs as go

#-----#-----#-----#-----#-----#-----#-----#-----#-----#-----#-----#-----#-----#
# FUNCTIONS...

def printProgressBar (iteration, total, prefix = '', suffix = '', decimals = 1, length = 100, fill = '█'):
    # Code extract from stackoverflow :) just like magic!
    """
    Call in a loop to create terminal progress bar
    @params:
        iteration   - Required  : current iteration (Int)
        total       - Required  : total iterations (Int)
        prefix      - Optional  : prefix string (Str)
        suffix      - Optional  : suffix string (Str)
        decimals    - Optional  : positive number of decimals in percent complete (Int)
        length      - Optional  : character length of bar (Int)
        fill        - Optional  : bar fill character (Str)
    """
    percent = ("{0:." + str(decimals) + "f}").format(100 * (iteration / float(total)))
    filledLength = int(length * iteration // total)
    bar = fill * filledLength + '-' * (length - filledLength)
    print('\r%s |%s| %s%% %s' % (prefix, bar, percent, suffix), end = '\r')
    # Print New Line on Complete
    if iteration == total:
        print()

def distanceFromOrigin(x,y,z):
    # compute distance from origin <0,0,0>
    point = np.array([x,y,z]) # place columns into an array <x,y,z>
    origin = np.zeros(3) # create origin <0,0,0>
    return np.linalg.norm(point-origin) # compute norm

def computeLineEquation(A,B):
    # computes line equation given 2 points: A and B
    # Both A and B need to be numpy arrays

    if (B[0]-A[0]) == 0: # Check if line is parallel to y axis (zero divide)
        #print("Zero division. Line is parallel to y axis. x={x}".format(x=A[0]))
        return np.array([None,None])
    else: # detect slope and intersection
        m = (B[1]-A[1])/(B[0]-A[0]) # slope
        xo = A[0]
        yo = A[1]
        c = -m*xo+yo
        #print("The line equation is y = {m}x + {c}".format(m=m,c=c))
        return np.array([m,c]) # returns slope and constant in numpy array format

def computeVolume(A,B,C):
    # computes volume given 3 points using double integral, line and plane equations
    # A, B and C are numpy arrays

    # Setting up plane equation
    AB = B-A # vector within plane
    BC = C-B # vector within plane
    NV = np.cross(AB,BC) # vector that is normal to plane

    # Plane values; plane equation is a*(x-xo)+b*(y-yo)+c*(z-zo)=0
    a = NV[0]
    b = NV[1]
    c = NV[2]
    xo = A[0]
    yo = A[1]
    zo = A[2]

    # Compute line equations:
    slopeAB, constantAB = computeLineEquation(A,B)
    slopeBC, constantBC = computeLineEquation(B,C)
    slopeAC, constantAC = computeLineEquation(A,C)

    # Compute double integral
    if ((slopeAC is not None) and (slopeAB is not None)): # if slopes are defined
        volume1, error1 = integrate.dblquad(lambda y, x: ((-a*(x-xo)-b*(y-yo))/c)+zo,
                                            A[0],
                                            B[0],
                                            lambda x: slopeAB*x+constantAB,
                                            lambda x: slopeAC*x+constantAC)
    else:
        volume1 = 0.0
    if ((slopeAC is not None) and (slopeBC is not None)): # if slopes are defined
        volume2, error2 = integrate.dblquad(lambda y, x: ((-a*(x-xo)-b*(y-yo))/c)+zo,
                                            B[0],
                                            C[0],
                                            lambda x: slopeAC*x+constantAC,
                                            lambda x: slopeBC*x+constantBC)
    else:
        volume2 = 0.0
    return abs(volume1)+abs(volume2) # return total volume

#-----#-----#-----#-----#-----#-----#-----#-----#-----#-----#-----#-----#-----#
# MAIN...

# Data loading
print('Loading survey data.')
dfCoordinates = pd.read_csv('gpsDataUTM.csv') # reads data into dataframe
pointCount = dfCoordinates['x'].count()
print('{x} points collected.'.format(x=pointCount))

# Adding new info to dataframe: distance from origin (common reference to all points)
print('Adding common reference to point cloud.')
dfCoordinates['oDist'] = np.vectorize(distanceFromOrigin)(dfCoordinates['x_rel'],
                                                          dfCoordinates['y_rel'],
                                                          dfCoordinates['z_rel'])

# sorts accordint to distance from the origin.
dfCoordinates = dfCoordinates.sort_values(by=['oDist'],
                                          ascending=True)

# Required number of loops to compute total volume = number of points - 1
totalVolume = 0.0 # initialize volume summation holder
iteration = 0
print('Computing volumes from triagular meshes.')
for i in range(dfCoordinates['x'].count()-2): # iterate thru all groups of 3 points in ascending order from origin.
    s1 = dfCoordinates.iloc[i] # get series (row entry)
    s2 = dfCoordinates.iloc[i+1]
    s3 = dfCoordinates.iloc[i+2]

    dfAnalysis = pd.DataFrame([]) # build dataframe composed of these 3 entry set
    dfAnalysis = dfAnalysis.append(s1,ignore_index=True)
    dfAnalysis = dfAnalysis.append(s2,ignore_index=True)
    dfAnalysis = dfAnalysis.append(s3,ignore_index=True)
    dfAnalysis = dfAnalysis.sort_values(by=['x_rel'], ascending=True)# order by lowest x_rel >> A,B,C

    A = pd.to_numeric(dfAnalysis.iloc[0][['x_rel','y_rel','z_rel']]).as_matrix()
    B = pd.to_numeric(dfAnalysis.iloc[1][['x_rel','y_rel','z_rel']]).as_matrix()
    C = pd.to_numeric(dfAnalysis.iloc[2][['x_rel','y_rel','z_rel']]).as_matrix()

    # Compute line equations, plane equations and volume
    volume = computeVolume(A,B,C)

    # Update Progress Bar
    iteration += 1
    printProgressBar(iteration, pointCount-2, prefix = 'Progress:', suffix = 'Complete', length = 50)

    totalVolume += volume # add to total volume
print('Program execution complete.')
print('The total volume is: {v} cubic meters.'.format(v=totalVolume))
