#!/usr/bin/env python

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
import PointValidation as validation
from PointValidation import State
import MissionTimeUtils as timeutils

#argument parsing sys libraries
from optparse import OptionParser
import sys
import os.path

parser = OptionParser("")
parser.add_option("-f", "--file", dest="files",
    action="append", help="read GPS data from log files and plot on the graph");

parser.add_option("-i", "--FaultInjection", dest="faultInjection",
    action="append", help="Marks GPS intervals during which a fault was injected");

parser.add_option("-m", "--mission", dest="mission",
    help="read data from mission file and plot mission on the graph");

parser.add_option("-c", "--caption", dest="captions",
    action="append",help="Adds caption for each file to plot");

parser.add_option("-d", "--distance", action="store_true",
    help="shows distance between test landzone and mission landzone",
    dest="distance");

parser.add_option("-t", "--time", action="store_true",dest="time",
    help="shows the estimated time for the completion of the selected mission");

parser.add_option("-e", "--eval", action="store_true",dest="eval",
    help="show evaluation of a specific mission");


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


if options.mission:

    #check if file exists
    if not os.path.isfile(str(options.mission)):
        raise Exception("File " + str(options.mission) + "does not exist");

    mission = utils.GetMissionWaypoints(str(options.mission))
    
    X = []; Y = []; Z = []; wp_type = [];
    for waypoint in mission:
        X.append(waypoint.x);
        X.append(waypoint.x1);
        Y.append(waypoint.y);
        Y.append(waypoint.y1);
        Z.append(waypoint.z);
        Z.append(waypoint.z1);
        wp_type.append(waypoint.type);


    ax.plot(X, Y, Z, label="Mission", color="red");
    
    #Add "start and end" captions to graph
    ax.text(X[0], Y[0], Z[0], "Start", color='green')
    ax.text(X[-1], Y[-1], Z[-1], "End", color='red')

    #store landing data to calculate distance
    missionlanding = (Y[-1],X[-1]);


if options.eval and options.mission and options.files:
    STATUS = State.NORMAL
    error_x = []; error_y = []; error_z = []
    #for each point in the logs
    for i in range(len(x)):
        TEMP_STATUS = validation.get_point_status(np.array([x[i],y[i],z[i]]), X, Y, Z, wp_type)

        if TEMP_STATUS != State.NORMAL:
            STATUS = TEMP_STATUS

            error_x += [x[i]]
            error_y += [y[i]]
            error_z += [z[i]]

            if TEMP_STATUS == State.MAJOR_FAULT:
                break;

    if STATUS == State.NORMAL:
        ax.text2D(0.05, 0.95, "OK", color='green', transform=ax.transAxes)
    elif STATUS == State.MINOR_FAULT:
        ax.text2D(0.05, 0.95, "Minor Fault", color='orange', transform=ax.transAxes)
    else:
        ax.text2D(0.05, 0.95, "Major Fault", color='red', transform=ax.transAxes)

    if(len(error_x) > 0):
        ax.plot(error_x,error_y,error_z, 'o', color='red', label='Point of error')


if options.faultInjection:
    first = True;

    for i in range(len(options.faultInjection)):
        #check if file exists
        if not os.path.isfile(str(options.files[i])):
            raise Exception("File " + options.files[i] + "does not exist");

        if not os.path.isfile(options.faultInjection[i]):
            raise Exception("File " + options.faultInjection[i] + "does not exist");

        data = utils.getFaultyPoints(options.faultInjection[i],options.files[i]);
        for element in data:
            if not first:
                ax.plot(element.x, element.y, element.z , color='#4b0082', linewidth=4, ls='-' ,dash_capstyle='round');
            else:
                ax.plot(element.x, element.y, element.z , label= "Fault Occurence" ,color='#4b0082', linewidth=4, ls='-' ,dash_capstyle='round');
                fist = False;

if options.distance:
    if not options.mission or not options.files:
        raise Exception("Cannot calculate distance between landing zones, since both Mission file and at least one mission is required!");
    
    for i in range(len(options.captions)):
        print "Distance between \"%s-LZ\" to \"%s-LZ\" is: %.3fm" % (options.captions[i],options.missionlabel,round(distance(runLandZones[i],missionlanding).meters,3))


if options.time and options.mission:
    time = timeutils.getEstimatedMissionTime(options.mission)
    time = "Time: %.2f" % round(time,2);
    ax.text2D(0.30, 0.95,time, color='blue', transform=ax.transAxes)


ax.set_xlabel('Latitude')
ax.set_ylabel('Longitude')
ax.set_zlabel('Altitude')

ax.legend()
plt.show()