# Main user interface.

from functionsEarthworks import *
from functionsProgramFlow import *
from functionsTestScenarios import *
from classes import *

# Custom functions:
# parseGpxFile # parses input .gpx file
# generateUTM # generates csv file with UTM coordinates
# printProgressBar # function definitions imported from suplementary .py files
# distanceFromOrigin # compute distance from origin <0,0,0>
# computeLineEquation # computes line equation given 2 points: A and B
# computeVolume # computes volume given 3 points using double integral, line and plane equations

# Think about some clever way of implementing language selection using arrays.

print('##################################')
print('Welcome to the Earthworks Program!')
print('##################################')

while True:
    print('Type one of the following options:')
    # print('[1] Parse data from GPS file (*.gpx).')
    # print('[2] Generate UTM coordinates file from latitude,longitude.')
    # print('[3] Load construction area limits (4 GPS coordinates) from \'limits.csv\'')
    print('[1] Compute cut/fill volumes.')
    print('[2] View point cloud scatter plot.')
    print('[3] Load terrain limits filter from limits.csv')
    print('[4] Generate test scenario.')
    print('[5] Exit program.')
    optionLevel1 = getNumericalInput('Option: ')
    if optionLevel1 in (1,2,3,4,5):

        if (optionLevel1==1): # Option 1: Compute volumes

            while True:
                print('---------------------------------------')
                print('[1] Use data from gpsData.gpx')
                print('[2] Use data from in gpsDataUTM.csv')
                print('[3] Use data from generatedPointCloud.csv')

                optionLevel2 = getNumericalInput('Option: ')
                if optionLevel2 in (1,2,3):
                    if optionLevel2==1:
                        # generate UTM file from .gpx and load data
                        print("Reading .gpx file.")
                        # Check existing .gpx files on current working folder and list them for selection
                        parseGpxFile('gpsData.gpx') # parse .gpx file
                        print('XML parsing complete.')
                        print('Generating UTM coordinates.')
                        # Check existing .csv files on current working folder and list them for selection
                        generateUTM('gpsData.csv','gpsDataUTM.csv') # generates csv file with UTM coordinates
                        dfSurvey = loadSurveyData() # load dataframe from csv file
                        dfSurvey = createRelativeDataframe(dfSurvey) # add relative coordinates (x_rel,y_rel,z_rel)
                        print('Process completed.')
                        #print(dfSurvey.where(dfSurvey['z_rel'] < 1))
                        #print(dfSurvey.head())
                        break
                    elif optionLevel2==2: # Use real world data from converted UTM file
                        dfSurvey = loadSurveyData() # load dataframe from csv file
                        dfSurvey = createRelativeDataframe(dfSurvey) # add relative coordinates (x_rel,y_rel,z_rel)
                        break
                    elif optionLevel2==3: # Use test set
                        dfSurvey = pd.read_csv('generatedPointCloud.csv')
                        print('Data from test set successfully loaded.')
                        print('{n} points available in test set.'.format(n=dfSurvey.x_rel.count()))
                        break

            # Save maximum values
            x_max = dfSurvey.x_rel.max()
            y_max = dfSurvey.y_rel.max()
            z_max = dfSurvey.z_rel.max()

            while True:
                print('------------------------------------')
                print('Type one of the following options:')
                print('[1] Compute volumes for a given terrain elevation.')
                print('[2] Find elevation for optimal volumes (cut equals fill).')
                print('[3] Back to previous menu.')
                optionLevel2 = getNumericalInput('Option: ')
                if optionLevel2 in (1,2,3):
                    if optionLevel2==1:
                        desiredElevation = getNumericalInput('Please input desired terrain level: ')
                        startTime = datetime.now() # start the clock on this script
                        try:
                            dfLimits
                        except NameError: # dfLimits was not defined
                            print('Construction limits were not defined. Using the entire terrain.')
                            print('Terrain width = {w:.2f}'.format(w=x_max))
                            print('Terrain length = {l:.2f}'.format(l=y_max))
                            # print('Aproximate terrain rectangular area = {a:.2f}'.format(a=x_max*y_max)) calculate area; not always rectangular
                            cutVol, cutErr, fillVol, fillErr = computePointCloudVolume(dfSurvey, elevation = desiredElevation, enablePrompts=True)
                        else: # compute on filtered data
                            # add relative coordinates to the limits dataframe; depens on minimum/maximum values of x,y
                            dfLimits['x_rel'] = dfLimits.x - dfSurvey.x.min()
                            dfLimits['y_rel'] = dfLimits.y - dfSurvey.y.min()

                            # plot terrain limits in comparison to full terrain data. Use z = (max-min)/2 - aka midpoint
                            dfLimits['z_rel'] = desiredElevation # sample z_rel for plotting purposes
                            dfLimits = createRelativeDataframe(dfLimits) # add distance from origin
                            plotFull = scatterPlotData(dfSurvey,'Terrain','rgba(217, 217, 217, 0.14)') #data frame to plot, name of the series and color
                            plotLimits = scatterPlotData(dfLimits,'Construction boundaries','rgba(117, 117, 117, 0.14)') #data frame to plot, name of the series and color

                            # Filter survey data and eliminate all points outside of boundaries
                            print('Filtering point cloud.')
                            dfFiltered = filterTerrainLimits(dfSurvey,dfLimits)
                            plotFiltered = scatterPlotData(dfFiltered,'Filtered data','rgba(17, 17, 17, 0.14)')
                            plots = [plotFull,plotLimits,plotFiltered]
                            print(dfFiltered.head())
                            cutVol, cutErr, fillVol, fillErr = computePointCloudVolume(dfFiltered, elevation = desiredElevation, enablePrompts=True)
                            url = plotTerrain(plots,'plotBoundaries.html') # plot data

                        print('The total cut volume is: {v:,.2f} cubic meters.'.format(v=cutVol))
                        print('Accumutaled integration error: {e}.'.format(e=cutErr))
                        print('The total fill volume is: {v:,.2f} cubic meters.'.format(v=fillVol))
                        print('Accumutaled integration error: {e}.'.format(e=fillErr))
                        print('Computation process completed.')
                        print('Script runtime: {t}'.format(t=datetime.now() - startTime))
                        print('---------------------------')
                        break # go back to previous menu
                    elif optionLevel2==2: # Find optimal values
                        print('------------------------------------')
                        stepElevation = getNumericalInput('Please provide elevation step size in meters: ')
                        try:
                            dfLimits
                        except NameError: # dfLimits was not defined
                            print('Construction limits were not defined. Using the entire terrain.')
                            print('Maximum x coordinate = {w:.2f}'.format(w=x_max))
                            print('Maximum y coordinate = {l:.2f}'.format(l=y_max))
                            swellFactor = getNumericalInput('Please provide a swell factor (terrain dependent): ')
#                            terrainDropFactor = getNumericalInput('Please provide a terrain drop factor in % value (e.g.: 1.5. 0.0 means no drop.): ')
#                            terrainDropFactor = terrainDropFactor/100.0
                            dfVol = computeOptimalVolumes(dfSurvey,stepElevation, swellFactor)
                        else: # compute on filtered data
                            # add relative coordinates to the limits dataframe; depens on minimum/maximum values of x,y
                            dfLimits['x_rel'] = dfLimits.x - dfSurvey.x.min()
                            dfLimits['y_rel'] = dfLimits.y - dfSurvey.y.min()

                            # plot terrain limits in comparison to full terrain data. Use z = (max-min)/2 - aka midpoint
                            dfLimits['z_rel'] = 10.0 # sample z_rel for plotting purposes
                            dfLimits = createRelativeDataframe(dfLimits) # add distance from origin
                            # Filter survey data and eliminate all points outside of boundaries
                            print('Filtering point cloud.')
                            dfFiltered = filterTerrainLimits(dfSurvey,dfLimits)
                            swellFactor = getNumericalInput('Please provide a swell factor (terrain dependent): ')
#                            terrainDropFactor = getNumericalInput('Please provide a terrain drop factor in % value (e.g.: 1.5. 0.0 means no drop.): ')
#                            terrainDropFactor = terrainDropFactor/100.0
                            dfVol = computeOptimalVolumes(dfFiltered,stepElevation, swellFactor)

                        break
                    elif optionLevel2==3: # Back to level 1
                        break
                else:
                    print('Invalid option. Try again.')
        elif (optionLevel1==2): # Option 2: View data
            while True:
                print('----------------------')
                print('[1] Use survey data.')
                print('[2] Use test data set.')
                print('[3] Back to previous menu.')
                optionLevel2 = getNumericalInput('Option: ')
                if optionLevel2 in (1,2,3):
                    if optionLevel2==1: # Load survey data and plot
                        dfSurvey = loadSurveyData() # load dataframe from csv file
                        dfSurvey = createRelativeDataframe(dfSurvey) # add relative coordinates (x_rel,y_rel,z_rel)
                        x_max = dfSurvey.x_rel.max()
                        y_max = dfSurvey.y_rel.max()
                        z_max = dfSurvey.z_rel.max()
                        reference = getNumericalInput('Please provide reference elevation <= {z:.2f}: '.format(z=z_max))
                        dfCut = dfSurvey[(dfSurvey['z_rel'] >= reference)]
                        dfFill = dfSurvey[(dfSurvey['z_rel'] < reference)]
                        plot1 = scatterPlotData(dfCut,'Cut','rgba(217, 217, 217, 0.14)')
                        plot2 = scatterPlotData(dfFill,'Fill','rgba(117, 117, 117, 0.14)')
                        plotData = [plot1,plot2]
                        urlFull = plotTerrain(plotData,'plotSurveyData.html')
                        print('Data plotted successfully at application folder.')
                        print('------------------------------------------------')
                        break
                    if optionLevel2==2: # Load and plot test data
                        dfTest = pd.read_csv('generatedPointCloud.csv')
                        plot1 = scatterPlotData(dfTest,'Cut','rgba(217, 217, 217, 0.14)')
                        plotData = [plot1]
                        urlFull = plotTerrain(plotData,'plotTestData.html')
                        print('Data plotted successfully at application folder.')
                        print('------------------------------------------------')
                        break
                else:
                    print('Invalid option. Try again.')
        elif optionLevel1==3:
            print('--------------------------------')
            print('Loading terrain limits from file.')
            print('Expected entry example: -24.9361964688,-51.3905997667')
            dfLimits = pd.read_csv('limits.csv')
            dfLimits = limitsUTM(dfLimits) # inserts UTM coordinates
            # ERROR CHECK TO IMPLEMENT: verify if boundaries are withing surveyed terrain and warn if outside (also set dfLimits to None if that's the case)
            print('Construction limits established.')
            print('All survey points outside of construction limits will be disregarded.')
            break
        elif (optionLevel1==4): # generate test set
            pointsPerPlane = getNumericalInput('Please provide the amount of points per plane: ')
            pointsPerPlane = int(pointsPerPlane)
            dfTest, pcDen = generateTestScenario01(amountOfPoints=pointsPerPlane)
            plot1 = scatterPlotData(dfTest,'Test set','rgba(217, 217, 217, 0.14)')
            plotData = [plot1]
            urlFull = plotTerrain(plotData,'plotTestSet.html')
            break

#        elif (optionLevel1==5): # Run accuracy tests
#            # Step 1: Determine point cloud densities that will undergo tests
#            densities = [10,20,50,100,150,200,250,300] # test set if given by 3 planes, so these values will be multiplied by 3 each for the total number of points
#            #densities = [10,20]
#            # Step 2: For each density, generate test set and store computed volume.
#            iterations = len(densities) # number of iterations
#            iteration = 0 # progress bar counter
#
#            dfResults = pd.DataFrame([]) # build dataframe for storing results
#
#            for points in densities:
#                points = int(points)
#                dfTest, pcDen = generateTestScenario01(amountOfPoints=points)
#                cutVol, cutErr, fillVol, fillErr = computePointCloudVolume(dfTest, elevation = 0.0, enablePrompts=False)
#                error = abs(170.0-cutVol)/170.0
#                accuracy = 1-error
#                # store result and density
#                testResult = pd.Series(dict(
#                                        density=pcDen,
#                                        error=error,
#                                        accuracy=accuracy))
#                dfResults = dfResults.append(testResult, ignore_index=True) # append newly converted data to dataframe
#                iteration += 1 # update progress counter
#                printProgressBar(iteration, iterations, prefix = 'Progress:', suffix = 'Complete', length = 50) # update progress bar
#            # Step 3: Plot graph: Density Vs. Accuracy (or Error)
#            #Plotting with Bokeh
#            x = dfResults['density'].values
#            y1 = dfResults['accuracy'].values
#            y2 = dfResults['error'].values
#
#            TOOLS = [BoxSelectTool(), HoverTool()]
#            p = figure(title="Program Analysis Report on Test Set", tools = TOOLS)
#            p.line(x, y1, legend="Accurracy",line_color="SteelBlue", line_dash="dotdash", line_width=4)
#            p.line(x, y2, legend="Error",line_color="Coral", line_dash="dotdash", line_width=4)
#            p.legend.location = "bottom_left"
#            p.xaxis.axis_label = 'Cloud density (points/㎥)'
#            p.yaxis.axis_label = 'Absolute scale (0-1)'
#            #p.yaxis[0].formatter = PrintfTickFormatter(format="%d")
#            output_file("plotProgramAnalysisReport.html", title="Program Analysis Report on Test Set")
#            show(p)
#            break
        elif (optionLevel1==5): # Exit program
            break
    else:
        print('Invalid option. Try again.')
    time.sleep(1) # do nothing for a couple of seconds
