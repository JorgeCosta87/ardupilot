import os.path

#Function to get Lattitude, Longitude and Altitude from file and gives it back in X, Y, Z list
def GetGPSData(filename):
    if not os.path.isfile(filename):
        raise Exception("File" + filename + "does not exist");

    file = open(filename, "rt");

    x = [];
    y = [];
    z = [];
    
    for line in file:
        split = line.split(",");
        x.append(float(split[0]));
        y.append(float(split[1]));
        z.append(float(split[2]));

    file.close();

    return x, y, z;
    

from collections import namedtuple

def GetMissionWaypoints(filename, takeoffH = "nan", landingH = "nan"):
    if not os.path.isfile(filename):
        raise Exception('File' + filename + 'does not exist');
    
    file = open(filename, "rt");

    line = file.readline();
    if not line.startswith('QGC WPL 110'):
        raise Exception('File ' + filename + ' is not supported WP version');

    #Define Constants
    waypoint = 16;
    landing = 21;
    takeoff = 22;

    #Reads first line and set's up variables
    line = file.readline();
    split = line.split("\t");

    default = namedtuple("coord", "lng lat alt");
    default.lng = float(split[9]);
    default.lat = float(split[8]);

    #if the base takeoff value is given then replace it, else keep the value given by default.
    if type(takeoffH) == type(str):
        default.alt = float(split[10]);
    else:
        default.alt = takeoffH;
    

    last = namedtuple("coord", "x y z x1 y1 z1");
    last.x1 = default.lng;
    last.y1 = default.lat;
    last.z1 = default.alt;

    #Coordinates list
    coords = [];
    for line in file:
        split = line.split("\t"); 

        #The drone action
        action = int(split[3]);

        if(action == waypoint):
            data = namedtuple("coord", "x y z x1 y1 z1");

            #Get Current position
            data.x = last.x1;
            data.y = last.y1;
            data.z = last.z1;
            
            #Get next way point 
            data.x1 = float(split[9]);
            data.y1 = float(split[8]);
            data.z1 = float(default.alt + float(split[10]));# TODO: this can screw up some stuff when there are more than 1 waypoint, needs testing
            
            #points to last waypoint so that it's possible to calculate the next one
            last = data;
            coords.append(data);


        if(action == takeoff or action == landing): #TODO: add RTL to this condition
            data = namedtuple("coord", "x y z x1 y1 z1");
            
            #Get Current position
            data.x = last.x1;
            data.y = last.y1;
            data.z = last.z1;

            #Get next way point 
            data.x1 = last.x1;
            data.y1 = last.y1;
            data.z1 = float(default.alt + float(split[10])); #TODO: comment later

            if(action == landing and type(landingH) != type(str)):#TODO: needs to be documented.
                data.z1 = landingH;

            #points to last waypoint so that it's possible to calculate the next one
            last = data;
            coords.append(data);

    file.close();
    return coords;

"""
#simple way to test GetMissionWaypoints
import sys

a = GetMissionWaypoints(sys.argv[1]);

i = 1;
#print "coord 0", d.lng, d.lat, d.alt;
for point in a:
    print "coord ", i , point.x, point.y, point.z, point.x1, point.y1, point.z1;
    i = i+1;
"""

#This is the slowest thing to ever exist, it's just here for referece, do not use it, as it trashes performance
"""
def point_in_cylinder(pt1, pt2, points, r, N=100):
    dist = np.linalg.norm(pt1 - pt2)
    ori = (pt2 - pt1) / dist 
    #line = np.array([pt1 + ori*t for t in np.linspace(0, dist, N)])
    line = (pt1.reshape(3, 1) + elc_ori.reshape(3, 1) @ np.linspace(0, dist, N).reshape(1, N)).T
    dists = np.min(cdist(line, points), 0)

    return np.where(dists <= r)[0]
"""

#Better method O(1)
#Given two 3d points and another list of 3d points, I want to check which one is inside the cylinder defined as the 3d line between the two points with a radius of r
#q is the point to test
def points_in_cylinder(pt1, pt2, r, q):
    vec = pt2 - pt1
    const = r * np.linalg.norm(vec)
    return np.where(np.dot(q - pt1, vec) >= 0 and np.dot(q - pt2, vec) <= 0 
           and np.linalg.norm(np.cross(q - pt1, vec)) <= const)

"""
import matplotlib.pyplot as plt
import numpy as np
from mpl_toolkits.mplot3d import Axes3D
import sys

def test():
    fig = plt.figure();
    ax = fig.add_subplot(111, projection='3d');

    dataset = GetMissionWaypoints(sys.argv[1]);
    x = [];
    y = [];
    z = [];
    for waypoint in dataset:
    # Cylinder
    #z.append()
    Xc, Zc=np.meshgrid(x, z)
    Yc = np.sqrt(1-Xc**2)

    # Draw parameters
    rstride = 20
    cstride = 10
    ax.plot_surface(Xc, Yc, Zc, alpha=0.2, rstride=rstride, cstride=cstride)
    ax.plot_surface(Xc, -Yc, Zc, alpha=0.2, rstride=rstride, cstride=cstride)

    ax.set_xlabel("X")
    ax.set_ylabel("Y")
    ax.set_zlabel("Z")
    plt.show()
"""
#test();