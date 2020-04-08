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
        mission = utils.GetMissionWaypoints(str(options.mission), firstH, lastH);
    
    X = []; Y = []; Z = [];
    for waypoint in mission:
        X.append(waypoint.x);
        X.append(waypoint.x1);
        Y.append(waypoint.y);
        Y.append(waypoint.y1);
        Z.append(waypoint.z);
        Z.append(waypoint.z1);


    ax.plot(X, Y, Z, label=options.missionlabel, color="red");
    
    #Add "start and end" captions to graph
    ax.text(X[0], Y[0], Z[0], "Start", color='green')
    ax.text(X[-1], Y[-1], Z[-1], "End", color='red')

    #store landing data to calculate distance
    missionlanding = (Y[-1],X[-1]);
    
    #Status = 0 is ok, 1 is minor fault, 2 is major fault
    STATUS = 0
    for i in range(len(x)):
        for J in range(0,len(X),2):
            #Outter if checks for inner cylinder and Inner if checks for outmost cylider
            #if the point is not inside the inner cilinder, check if it has surpassed the outter cylinder threshold
            if  not validation.points_in_cylinder(np.array([X[J],Y[J],Z[J]]), np.array([X[J+1],Y[J+1],Z[J+1]]), 0.000001 * 3, np.array([x[i],y[i],z[i]])):
                if not validation.points_in_cylinder(np.array([X[J],Y[J],Z[J]]), np.array([X[J+1],Y[J+1],Z[J+1]]), 0.000001 * 3 * 2, np.array([x[i],y[i],z[i]])):
                    STATUS = 2
                else:
                    STATUS = 1
            else:
                STATUS = 0;
                break;
        
        #if not found, check the spheres
        if STATUS != 0:
            break;

        STATUS_SPHERE = 0;
        for J in range(1,len(X)-1):
            if validation.inSphere(np.array([x[i],y[i],z[i]]), np.array([X[J],Y[J],Z[J]]), 0.000001 * 3):
                if validation.inSphere(np.array([x[i],y[i],z[i]]), np.array([X[J],Y[J],Z[J]]), 0.000001 * 3 * 2):
                    STATUS_SPHERE = 2
                else:
                    STATUS_SPHERE = 1
            else:
                STATUS = 0;
                break;

        #Basically means that the point is between a inner sphere and outter sphere.
        if STATUS_SPHERE < STATUS:
            STATUS = STATUS_SPHERE;

    if STATUS == 0:
        ax.text2D(0.05, 0.95, "OK", color='green', transform=ax.transAxes)
    elif STATUS == 1:
        ax.text2D(0.05, 0.95, "Minor Fault", color='orange', transform=ax.transAxes)
    else:
        ax.text2D(0.05, 0.95, "Major Fault", color='red', transform=ax.transAxes)

    #TODO: Remove this later, it's just a demo
    time = timeutils.getEstimatedMissionTime(options.mission)
    time = "Time: %.2f" % round(time,2);
    ax.text2D(0.30, 0.95,time, color='blue', transform=ax.transAxes)


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
        print runLandZones[i],"-",missionlanding;    
        print "Distance between \"",options.captions[i],"\"-LZ to \"",options.missionlabel,"\"-LZ: ",distance(runLandZones[i],missionlanding).meters,"m"


ax.set_xlabel('Latitude')
ax.set_ylabel('Longitude')
ax.set_zlabel('Altitude')

ax.legend()
plt.show()