#distance.calculate(); #https://geopy.readthedocs.io/en/stable/#module-geopy.distance

#3dPlot libraries
import numpy as np
import matplotlib as mpl
import matplotlib.pyplot as plt
from mpl_toolkits.mplot3d import Axes3D

#Library used for distance calculation
from geopy.distance import distance

#My library that parse the logs
import LogUtils as utils

#argument parsing sys libraries
from optparse import OptionParser
import sys
import os.path


parser = OptionParser("")
parser.add_option("-f", "--file", dest="files",
    action="append", help="read GPS data from log files and plot on the graph");

parser.add_option("-m", "--mission", dest="mission",
    help="read data from mission file and plot mission on the graph");

parser.add_option("-l", "--mission_label", dest="missionlabel",
    help="read data from mission files and plot on the graph");

parser.add_option("-c", "--caption", dest="captions",
    action="append",help="Adds caption for each file to plot");

parser.add_option("-d", "--distance", action="store_true",
    default="store_false",dest="distance");

(options, args) = parser.parse_args();

if len(args) == 1:
    parser.error("incorrect number of arguments")

#init graph vars
mpl.rcParams['legend.fontsize'] = 10
fig = plt.figure()
ax = fig.gca(projection='3d')


if not options.mission and not options.files:
    raise Exception("need data to proccess, no data, no fun! try -h");

firstH  = sys.maxsize;
lastH   = sys.maxsize;
runLandZones = [];

if options.files:
    for i in range(len(options.files)):
        #check if file exists
        if not os.path.isfile(str(options.files[i])):
            raise Exception("File " + str(options.files[i]) + "does not exist");

        x,y,z = utils.GetGPSData(str(options.files[i]));
        ax.plot(x, y, z, label=str(options.captions[i]));
        
        #The distance calculator utilizes "lat, lng" format, hence why it's y,x and not x,y.
        #values are stored here so we can calculate the distances later
        runLandZones.append((y[-1],x[-1]));

        #get lowest values for taking off and landing (this is simple to compesate for mission planner's error)
        if z[0] < firstH:
            firstH = z[0];
        
        if z[-1] < lastH:
            lastH = z[-1];


if options.mission:

    if not options.missionlabel:
        raise Exception("mission must have a label");

    #check if file exists
    if not os.path.isfile(str(options.mission)):
        raise Exception("File " + str(options.mission) + "does not exist");

    if not options.files:
        mission = utils.GetMissionWaypoints(str(options.mission));
    else:
        print "its this one"
        mission = utils.GetMissionWaypoints(str(options.mission), firstH, lastH);
    
    x = []; y = []; z = [];
    for waypoint in mission:
        x.append(waypoint.x);
        x.append(waypoint.x1);
        y.append(waypoint.y);
        y.append(waypoint.y1);
        z.append(waypoint.z);
        z.append(waypoint.z1);

    ax.plot(x, y, z, label=options.missionlabel, colour="red");

    #store landing data to calculate distance
    missionlanding = (y[-1],x[-1]);

if options.distance:
    if not options.mission or not options.files:
        raise Exception("Cannot calculate distance between landing zones, since both Mission file and at least one mission is required!");
    
    for i in range(len(options.captions)):
        print runLandZones[i],"-",missionlanding;    
        print "Distance between ",options.captions[i],"-LZ to ",options.missionlabel[0],"-LZ: ",distance(runLandZones[i],missionlanding).meters,"m"

ax.legend()
plt.show()