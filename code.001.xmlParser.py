# This piece of code converts the .gpx file (XML format) to a CSV file with the following information:
# latitude, longitude, elevation

from xml.dom.minidom import parse
import xml.dom.minidom

DOMTree = xml.dom.minidom.parse("gpsData.gpx")
collection = DOMTree.documentElement

# Get all track points in the collection
trackPoints = collection.getElementsByTagName("trkpt")

# Read in all the data of interest
file = open("gpsData.csv",'w') # create output file
file.write("latitude,longitude,elevation")

for point in trackPoints:
    lati = point.getAttribute("lat")
    long = point.getAttribute("lon")
    altx = point.getElementsByTagName('ele')[0]
    alti = altx.childNodes[0].data

    # all data types are str; checked: print(type(lati),type(long),type(alti))
    file.write(lati+","+long+","+alti+"\n") # output to file and process next point
file.close() #close output file
