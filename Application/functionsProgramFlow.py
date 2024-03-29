# This file contains functions calls to be used in the main.py script.
# It basically groups together calls to functionsEarthworks to make program flow easier to follow.

from functionsEarthworks import *

def loadSurveyData():
    # Returns a pandas dataframe with the survey data
    print('Loading survey data.')
    dfCoordinates = pd.read_csv('gpsDataUTM.csv') # reads data into dataframe
    pointCount = dfCoordinates['x'].count() # count how many points are available
    print('{x} points collected.'.format(x=pointCount))
    return dfCoordinates

def createRelativeDataframe(dfCoordinates):
    # Returns ordered dataframe with relative distance from origin

    # Adding new info to dataframe: distance from origin (common reference to all points)
    print('Adding common reference to point cloud.')
    dfCoordinates['oDist'] = np.vectorize(distanceFromOrigin)(dfCoordinates['x_rel'],
                                                              dfCoordinates['y_rel'],
                                                              dfCoordinates['z_rel'])

    # sorts accordint to distance from the origin.
    dfCoordinates = dfCoordinates.sort_values(by=['oDist'],
                                              ascending=True)

    z_max = dfCoordinates.z_rel.max() # compute maximum relative elevation
    z_max_abs = dfCoordinates.z.max() # compute maximum absolute elevation
    z_min_abs = dfCoordinates.z.min() # compute minimum absolute elevation
    print('Maximum relative terrain elevation: {ele:.2f}'.format(ele=z_max)) # report maximum elevation
    print('Maximum absolute terrain elevation: {ele:.2f}'.format(ele=z_max_abs)) # report maximum elevation
    print('Minimum absolute terrain elevation: {ele:.2f}'.format(ele=z_min_abs)) # report maximum elevation
    return dfCoordinates

def computeOptimalVolumes(dfCoordinates, stepSize=1.0, swellFactor=1.0):
    # Returns dataframe with computed volumes
	# stepSize = the amount of meters to increase the soil leveling at each calculation step
	# cutReuseFactor = accounts for the fact that not all cut volume can be used to fill a volume of equal amount. E.g.: 1.4 cubic meters cut from clay can be used to fill 1 cubic meter elsewhere in the target terrain.

    startTime = datetime.now() # start the clock on this script
    print('------------------------------------')
    print('Computing optimal terrain elevation.')
    dfVolumes = pd.DataFrame([])
    z_max = dfCoordinates.z_rel.max() # compute maximum relative elevation
    checkElevations = np.arange(0,z_max,stepSize) # check elevations in step size of X meters
    iterations = len(checkElevations)-1
    iterationCounter = 0
    
    
    for desiredElevation in checkElevations: # calculate cut and fill for all elevations store results in a pandas dataframe
        cutVol, cutErr, fillVol, fillErr = computePointCloudVolume(dfCoordinates,elevation = desiredElevation, enablePrompts=False)

        # Append computed values to pandas dataframe
        dfEntry = pd.Series(dict(
                                elevation=desiredElevation,
                                cut=cutVol,
                                fill=fillVol,
                                difference=abs(cutVol-fillVol),
                                cutAccError=cutErr,
                                fillAccError=fillErr,
                                usableCut = cutVol / swellFactor))
        dfVolumes = dfVolumes.append(dfEntry,ignore_index=True)
        printProgressBar(iterationCounter, iterations, prefix = 'Progress:', suffix = 'Complete', length = 50) # update progress bar
        iterationCounter += 1

#     print('Optimal condition:')
#     print(dfVolumes[dfVolumes['difference'] == dfVolumes['difference'].min()])
    dfVolumes.to_csv('optimalVolumes.csv',index=False) # save to file
    print('Computed cut and fill volumes saved to file.')

    #Plotting with Bokeh
    x = dfVolumes['elevation'].values
    y1 = dfVolumes['cut'].values
    y2 = dfVolumes['fill'].values
    y3 = dfVolumes['usableCut'].values

    TOOLS = [BoxSelectTool(), HoverTool()]
    p = figure(title="Cut/Fill Volumes X Elevation", tools = TOOLS)
    p.line(x, y1, legend="Cut Volume",line_color="SteelBlue", line_dash="dotdash", line_width=4)
    p.line(x, y2, legend="Fill Volume",line_color="Coral", line_dash="dotdash", line_width=4)
    p.line(x, y3, legend="Usable Cut Volume",line_color="IndianRed", line_dash="dotdash", line_width=4)
    p.legend.location = "top_right"
    p.xaxis.axis_label = 'Elevation (m)'
    p.yaxis.axis_label = 'Volume (㎥)'
    p.yaxis[0].formatter = PrintfTickFormatter(format="%d")

    output_file("plotOptimalVolumesAnalysis.html", title="Cut/Fill Volumes X Elevation")
    show(p)
    print('Script runtime: {t}'.format(t=datetime.now() - startTime))
    print('--------------------------------')
    return dfVolumes
