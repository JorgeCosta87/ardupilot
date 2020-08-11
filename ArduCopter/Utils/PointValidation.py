import numpy as np
from LogUtils import WPaction
import LogUtils as utils
from Enumerators import State
import os.path
import math


class Validation:
    def __init__(self, minor = 1.5, major = 3):
        if minor <= 0 or major <= 0:
            minor = 1.5
            major = 3

        if minor > major:
            major = minor + 1

        #Exactly one meeter in GPS notation: https://gis.stackexchange.com/questions/8650/measuring-accuracy-of-latitude-and-longitude
        self.__METER_RADIUS = (0.00000953)
        self.__MINOR_METER_RADIUS = minor
        self.__MAJOR_METER_RADIUS = major
        self._MINOR_RADIUS = self._meters_to_degrees(self.__MINOR_METER_RADIUS)
        self._MAJOR_RADIUS = self._meters_to_degrees(self.__MAJOR_METER_RADIUS)


    def _meters_to_degrees(self, meters):
        return self.__METER_RADIUS * meters


    def _is_point_in_cylinder(self, point, p1, p2, radius):
        vec = p2 - p1
        const = radius * np.linalg.norm(vec)

        if np.count_nonzero(vec) == 0:
            return False

        return len(np.where(np.dot(point - p1, vec) >= 0 and np.dot(point - p2, vec) <= 0
                        and np.linalg.norm(np.cross(point - p1, vec)) <= const)[0]) > 0


    def _is_point_in_sphere(self, point, sphere, radius):
        return ((point[0] - sphere[0])**2) + ((point[1] - sphere[1])**2) + ((point[2] - sphere[2])**2) <= radius**2
        

    def check_corners(self, point, x, y, z):
        minor_check = False

        rng = [0,len(x)-1]
        rng += range(1, len(x)-1, 2)

        for i in rng:
            if self._is_point_in_sphere(point,(x[i],y[i],self._meters_to_degrees(z[i])), self._MINOR_RADIUS):
                return State.NORMAL

            elif self._is_point_in_sphere(point,(x[i],y[i],self._meters_to_degrees(z[i])), self._MAJOR_RADIUS):
                minor_check = True
        
        if minor_check == True:
            return State.MINOR_FAULT


    def evaluate_point(self, point, x, y, z):
        minor_fault_check = False

        # Convert altitude to angle
        point[2] = self._meters_to_degrees(point[2])

        # For each mission segment
        for i, j in zip(range(0,len(x),2), range(len(x)/2)):
            p1 = np.array([ x[i], y[i], self._meters_to_degrees(z[i])])
            p2 = np.array([ x[i+1], y[i+1], self._meters_to_degrees(z[i+1])])
            
            if self._is_point_in_cylinder(point, p1, p2, self._MINOR_RADIUS):
                return State.NORMAL
            
            elif self._is_point_in_cylinder(point, p1, p2, self._MAJOR_RADIUS):
                minor_fault_check = True


        corner_check = self.check_corners(point, x, y, z)
        if corner_check == State.NORMAL:
            return State.NORMAL

        if minor_fault_check == True or corner_check == State.MINOR_FAULT:
            return State.MINOR_FAULT
        
        return State. MAJOR_FAULT


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
        TEMP_STATUS = validate.evaluate_point(np.array([x[i],y[i],z[i]]), X, Y, Z)

        if TEMP_STATUS != State.NORMAL:
            STATUS = TEMP_STATUS

            error_x += [x[i]]
            error_y += [y[i]]
            error_z += [z[i]]

            if TEMP_STATUS == State.MAJOR_FAULT:
                break;

    return STATUS;