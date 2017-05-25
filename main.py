# Main user interface.

from functionDefinitions import *

# Custom functions:
# parseGpxFile # parses input .gpx file
# generateUTM # generates csv file with UTM coordinates
# printProgressBar # function definitions imported from suplementary .py files
# distanceFromOrigin # compute distance from origin <0,0,0>
# computeLineEquation # computes line equation given 2 points: A and B
# computeVolume # computes volume given 3 points using double integral, line and plane equations

startTime = datetime.now() # start the clock on this script

print("Reading .gpx file.")
parseGpxFile('gpsData.gpx') # parse .gpx file
print('XML parsing complete.')

print('Generating UTM coordinates.')
generateUTM('gpsData.csv') # generates csv file with UTM coordinates
print('Process completed.')

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

# Ask user for desired terrain elevation to be leveled
z_max = dfCoordinates.z_rel.max()
print('Maximum relative terrain elevation: {ele:.2f}'.format(ele=z_max))

print('------------------------------------')
print('Select one of the following options:')
print('[1] Calculate volumes for a given terrain elevation.')
print('[2] Calculate terrain elevation for cut equals fill volume.')

while True:
    option = getNumericalInput()
    if option in (1,2):
        break
    else:
        print('Invalid option. Try again.')

if (option==1): # calculate volumes based on given elevation
    desiredElevation = getNumericalInput('Please input desired terrain level: ')

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
    print('---------------------------')
else: # calculate optimal elevation -> cut equals fill >> Option 2
    print('------------------------------------')
    print('Computing optimal terrain elevation.')
    dfVolumes = pd.DataFrame([])
    minimumPCDensity = 2 # minimum required point cloud density for accurate measurements
    checkElevations = np.arange(0,z_max-1,1.5) # check elevations in step size of 0.5 meters
    iterations = len(checkElevations)
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
    p.line(x, y1, legend="Cut Volume",line_color="SteelBlue", line_dash="dotdash")
    p.line(x, y2, legend="Fill Volume",line_color="Coral", line_dash="dotdash")
    p.legend.location = "top_right"

    output_file("plot.html", title="Cut/Fill Volumes X Elevation")
    show(p)

print('Script runtime: {t}'.format(t=datetime.now() - startTime))

    # Plotting dataframe iteration x cut x fill
# traceCut = go.Scatter(
#     x = dfVolumes[['elevation']].values,
#     y = dfVolumes[['cut']].values,
#     name = 'Cut Volume'
# )
# traceFill = go.Scatter(
#     x = dfVolumes[['elevation']].values,
#     y = dfVolumes[['fill']].values,
#     name = 'Fill Volume'
# )
# data = [traceCut, traceFill]
# py.iplot(data, filename='Cut and Fill volumes X Terrain elevation')
# print('Program execution complete.')
