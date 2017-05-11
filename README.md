## Earthworks Python

Welcome to my Earthworks Python application.

### Why?
This application comes out of a necessity of computing cut and fill volumes required for leveling terrains on electrical substations construction sites.

### How does it work?
Given a .gpx file obtained from a GPS survey on the terrain, the construciton area (delimited by 4 GPS points) and a reference elevation this application will compute the required cut and fill volumes for leveling the terrain and plot corresponding graphs.

As GPS coordinates are based on a Geographic Coordinate System, these coordinates are converted into a Cartesian Coordinate System in order to make use of linear algebra for computing the volumes.
