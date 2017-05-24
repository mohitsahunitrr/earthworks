# Main user interface.

from functionDefinitions import *

# Custom functions:
# parseGpxFile # parses input .gpx file
# generateUTM # generates csv file with UTM coordinates
# printProgressBar # function definitions imported from suplementary .py files
# distanceFromOrigin # compute distance from origin <0,0,0>
# computeLineEquation # computes line equation given 2 points: A and B
# computeVolume # computes volume given 3 points using double integral, line and plane equations

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
desiredElevation = getIntegerInput('Please inform the relative elevation to level: ')
desiredElevation = float(desiredElevation)

# splitting point cloud for cut and fill computation
if(desiredElevation != 0.0):
    print('-------------------------------------------')
    print('Calculating amount of fill volume required.')
    dfFill = dfCoordinates[(dfCoordinates['z_rel'] < desiredElevation)]
    totalVolume, totalError = computeVolumePointCloud(dfFill, how='fill')
    print('The total fill volume is: {v:.2f} cubic meters.'.format(v=totalVolume))
    print('Accumutaled integration error: {e}.'.format(e=totalError))

print('------------------------------------------')
print('Calculating amount of cut volume required.')
dfCut = dfCoordinates[(dfCoordinates['z_rel'] >= desiredElevation)]
totalVolume, totalError = computeVolumePointCloud(dfCut, how='cut')
print('The total cut volume is: {v:.2f} cubic meters.'.format(v=totalVolume))
print('Accumutaled integration error: {e}.'.format(e=totalError))
print('---------------------------')
print('Program execution complete.')
