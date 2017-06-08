# Function definitions

# Imports
import math as m
import pandas as pd
import numpy as np
import scipy as sp
import os
from scipy import integrate
import utm # library for UTM projection map conversion
from datetime import datetime
import time
from scipy.spatial import ConvexHull

# XML parsing libraries
from xml.dom.minidom import parse
import xml.dom.minidom

# Imports for plotting
my_plotly_api_key = os.environ.get('MY_PLOTLY_API_KEY') # retrive api_key from operating system
import plotly
plotly.tools.set_credentials_file(username='agu3rra', api_key=my_plotly_api_key) # setting up credentials; Plotly is an online service.
import plotly.plotly as py # import graphics library
import plotly.graph_objs as go
from plotly.offline import download_plotlyjs, plot

# Plotting with Bokeh
from bokeh.plotting import figure, show, output_file
from bokeh.models import HoverTool, BoxSelectTool

def getNumericalInput(prompt=''):
    # get input from user.
    # loop until one of the options is selected
    # options is a list with the available options
    while (True):
        userInput = input(prompt)
        try:
            userInput = float(userInput)
            break
        except ValueError:
            print("Invalid. Input must be numerical. Try again.")
    return userInput

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

def parseGpxFile (filePath):
    # parses .gpx file and saves it into a csv file called gpsData.csv
    DOMTree = xml.dom.minidom.parse(filePath)
    collection = DOMTree.documentElement

    # Get all track points in the collection
    trackPoints = collection.getElementsByTagName("trkpt")

    # Read in all the data of interest
    file = open("gpsData.csv",'w') # create output file
    file.write("latitude,longitude,elevation\n")

    for point in trackPoints:
        lati = point.getAttribute("lat")
        long = point.getAttribute("lon")
        altx = point.getElementsByTagName('ele')[0]
        alti = altx.childNodes[0].data

        # all data types are str; checked: print(type(lati),type(long),type(alti))
        file.write(lati+","+long+","+alti+"\n") # output to file and process next point
    file.close() #close output file

def generateUTM (sourcePath,destinationPath):
    # reads csv file with parsed latitude, longitude and elevation. Outputs another csv file containing additional UTM coordinates
    # both inputs are strings
    dfGPS = pd.read_csv(sourcePath, sep=',') # import csv data into pandas dataframe
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
    dfUTM.to_csv(destinationPath,index=False) # save to file

def limitsUTM (dfUTM):
    # takes a dataframe with x,y coordinates (latitude,longitude) and converts to UTM coordinates
    # returns a dataframe with converted coordinates
    dfLimits = pd.DataFrame([]) # initialize new dataframe
    for rowIndex, row in dfUTM.iterrows(): #Iterating thru elements in dataframe
        point = utm.from_latlon(row['latitude'],row['longitude']) # convert to UTM coordinates
        pointUTM = pd.Series(dict(
                                latitude=row['latitude'],
                                longitude=row['longitude'],
                                x=point[0],
                                y=point[1],
                                zoneNumber=point[2],
                                zoneLetter=point[3]))
        dfLimits = dfLimits.append(pointUTM, ignore_index=True) # append newly converted data to dataframe
    return dfLimits

def distanceFromOrigin(x,y,z):
    # computes distance from origin <0,0,0>
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

def computeVolumeTriangularMesh(A,B,C):
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
    totalVolume = abs(volume1)+abs(volume2)
    totalError = abs(error1)+abs(error2)
    return [totalVolume, totalError] # return total volume

def computeVolumePointCloud(dfPointCloud, how='cut', enablePrompts=True):
    # given a point cloud (x,y,z coordinates), computes the volume of corresponding solid in relation to z=0 using a sum of triagular meshes
    # dfPointCloud is expected to be a pandas dataframe with relative coordinates (x,y,z)
    # Optional inputs:
    # how = cut/fill; cut = return cut volume; fill = return fill volume (return = cube volume - cut volume, where the cube is delimited by *_max coordinates)

    # Required number of loops to compute total volume = number of points - 1
    totalVolume = 0.0 # initialize volume summation holder
    totalError = 0.0
    iteration = 0
    pointCount = dfPointCloud['x_rel'].count()
    if enablePrompts: print('Computing volume from triangular meshes.')
    for i in range(dfPointCloud['x_rel'].count()-2): # iterate thru all groups of 3 points in ascending order from origin.
        s1 = dfPointCloud.iloc[i] # get series (row entry)
        s2 = dfPointCloud.iloc[i+1]
        s3 = dfPointCloud.iloc[i+2]

        dfAnalysis = pd.DataFrame([]) # build dataframe composed of these 3 entry set
        dfAnalysis = dfAnalysis.append(s1,ignore_index=True)
        dfAnalysis = dfAnalysis.append(s2,ignore_index=True)
        dfAnalysis = dfAnalysis.append(s3,ignore_index=True)
        dfAnalysis = dfAnalysis.sort_values(by=['x_rel'], ascending=True)# order by lowest x_rel >> A,B,C

        A = pd.to_numeric(dfAnalysis.iloc[0][['x_rel','y_rel','z_rel']]).as_matrix()
        B = pd.to_numeric(dfAnalysis.iloc[1][['x_rel','y_rel','z_rel']]).as_matrix()
        C = pd.to_numeric(dfAnalysis.iloc[2][['x_rel','y_rel','z_rel']]).as_matrix()

        # Compute line equations, plane equations and volume
        volume, error = computeVolumeTriangularMesh(A,B,C)

        # Update Progress Bar
        if enablePrompts:
            iteration += 1
            printProgressBar(iteration, pointCount-2, prefix = 'Progress:', suffix = 'Complete', length = 50)

        totalVolume += volume # add to total volume
        totalError += error # accumulate error

    # Returning computed values
    if (how == 'cut'):
        return [totalVolume, totalError]
    elif (how == 'fill'):
        # Obtaining range of point cloud values
        x_max = dfPointCloud['x_rel'].max()
        y_max = dfPointCloud['y_rel'].max()
        z_max = dfPointCloud['z_rel'].max()
        cubeVolume = x_max * y_max * z_max
        #print('{x},{y},{z} >> {c}'.format(x=x_max,y=y_max,z=z_max,c=cubeVolume))
        return [cubeVolume-totalVolume, totalError]
    else:
        print('Invalid argument passed to function call. how must be either \'cut\' or \'fill\'')
        return [None, None]

def plotTerrain(dictPlotData, plotFile = 'plot.html'):
    # Plots a 3D Scatter in Plotly using x,y,z coordinates from dataset
    # dictDataframes is expected to be a dictionary with dataFrame, seriesName and rgba config string
    traces = []
    for entry in dictPlotData:
        trace = go.Scatter3d(
            x = entry.df['x_rel'],
            y = entry.df['y_rel'],
            z = entry.df['z_rel'],
            name = entry.name,
            mode='markers',
            marker=dict(
                size=4,
                line=dict(
                    color=entry.color,
                    width=0.5
                ),
                opacity=0.8
            ),
            connectgaps=False,
            projection=dict(x=dict(show=True, opacity=0.3),
                            y=dict(show=True, opacity=0.3),
                            z=dict(show=True, opacity=0.3))
        )
        traces.append(trace)
    layout = go.Layout(
        autosize=False,
        width=1000,
        height=600,
        margin=go.Margin(
            l=10, # left margin
            r=10, # right margin
            b=10, # below margin
            t=10, # top margin
            pad=4
        ),
        paper_bgcolor='#ffffff',
        #xaxis=dict(color='#234')
        plot_bgcolor='#fff3ff'
        #title='Terrain data'
    )
    fig = go.Figure(data=traces,layout=layout)
    return plot(fig,filename=plotFile)
    # return plot(traces,filename=plotFile)

def filterTerrainLimits(dfSurvey,dfLimits):
    # given a survey dataframe and a dataframe containing terrain boundaries, filters out points ouside of boundaries
    # filtered terrain is returned in a dataframe

    # terrain limits are defined by a quadrilateral polygon (ABCD).
    # for each point in the survey data, check if point projection (x,y coordinates) are inside the quadrilateral
    #   inside: ABCD == PAB + PBC + PAD + PCD

    # Step 1: Check if dfLimits has only 4 points
    if (dfLimits.x_rel.count() != 4):
        print('Error: Terrain isn\'t limited by 4 points.')
        return None

    # Step 2: Name terrain limits ABCD (for program readability)
    A = np.array([dfLimits.iloc[0].x_rel, dfLimits.iloc[0].y_rel])
    B = np.array([dfLimits.iloc[1].x_rel, dfLimits.iloc[1].y_rel])
    C = np.array([dfLimits.iloc[2].x_rel, dfLimits.iloc[2].y_rel])
    D = np.array([dfLimits.iloc[3].x_rel, dfLimits.iloc[3].y_rel])

    # Step 3: Iterate thru points and determine if point is within terrain limits
    dfFiltered = pd.DataFrame([])
    print(dfSurvey.x_rel.count())
    for i in range(dfSurvey.x.count()):
        P = np.array([dfSurvey.iloc[i].x_rel, dfSurvey.iloc[i].y_rel])
        if (pointWithinQuadLimits(P,A,B,C,D)==True):
            dfEntry = pd.Series(dict(x_rel=P[0],
                                     y_rel=P[1],
                                     z_rel=dfSurvey.iloc[i].z_rel)) # adding z coordinate
            dfFiltered = dfFiltered.append(dfEntry,ignore_index=True)
        printProgressBar(i, dfSurvey.x.count()-1, prefix = 'Progress:', suffix = 'Complete', length = 50)
    return dfFiltered

def centroid(arr):
    length = arr.shape[0]
    sum_x = np.sum(arr[:,0])
    sum_y = np.sum(arr[:,1])
    return sum_x/length, sum_y/length

def angleFromCentroid(x,y,xc,yc):
    origin = np.zeros(2) # create origin <0,0>
    centroid = np.array([xc,yc])
    CA = np.array([x,y])-centroid # computes vector CA: centroid -> A
    OC = centroid-origin # computes vector OC: origin -> centroid
    angle1 = m.atan2(OC[1],OC[0]) # computes angle in radians between OC and the x axis
    angle2 = m.atan2(CA[1],CA[0]) # computes angle between CA and the x axis
    angleAC = angle2-angle1
    if (angleAC < 0):
        angleAC += 2*m.pi # for negative angles, sum 2*𝝿 to get range from 0->2𝝿
    return angleAC

def clockwiseArray(arr):
    # retuns arr in a clockwise fashion in a dataframe format
    # arr is a collection of 2D points in the cartesian plane xy; numpy array format expected
    xc,yc = centroid(arr) # computes centroid of the collection of points
    df = pd.DataFrame(arr,columns=['x','y']) # change numpy array into a DataFrame
    df['xc'] = xc # add center to list of entries; Think about how to change this later as it looks ugly in code
    df['yc'] = yc
    df['angle'] = np.vectorize(angleFromCentroid)(df['x'],df['y'],df['xc'],df['yc']) # add new column: angle between point and centroid vector
    df = df.sort_values(by='angle',ascending=False) # sorts according to angle
    return df

def pointWithinQuadLimits(P,A,B,C,D):
    # given a point P, determines whether or not it is inside quadrilateral ABCD
    square = np.array([A,B,C,D])
    sqArea = ConvexHull(square).volume # computes the volume of the convex hull. As we are in 2D, that corresponds to the area

    # sort ABCD in clockwise fashion
    dfSorted = clockwiseArray(square)

    # rearrange ABCD in clockwise order
    A = dfSorted.iloc[0][['x','y']].values
    B = dfSorted.iloc[1][['x','y']].values
    C = dfSorted.iloc[2][['x','y']].values
    D = dfSorted.iloc[3][['x','y']].values

    # inside: ABCD == PAB + PBC + PAD + PCD
    T1 = np.array([P,A,B])
    T2 = np.array([P,B,C])
    T3 = np.array([P,C,D])
    T4 = np.array([P,A,D])

    trArea = 0.0
    trArea += ConvexHull(T1).volume
    trArea += ConvexHull(T2).volume
    trArea += ConvexHull(T3).volume
    trArea += ConvexHull(T4).volume

    if (round(sqArea,2)==round(trArea,2)):
        return True
    else:
        return False

def pointWithingPolygon(P,Poly):
    # To be implemented just for fun:
    # True if point is inside 2D points delimited by Poly; False otherwise.
    return True
