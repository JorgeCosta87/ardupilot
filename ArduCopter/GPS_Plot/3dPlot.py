
#import geopy.distance as distance
#Function to calculate the distance between 2 GPS coordinates
#distance.calculate(); #https://geopy.readthedocs.io/en/stable/#module-geopy.distance

#Plot script
import sys;
import numpy as np
import matplotlib as mpl
import matplotlib.pyplot as plt
from mpl_toolkits.mplot3d import Axes3D

import LogUtils as utils

mpl.rcParams['legend.fontsize'] = 10
fig = plt.figure()

ax = fig.gca(projection='3d')

#TODO: make this a foreach that can take as many files as necessary
x,y,z = utils.GetGPSData(sys.argv[1]);
ax.plot(x, y, z, label = "default run");

#Keep real terrain height to use for takeoff and landing on the mission waypoints, since mission planner is innacurate. 
#TODO: Explore ways to make it so it gathers the altitude on by itself.
firstH = z[0];
lastH = z[-1];

if(len(sys.argv) > 2):
    x, y, z = utils.GetGPSData(sys.argv[2]);
    ax.plot(x, y, z, label = "fault injection run")

if(len(sys.argv) == 4):
    mission = utils.GetMissionWaypoints(sys.argv[3], firstH, lastH);
    x = []; y = []; z = [];
    for waypoint in mission:
        x.append(waypoint.x);
        x.append(waypoint.x1);
        y.append(waypoint.y);
        y.append(waypoint.y1);
        z.append(waypoint.z);
        z.append(waypoint.z1);

    ax.plot(x, y, z, label = "Mission Plan", color = "red");
    
ax.legend() 
plt.show()