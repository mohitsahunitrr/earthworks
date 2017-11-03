# Given the following points, generate a random set of points contained within each of the planes defined by them
import numpy as np
import pandas as pd
import plotly
import plotly.plotly as py # import graphics library
import plotly.graph_objs as go
from plotly.offline import download_plotlyjs, plot
import random
import pickle

def planeEquation(P1,P2,P3, xRange, yRange, linearSpaceSize=1000, randomPointsCount=500):
    # returns a pandas dataframe with collection of X,Y,Z coordinates

    # P1,P2,P3 are expected to be Pandas Series with x,y,z columns
    # xRange is a numpy array containing from and to values for X to be evaluated.
    # yRange follows the same logic as xRange
    # randomPointsCount is the number of points to be returned into the dataframe
    # linearSpaceSize is the amount of points to be generated in the linear space to evaluate the plane Z

    # Error handling
    if ((len(xRange) != 2) or (len(yRange) != 2)):
        print('argument size error')
        return None

    # Generating linear space
    x = np.linspace(xRange[0],xRange[1],num=linearSpaceSize) # generate linear space for x values
    y = np.linspace(yRange[0],yRange[1],num=linearSpaceSize)
    xGrid, yGrid = np.meshgrid(x,y) # generate mesh grid for plotting sample data

    planeVectorOne = P1.values - P2.values # a vector within the plane
    planeVectorTwo = P1.values - P3.values # a vector within the plane
    perpendicularVector = np.cross(planeVectorOne, planeVectorTwo) # plane equation coeficients obtained <a,b,c>
    # saving constants to literals
    a = perpendicularVector[0]
    b = perpendicularVector[1]
    c = perpendicularVector[2]
    xo = P1.x
    yo = P1.y
    zo = P1.z
    z = ((-a*(xGrid-xo)-b*(yGrid-yo))/c)+zo # Plane equation a(x-xo)+b(y-yo)+c(z-zo)=0 with isolated z:

    pointsInGrid = z.shape[0]
    randomIndexesX = random.sample(range(pointsInGrid), randomPointsCount) # generate random list of x points, where x is the number of points collected by the GPS
    randomIndexesY = random.sample(range(pointsInGrid), randomPointsCount)
    # Generate samples for plane
    sample = pd.DataFrame([]) # initialize new dataframe for sample storage
    for i in range(randomPointsCount):
        x_value = xGrid[randomIndexesX[i]][randomIndexesX[i]] # obtain value of corresponding random value from the xGrid
        y_value = yGrid[randomIndexesY[i]][randomIndexesY[i]]
        z_value = z[randomIndexesX[i]][randomIndexesY[i]] # Corresponding z value evaluated for x,y
        samplePoint = pd.Series(dict(x=x_value,
                                     y=y_value,
                                     z=z_value))
        sample = sample.append(samplePoint,ignore_index=True) # append newly converted data to dataframe

    return sample

def plotScatter3D(my3Ddataframe,name='Some Graph',color='rgba(217, 217, 217, 0.14)',plotFile='plot.html'):
    trace = go.Scatter3d(
        x = my3Ddataframe.x,
        y = my3Ddataframe.y,
        z = my3Ddataframe.z,
        name = name,
        mode='markers',
        marker=dict(
            size=4,
            line=dict(
                color=color,
                width=0.5
            ),
            opacity=0.8
        ),
        connectgaps=False
    )
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
    fig = go.Figure(data=[trace],layout=layout)
    return plot(fig,filename=plotFile)

# My collection of known points
P1 = np.array([[0,0,0]])
P2 = np.array([[5,0,0]])
P3 = np.array([[8,0,0]])
P4 = np.array([[13,0,0]])
P5 = np.array([[0,0,2]])
P6 = np.array([[5,0,2]])
P7 = np.array([[8,0,1]])
P8 = np.array([[13,0,1]])
P9 = np.array([[0,0,7]])
P10 = np.array([[11,0,7]])
P11 = np.array([[0,4,0]])
P12 = np.array([[5,4,0]])
P13 = np.array([[8,4,0]])
P14 = np.array([[13,4,0]])
P15 = np.array([[0,4,2]])
P16 = np.array([[5,4,2]])
P17 = np.array([[8,4,1]])
P18 = np.array([[13,4,1]])
P19 = np.array([[0,4,7]])

# fuse them into a single array
PNs = np.concatenate([P1,P2,P3,
                    P4,P5,P6,
                    P7,P8,P9,
                    P10,P11,P12,
                    P13,P14,P15,
                    P16,P17,P18,P19])
data = pd.DataFrame(PNs,columns=['x','y','z']) # creating a corresponding dataframe

# Plotting data to visualize and make sure it is as expected.
#var = plotScatter3D(data)

# Generate point cloud from planes

df1 = planeEquation(data.iloc[8],
                    data.iloc[5],
                    data.iloc[15],
                    xRange=np.array([0.0,5.0]),
                    yRange=np.array([0.0,4.0])) # Plane: P9,P6,P16
df2 = planeEquation(data.iloc[1],
                    data.iloc[2],
                    data.iloc[12],
                    xRange=np.array([5.0,8.0]),
                    yRange=np.array([0.0,4.0]))
df3 = planeEquation(data.iloc[9],
                    data.iloc[17],
                    data.iloc[16],
                    xRange=np.array([8.0,13.0]),
                    yRange=np.array([0.0,4.0]))
df = pd.concat([df1,df2,df3])
var = plotScatter3D(df)
print('{p} points generated thru equations.'.format(p=df.shape[0]))
print('Point cloud density: {x} points per cubic meter'.format(x=df.shape[0]/(data.x.max()*data.y.max()*data.z.max())))
df=df.rename(columns={'x':'x_rel','y':'y_rel','z':'z_rel'})
df.to_csv('generatedPointCloud.csv')
