# Imports
import math as m
import pandas as pd
import numpy as np
import scipy as sp
import os
my_plotly_api_key = os.environ.get('MY_PLOTLY_API_KEY') # retrive api_key from operating system
import plotly
plotly.tools.set_credentials_file(username='agu3rra', api_key=my_plotly_api_key) # setting up credentials; Plotly is an online service.
import plotly.plotly as py # import graphics library
import plotly.graph_objs as go
from scipy import integrate
import random
import pickle

# Data loading
print('Loding survey data')
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
#-----#-----#-----#-----#-----#-----#-----#-----#-----#-----#-----#-----#-----#
# FUNCTIONS
def combination(n,k): # Combination of n samples taken k at a time.
    return m.factorial(n)/(m.factorial(n-k)*m.factorial(k))

def combinations(iterable, r):
    # Generates all possible combinations and returns iterable object
    # combinations('ABCD', 2) --> AB AC AD BC BD CD
    # combinations(range(4), 3) --> 012 013 023 123
    pool = tuple(iterable)
    n = len(pool)
    if r > n:
        return
    indices = list(range(r))
    yield tuple(pool[i] for i in indices)
    while True:
        for i in reversed(range(r)):
            if indices[i] != i + n - r:
                break
        else:
            return
        indices[i] += 1
        for j in range(i+1, r):
            indices[j] = indices[j-1] + 1
        yield tuple(pool[i] for i in indices)

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

#-----#-----#-----#-----#-----#-----#-----#-----#-----#-----#-----#-----#-----#
# CODING...
# Determine bounds of interest
x_max = dfCoordinates['x_rel'].max()
y_max = dfCoordinates['y_rel'].max()
z_max = dfCoordinates['z_rel'].max()

# Remember: in terrain measurements, all x, y and z values will be positive
# Dev note: increasing number of samples may be required
x = np.linspace(0.0,x_max,num=500) # generate linear space for x values
y = np.linspace(0.0,y_max,num=500)
xGrid, yGrid = np.meshgrid(x,y) # generate mesh grid for plotting sample data

# define all plane equations that can be obtained from combination of each point 3 at a time.
dfSurvey = dfCoordinates[['x_rel',
                          'y_rel',
                          'z_rel']]
pointsCount = int(dfSurvey.count()[0]) # number of points available
possiblePlanes = combination(155,3) # number of possible combinations of planes
print('Generating %s plane equations.' % possiblePlanes)

# Progress bar
iteration=0 # progrss bar initialization
printProgressBar(iteration, possiblePlanes, prefix = 'Progress:', suffix = 'Complete', length = 50)

planeCombinations = combinations(range(pointsCount),3) # indexes all possible combinations of available points
#planeCombinations = combinations(range(5),3) # reducing set for debugging

mlDataset = pd.DataFrame([]) # initialize new dataframe for the machine learning dataset
# Determine plane equation for each set of 3 points and calculate corresponding volume
for pointSet in planeCombinations:
    point1index = pointSet[0] # index of the first point
    point2index = pointSet[1]
    point3index = pointSet[2]

    # fetching actual points according to index
    point1 = np.array([dfSurvey.iloc[point1index].values[0],
                       dfSurvey.iloc[point1index].values[1],
                       dfSurvey.iloc[point1index].values[2]])
    point2 = np.array([dfSurvey.iloc[point2index].values[0],
                       dfSurvey.iloc[point2index].values[1],
                       dfSurvey.iloc[point2index].values[2]])
    point3 = np.array([dfSurvey.iloc[point3index].values[0],
                       dfSurvey.iloc[point3index].values[1],
                       dfSurvey.iloc[point3index].values[2]])

    planeVectorOne = point2 - point1 # a vector within the plane
    planeVectorTwo = point3 - point2 # a vector within the plane
    perpendicularVector = np.cross(planeVectorOne, planeVectorTwo) # plane equation coeficients obtained <a,b,c>

    # saving constants to literals
    a = perpendicularVector[0]
    b = perpendicularVector[1]
    c = perpendicularVector[2]
    xo = point1[0]
    yo = point1[1]
    zo = point1[2]

    # Plane equation a(x-xo)+b(y-yo)+c(z-zo)=0 with isolated z:
    z = ((-a*(xGrid-xo)-b*(yGrid-yo))/c)+zo

    pointsInGrid = z.shape[0]
    evalutePoints = pointsInGrid - pointsCount # evaluate number of available points within your grid - samples from GPS
    if evalutePoints>0: # normal scenario
        randomIndexesX = random.sample(range(pointsInGrid), pointsCount) # generate random list of x points, where x is the number of points collected by the GPS
        randomIndexesY = random.sample(range(pointsInGrid), pointsCount)
    else: # your grid has less points than colleted from the GPS survey. Increase grid size
        print("Your grid has %s points less than required. Increase grid size." % evaluatePoints)

    mlSample = pd.DataFrame([]) # initialize new dataframe for sample storage

    for i in range(pointsCount):
        x_value = xGrid[randomIndexesX[i]][randomIndexesX[i]] # obtain value of corresponding random value from the xGrid
        y_value = yGrid[randomIndexesY[i]][randomIndexesY[i]]
        z_value = z[randomIndexesX[i]][randomIndexesY[i]] # Corresponding z value evaluated for x,y

        # append data to dataframe
        samplePoint = pd.Series(dict(x=x_value,
                                     y=y_value,
                                     z=z_value))
        mlSample = mlSample.append(samplePoint,
                                   ignore_index=True) # append newly converted data to dataframe

    # the dfTrainingSample contains a set of points for which we need to evaluate the corresponding bounds and volume
    # evaluate max and min bounds
    x_min = mlSample['x'].min()
    x_max = mlSample['x'].max()
    y_min = mlSample['y'].min()
    y_max = mlSample['y'].max()
    # evaluating bounds for z is not required for evaluating the double integral (plane equation is used for z)

    # Evaluating corresponding volume for this point set
    volume = integrate.dblquad(lambda y, x: ((-a*(x-xo)-b*(y-yo))/c)+zo,
                               x_min, x_max,
                               lambda x: y_min, lambda x: y_max)
    volume = volume[0] # saving the computed volume. The second element in the list holds the error.
#     print(dfTrainingSample.head())
#     print(volume)
    # at this point of the code we have a dataframe with corresponding points in a plane and a corresponding volume.
    # This is a sample! We made one! Now on to saving it in a format compatible with the neural network
    # Saving training sample: for 155 data points >> row = 466 elements all x's, all y's, all z's + volume
    # append data to mlDataset

    #create numpy array to store in mlDataframe (single row)
    sampleData = np.concatenate([mlSample['x'].values,
                                 mlSample['y'].values,
                                 mlSample['z'].values])
    datasetSample = pd.Series(dict(inputData = sampleData,
                                   inputLabel = volume))
    mlDataset = mlDataset.append(datasetSample,
                                 ignore_index=True)

    # Update Progress Bar
    iteration += 1
    printProgressBar(iteration, possiblePlanes, prefix = 'Progress:', suffix = 'Complete', length = 50)

# Saving dataset to a pickle
file = open('mlDataset.pickle', 'wb')
pickle.dump(mlDataset, file)
file.close()
