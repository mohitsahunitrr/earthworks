## Python Earthworks

Welcome to the Python Earthworks program.

### Why?
This application comes out of the necessity of computing cut and fill volumes required for leveling terrains on electrical substations construction sites.

### How does it work?
Given a .gpx file obtained from a GPS survey on the terrain, the construciton area (delimited by 4 GPS points) and a reference elevation this application will compute the required cut and fill volumes for leveling the terrain to that reference and plot corresponding graphs.

As GPS coordinates are based on a Geographic Coordinate System, these coordinates are converted to a Cartesian Coordinate System in order to make use of linear algebra for computing the volumes. The WGS84 (World Geodetic System) standard was used in the conversion process.
