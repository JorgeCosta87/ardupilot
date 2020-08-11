#!/usr/bin/env python

import PointValidation as evaluation
import LogUtils as utils
import os
from sys import argv
from optparse import OptionParser

def num(s):
    try:
        return float(s)
    except ValueError:
        return int(s)

parser = OptionParser("")
parser.add_option("-c", "--compare", dest="compare", help="Compares if 2 GPS coordninates are within a given radius of eachother.")
parser.add_option("-m", "--mission", dest="mission_path", help="Check if a gps coordinate is close to a given waypoint, HARDCODED TO waypoint 14")

(options, args) = parser.parse_args()

if len(args) != 1:
    parser.error("incorrect number of arguments")

if len(argv) < 3:
    print "Example: ", argv[0], "< run gps file > < -opt >"
    exit(1)

run = argv[1]

if options.mission_path:
    #check if files are valid
    if not os.path.isfile(options.mission_path):
        raise Exception('File\'' + mission_path + '\'does not exist')

    if not os.path.isfile(run):
        raise Exception('File\'' + run + '\'does not exist')

    # Load mission and data 
    x,y,z = utils.GetGPSData(run)
    mission = utils.GetMissionWaypoints(options.mission_path)
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
        if eval._is_point_in_sphere(point, sphere, eval._meters_to_degrees(0.30)):
            print True
            exit(0)
    
    print False

elif options.compare:
    eval = evaluation.Validation()

    split = options.compare.split(",")
    sphere = (float(split[0]),float(split[1]),eval._meters_to_degrees(num(split[2])))
    point  = (float(split[3]),float(split[4]),eval._meters_to_degrees(num(split[5])))

    if eval._is_point_in_sphere(point, sphere, eval._meters_to_degrees(0.30)):
        print True
    else:
        print False