## Python Earthworks

Welcome to the Python Earthworks program.

### What does it do?
Computes cut and fill volumes required for leveling terrains on electrical substations construction sites.

### How does it work?
Given a .gpx file obtained from a GPS survey, the construciton area (a rectangle delimited by 4 GPS points) and a reference elevation this application will compute the required cut and fill volumes for leveling the terrain to that reference and plot corresponding graphs.

### How do I use it?
- Step 1: Download and install Python 3 and corresponding libraries
- Step 2: Setup a Plotly account and corresponding API_KEY (info below)
- Step 3: Survey data on the field using a GPS.
- Step 4: Download this program and place the corresponding .gpx file generated from your survey on the root folder, replacing the existing gpsData.gpx
- Step 5: open a new Terminal window on the program folder
- Step 6: run "python3 main.py"

Done!

### Bug reports are welcome!

### Important: Setting up Plotly api_key
As a safety measure, API keys are not hardcoded. Please setup your own key when using the program.
In Terminal:
export MY_API_KEY='bdfr43lkjfr35'
