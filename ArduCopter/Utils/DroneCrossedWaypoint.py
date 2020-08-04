#!/usr/bin/env python

import PointValidation as evaluation
import LogUtils as utils
import os
from sys import argv

if len(argv) < 3:
    print "Example: ", argv[0], " <missionFile> < run gps file >"
    exit(1)

mission_path = argv[1]
run = argv[2]

#check if files are valid
if not os.path.isfile(mission_path):
    raise Exception('File\'' + mission_path + '\'does not exist')

if not os.path.isfile(run):
    raise Exception('File\'' + run + '\'does not exist')

# Load mission and data 
x,y,z = utils.GetGPSData(run)
mission = utils.GetMissionWaypoints(mission_path)
X = []; Y = []; Z = []
for waypoint in mission:
    X.append(waypoint.x)
    X.append(waypoint.x1)
    Y.append(waypoint.y)
    Y.append(waypoint.y1)
    Z.append(waypoint.z)
    Z.append(waypoint.z1)

eval = evaluation.Validation()
sphere = (X[-2], Y[-2], eval._meters_to_degrees(Z[-2]))

for i in range(len(x)):
    point = (x[i], y[i], eval._meters_to_degrees(z[i]))
    if eval._is_point_in_sphere(point, sphere, eval._meters_to_degrees(0.15)):
        print True
        exit(0)

print False