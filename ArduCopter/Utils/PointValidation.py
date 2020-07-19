import numpy as np
from LogUtils import WPaction
import LogUtils as utils
from enum import IntEnum
import os.path
import math

class State(IntEnum):
    NORMAL      = 0
    MINOR_FAULT = 1
    MAJOR_FAULT = 2
    CRASH       = 3

class Validation:
    def __init__(self, minor = 1, major = 2):
        if minor > major:
            major = minor + 1

        #Exactly one meeter in GPS notation: https://gis.stackexchange.com/questions/8650/measuring-accuracy-of-latitude-and-longitude
        self.__METER_RADIUS = (0.00001 - 0.000001)
        self._MINOR_Z_RADIUS = None
        self._MAJOR_Z_RADIUS = None
        self._MINOR_XY_RADIUS = None
        self._MAJOR_XY_RADIUS = None

        self._set_radius(minor,major)

    def _set_radius(self, minor, major):
        if minor <= 0 or major <= 0:
            return 

        self._MINOR_Z_RADIUS = minor
        self._MAJOR_Z_RADIUS = major
        self._MINOR_XY_RADIUS = self.__METER_RADIUS * self._MINOR_Z_RADIUS
        self._MAJOR_XY_RADIUS = self.__METER_RADIUS * self._MAJOR_Z_RADIUS


    #From :https://stackoverflow.com/questions/26818772/python-checking-if-a-point-is-in-sphere-with-center-x-y-z/26818848 by - Smit
    def _point_in_circle(self, point, circle, radius):
        return (point[0] - circle[0])**2 + (point[1] - circle[1])**2 < radius **2


    def _get_slope(self, p1,p2):
        return (p2[1] - p1[1]) / (p2[0] - p1[0])


    def _get_origin(self, p1,p2):
        return p1[1] - (_get_slope(p1,p2) * p1[0])


    def _valid_value(self, value, p1, p2):
        return (value >= p1 and value <= p2) or (value <= p1 and value >= p2)
    

    def _get_line_equation(self, p1, p2):
        m = (p2[1] - p1[1]) / (p2[0] - p1[0])
        b = p1[1] - (m * p1[0])
        return m,b


    def distance_between_line_and_points(self, p1, p2, q):
        p1 = np.asarray(p1); p2 = np.asarray(p2); q  = np.asarray(q)
        return np.linalg.norm(np.cross(p2-p1, p1-q))/np.linalg.norm(p2-p1)


    def _point_in_cylinder(self, p1, p2, r, q, type):
        x = 0; y = 1; z = 2

        if type == WPaction.VERTICAL_UP or type == WPaction.VERTICAL_DOWN:
            return self._valid_value(q[z], p1[z], p2[z])
    
        m, b = self._get_line_equation((p1[x],p1[y]), (p2[x],p2[y]))
        result_y = abs(((m * q[x]) + b) - q[y])
        result_x = abs(((q[y] - b) / m) - q[x])

        return math.sqrt((result_x**2) + (result_y**2)) <= r


    def _altitude_check(self, point, y, z, type, i, j):
        if type[j] == WPaction.HORIZONTAL and y[i] != y[i+1]:
            #here, we are using the Y as x and Z as Y to find the correct height of the point
            m, b = self._get_line_equation((y[i], z[i]), (y[i+1], z[i+1]))
            result = abs(((m * point[1]) + b) - point[2])
            
            z_check_normal = result <= self._MINOR_Z_RADIUS
            z_check_minor  = result <= self._MAJOR_Z_RADIUS

        else:
            if self._valid_value(point[2], z[i], z[i+1]) == True:
                z_check_normal = True
                z_check_minor  = False
            else:
                z_check_normal =  (point[2] >= z[i]-self._MINOR_Z_RADIUS and point[2] <= z[i+1]+self._MINOR_Z_RADIUS) or (point[2] >= z[i]+self._MINOR_Z_RADIUS and point[2] <= z[i+1]-self._MINOR_Z_RADIUS)
                z_check_minor  =  (point[2] >= z[i]-self._MAJOR_Z_RADIUS and point[2] <= z[i+1]+self._MAJOR_Z_RADIUS) or (point[2] >= z[i]+self._MAJOR_Z_RADIUS and point[2] <= z[i+1]-self._MAJOR_Z_RADIUS)
        
        return z_check_normal, z_check_minor


    def _check_corners(self, point, x, y, z, minor_fault_check):
        rng = [0,len(x)-1]
        rng += range(1, len(x)-1, 2)
        print "checking corners"
        
        for i in rng:
            z_check_normal = (z >= z[i]-self._MINOR_Z_RADIUS and z <= z[i]+self._MINOR_Z_RADIUS)
            z_check_minor  = (z >= z[i]-self._MAJOR_Z_RADIUS and z <= z[i]+self._MAJOR_Z_RADIUS)

            if self._point_in_circle(point,[ x[i], y[i] ], self._MINOR_XY_RADIUS ) and z_check_normal:
                return State.NORMAL

            elif self._point_in_circle(point,[ x[i], y[i] ], self._MAJOR_XY_RADIUS) and z_check_minor:
                minor_fault_check[0] = True
                print "minor inside"
                #return State.MINOR_FAULT


    def is_point_inside(self, point, x, y, z, type):
        minor_fault_check = [False]
        for i, j in zip(range(0,len(x),2), range(len(x)/2)):
            p1 = np.array([ x[i], y[i], z[i]])
            p2 = np.array([ x[i+1], y[i+1], z[i+1]])

            z_check_normal, z_check_minor = self._altitude_check(point, y, z, type, i, j)
        
            #print "Z Check: ", z_check_normal, z_check_minor, type[j].name, " - ", j , " ## cylinder --> ",self._point_in_cylinder(p1,p2, self._MINOR_XY_RADIUS, point, type[j]),self._point_in_cylinder(p1,p2, self._MAJOR_XY_RADIUS, point, type[j])
            
            if self._point_in_cylinder(p1,p2, self._MINOR_XY_RADIUS, point, type[j]) and z_check_normal:
                return State.NORMAL
            
            elif self._point_in_cylinder(p1,p2, self._MAJOR_XY_RADIUS, point, type[j]) and z_check_minor:
                print "minor"
                #pa = [p1[0], p1[1]]
                #pb = [p2[0], p2[1]]
                #pt = [point[0], point[1]]
                #print '%f' % self.distance_between_line_and_points(pa, pb, pt) 
                minor_fault_check = [ True ]

                #return State.MINOR_FAULT

        
        corners = self._check_corners(point, x, y, z, minor_fault_check)
        if corners == State.NORMAL:
            return corners
        
        if minor_fault_check[0] == True:
            return State.MINOR_FAULT

        return State.MAJOR_FAULT


def EvaluateMission(mission_path, run):

    #check if files are valid
    if not os.path.isfile(mission_path):
        raise Exception('File\'' + mission_path + '\'does not exist');

    if not os.path.isfile(run):
        raise Exception('File\'' + run + '\'does not exist');

    #get gps values from logs
    x,y,z = utils.GetGPSData(run);
    
    #get mission coordinates
    mission = utils.GetMissionWaypoints(mission_path);
    
    X = []; Y = []; Z = []; wp_type = [];
    for waypoint in mission:
        X.append(waypoint.x);
        X.append(waypoint.x1);
        Y.append(waypoint.y);
        Y.append(waypoint.y1);
        Z.append(waypoint.z);
        Z.append(waypoint.z1);
        wp_type.append(waypoint.type);

    ##Evaluate mission
    STATUS = State.NORMAL
    error_x = []; error_y = []; error_z = []

    validate = Validation()

    #for each point in the logs
    for i in range(len(x)):
        TEMP_STATUS = validate.is_point_inside(np.array([x[i],y[i],z[i]]), X, Y, Z, wp_type)

        if TEMP_STATUS != State.NORMAL:
            STATUS = TEMP_STATUS

            error_x += [x[i]]
            error_y += [y[i]]
            error_z += [z[i]]

            if TEMP_STATUS == State.MAJOR_FAULT:
                break;

    return STATUS;