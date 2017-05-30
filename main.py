# Main user interface.

from functionDefinitions import *
from mainFlow import *

# Custom functions:
# parseGpxFile # parses input .gpx file
# generateUTM # generates csv file with UTM coordinates
# printProgressBar # function definitions imported from suplementary .py files
# distanceFromOrigin # compute distance from origin <0,0,0>
# computeLineEquation # computes line equation given 2 points: A and B
# computeVolume # computes volume given 3 points using double integral, line and plane equations


print('##################################')
print('Welcome to the Earthworks Program!')
print('##################################')

while True:
    print('Select one of the following options:')
    print('[1] Load data from GPS file (*.gpx).')
    print('[2] Generate UTM coordinates file from latitude,longitude.')
    print('[3] Compute cut/fill volumes from existing UTM coordinates file.')
    print('[4] View point cloud of existing UTM coordinates file.')
    print('[5] Exit program.')
    optionLevel1 = getNumericalInput()
    if optionLevel1 in (1,2,3,4,5):
        if (optionLevel1==1): # Option 1: Parse .gpx file
            print('------------------')
            print("Reading .gpx file.")
            # Check existing .gpx files on current working folder and list them for selection
            parseGpxFile('gpsData.gpx') # parse .gpx file
            print('XML parsing complete.')
            print('---------------------')
        elif (optionLevel1==2): # Option 2: Generate UTM
            print('---------------------------')
            print('Generating UTM coordinates.')
            # Check existing .csv files on current working folder and list them for selection
            generateUTM('gpsData.csv') # generates csv file with UTM coordinates
            print('Process completed.')
            print('------------------')
        elif (optionLevel1==3): # Option 3: Compute volumes
            # [1] Compute volumes for a given terrain elevation.
            # [2] Find elevation for optimal volumes (cut equals fill)
            while True:
                print('------------------------------------')
                print('Select one of the following options:')
                print('[1] Define terrain dimensions.')
                print('[2] Compute volumes for a given terrain elevation.')
                print('[3] Find elevation for optimal volumes (cut equals fill).')
                print('[4] Back to previous menu.')
                optionLevel2 = getNumericalInput()
                if optionLevel2 in (1,2,3,4):
                    dx = None # define delta x: terrain width
                    dy = None # define delta y: terrain length
                    if optionLevel2==1:
                        # print('-------------------------------------')
                        # print('Define construction area width (dx): ')
                        # dx = getNumericalInput()
                        # print('Define construction area length (dy): ')
                        # dy = getNumericalInput()
                        # print('Define area step size in meters. Lowest values take longer to compute: ')
                        # areaStep = getNumericalInput()
                        print('Feature being implemented. Please be patient. :)')
                        break
                    if optionLevel2==2:
                        # if ((dx is None) or (dy is None)): # use full terrain area
                        #     print('Construction area was not defined. Using the entire terrain.')
                        df = loadSurveyData()
                        df = createRelativeDataframe(df)
                        computeVolumesFromElevation(df)
                        break # go back to previous menu
                    elif optionLevel2==3: # Find optimal values
                        df = loadSurveyData()
                        df = createRelativeDataframe(df)
                        print('------------------------------------')
                        step = getNumericalInput('Please provide step size in meters: ')
                        dfVol = computeOptimalVolumes(df,step)
                        break
                    elif optionLevel2==4: # Back to level 1
                        break
                else:
                    print('Invalid option. Try again.')
        elif (optionLevel1==4): # Option 4: View data
            dfFull = loadSurveyData()
            dfFull = createRelativeDataframe(dfFull)
            while True:
                print('------------------------------------')
                print('Select one of the following options:')
                print('[1] Print full dataset.')
                print('[2] Print Cut and Fill datasets given a reference relative elevation.')
                print('[3] Back to previous menu.')
                optionLevel2 = getNumericalInput()
                if optionLevel2 in (1,2,3):
                    if optionLevel2==1:
                        # Full dataset print
                        print('---------------------')
                        print('Plotting terrain data')
                        url = plotTerrain(dfFull)
                        print('Data plotted successfully at:')
                        print(url)
                        print('-----------------------------')
                        break
                    elif optionLevel2==2:
                        # Print full dataset plus cut and fill
                        z_max = dfFull.z_rel.max()
                        while True:
                            reference = getNumericalInput('Please provide reference elevation <= {z:.2f}: '.format(z=z_max))
                            if (reference <= z_max):
                                dfCut = dfFull[(dfFull['z_rel'] >= reference)]
                                pd.options.mode.chained_assignment = None  # default='warn'
                                dfCut['z_rel'] = dfCut.z_rel.apply(lambda x: x-reference) # update z_rel = z_rel - reference
                                pd.options.mode.chained_assignment = 'warn'  # default='warn'
                                dfFill = dfFull[(dfFull['z_rel'] < reference)]
                                urlFull = plotTerrain(dfFull,'plotFull.html')
                                urlCut = plotTerrain(dfCut,'plotCut.html')
                                urlFill = plotTerrain(dfFill,'plotFill.html')
                                print('Data plotted successfully at application folder.')
                                print('------------------------------------------------')
                                break
                        break
                    elif optionLevel2==3:
                        break # Back
                else:
                    print('Invalid option. Try again.')
        elif (optionLevel1==5): # Exit program
            break
        #break
    else:
        print('Invalid option. Try again.')
    time.sleep(1) # do nothing for a couple of seconds
