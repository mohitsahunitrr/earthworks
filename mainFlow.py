
from functionDefinitions import *

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
    print('Maximum relative terrain elevation: {ele:.2f}'.format(ele=z_max)) # report maximum elevation
    return dfCoordinates

def computeVolumesFromElevation(dfCoordinates): # calculate volumes based on given elevation
    desiredElevation = getNumericalInput('Please input desired terrain level: ')

    startTime = datetime.now() # start the clock on this script
    # splitting point cloud for cut and fill computation
    if(desiredElevation != 0.0):
        print('-------------------------------------------')
        print('Calculating amount of fill volume required.')
        dfFill = dfCoordinates[(dfCoordinates['z_rel'] < desiredElevation)]
        totalVolume, totalError = computeVolumePointCloud(dfFill, how='fill', enablePrompts=True)
        print('The total fill volume is: {v:.2f} cubic meters.'.format(v=totalVolume))
        print('Accumutaled integration error: {e}.'.format(e=totalError))

    print('------------------------------------------')
    print('Calculating amount of cut volume required.')
    dfCut = dfCoordinates[(dfCoordinates['z_rel'] >= desiredElevation)]

    # update z_rel = z_rel - desiredElevation
    pd.options.mode.chained_assignment = None  # default='warn'
    dfCut['z_rel'] = dfCut.z_rel.apply(lambda x: x-desiredElevation) # update z_rel = z_rel - desiredElevation
    pd.options.mode.chained_assignment = 'warn'  # default='warn'

    totalVolume, totalError = computeVolumePointCloud(dfCut, how='cut', enablePrompts=True)
    print('The total cut volume is: {v:.2f} cubic meters.'.format(v=totalVolume))
    print('Accumutaled integration error: {e}.'.format(e=totalError))
    print('Computation process completed.')
    print('Script runtime: {t}'.format(t=datetime.now() - startTime))
    print('---------------------------')

def computeOptimalVolumes(dfCoordinates, stepSize=1.0):
    # Returns dataframe with computed volumes

    startTime = datetime.now() # start the clock on this script
    print('------------------------------------')
    print('Computing optimal terrain elevation.')
    dfVolumes = pd.DataFrame([])
    minimumPCDensity = 2 # minimum required point cloud density for accurate measurements
    z_max = dfCoordinates.z_rel.max() # compute maximum relative elevation
    checkElevations = np.arange(0,z_max-1,stepSize) # check elevations in step size of X meters
    iterations = len(checkElevations)-1
    iterationCounter = 0
    for desiredElevation in checkElevations: # calculate cut and fill for all elevations store results in a pandas dataframe
        # Compute fill
        if (desiredElevation == 0.0): # fill volume is zero; calcule cut only
            fillVolume = 0.0
            fillError = 0.0
            fillPoints = 0.0
        else: # calculate fill
            dfFill = dfCoordinates[(dfCoordinates['z_rel'] < desiredElevation)]
            fillPoints = dfFill['z_rel'].count()
            if (fillPoints < minimumPCDensity):
                printProgressBar(iterationCounter, iterations, prefix = 'Progress:', suffix = 'Complete', length = 50) # update progress bar
                iterationCounter += 1
                continue # if there's less than X points in the point cloud, skip this iteration
            fillVolume, fillError = computeVolumePointCloud(dfFill, how='fill', enablePrompts=False)

        # Compute cut
        dfCut = dfCoordinates[(dfCoordinates['z_rel'] >= desiredElevation)]
        cutPoints = dfCut['z_rel'].count()
        if (cutPoints < minimumPCDensity):
            printProgressBar(iterationCounter, iterations, prefix = 'Progress:', suffix = 'Complete', length = 50) # update progress bar
            iterationCounter += 1
            continue # if there's less than 20 points in the point cloud, skip this iteration
        pd.options.mode.chained_assignment = None  # default='warn'
        dfCut['z_rel'] = dfCut.z_rel.apply(lambda x: x-desiredElevation) # update z_rel = z_rel - desiredElevation
        pd.options.mode.chained_assignment = 'warn'  # default='warn'
        cutVolume, cutError = computeVolumePointCloud(dfCut, how='cut', enablePrompts=False)

        # Append computed values to pandas dataframe
        dfEntry = pd.Series(dict(
                                elevation=desiredElevation,
                                cut=cutVolume,
                                fill=fillVolume,
                                difference=abs(cutVolume-fillVolume),
                                cutAccError=cutError,
                                fillAccError=fillError,
                                fillPoints=fillPoints,
                                cutPoints=cutPoints))
        dfVolumes = dfVolumes.append(dfEntry,ignore_index=True)
        printProgressBar(iterationCounter, iterations, prefix = 'Progress:', suffix = 'Complete', length = 50) # update progress bar
        iterationCounter += 1


    print('Optimal condition:')
    print(dfVolumes[dfVolumes['difference'] == dfVolumes['difference'].min()])
    dfVolumes.to_csv('optimalVolumes.csv',index=False) # save to file
    print('Computed cut and fill volumes saved to file.')

    #Plotting with Bokeh
    x = dfVolumes['elevation'].values
    y1 = dfVolumes['cut'].values
    y2 = dfVolumes['fill'].values

    TOOLS = [BoxSelectTool(), HoverTool()]
    p = figure(title="Cut/Fill Volumes X Elevation", tools = TOOLS)
    p.line(x, y1, legend="Cut Volume",line_color="SteelBlue", line_dash="dotdash", line_width=4)
    p.line(x, y2, legend="Fill Volume",line_color="Coral", line_dash="dotdash", line_width=4)
    p.legend.location = "top_right"

    output_file("plot.html", title="Cut/Fill Volumes X Elevation")
    show(p)
    print('Script runtime: {t}'.format(t=datetime.now() - startTime))
    print('--------------------------------')
    return dfVolumes
