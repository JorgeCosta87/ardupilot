import numpy as np
from LogUtils import WPaction
from enum import IntEnum

def points_in_cylinder(pt1, pt2, r, q):
    vec = pt2 - pt1
    const = r * np.linalg.norm(vec)

    return (np.dot(q - pt1, vec) >= 0 and np.dot(q - pt2, vec) <= 0 \
            and np.linalg.norm(np.cross(q - pt1, vec)) <= const)


def get_line_equation(pointA, pointB):
    x_coords, y_coords = zip(*[pointA, pointB])

    A = np.vstack([x_coords, np.ones(len(x_coords))]).T
    m, b = np.linalg.lstsq(A, y_coords)[0]

    return m,b;


#From :https://stackoverflow.com/questions/26818772/python-checking-if-a-point-is-in-sphere-with-center-x-y-z/26818848 by - Smit
def in_sphere(point, sphere, radius):
    return (point[0] - sphere[0])**2 + (point[1] - sphere[1])**2 < radius ** 2


class State(IntEnum):
    NORMAL      = 0
    MINOR_FAULT = 1
    MAJOR_FAULT = 2


def get_point_status(point, wp_x, wp_y, wp_z, wp_type):
    #Exactly one meeter in GPS notation: https://gis.stackexchange.com/questions/8650/measuring-accuracy-of-latitude-and-longitude
    GPS_NORMAL_RADIUS = (0.000001 * 10) - (0.0000001 * 10) #Exactly 1 meter

    #The minor fault boundary limit is equal to 150% of the normal gps boudary
    GPS_HIGH_RADIUS = GPS_NORMAL_RADIUS * 1.50 #Exactly 1.5 meters

    #Since the Altitude is measured in meters, we use M_RADIUS as the meter radius. It contains the largest radius. 
    M_RADIUS = 1.5 #Meter

    for i, j in zip(range(0,len(wp_x),2), range(len(wp_x)/2)):
        point1 = np.array([ wp_x[i], wp_y[i], 0 ])
        point2 = np.array([ wp_x[i+1], wp_y[i+1], 0 ])
        z = point[2]

        if wp_type[j] == WPaction.HORIZONTAL:
            #here, we are using the Y as x and Z as Y to find the correct height of the point
            x = point[1]
            m, b = get_line_equation((wp_y[i], wp_z[i]), (wp_y[i+1], wp_z[i+1]))
            result = abs(((m * x) + b) - z)
            z_check = result <= M_RADIUS
        
        else:
            z_check = (z >= wp_z[i] and z <= wp_z[i+1]) or (z <= wp_z[i] and z >= wp_z[i+1])
            

        if points_in_cylinder(point1,point2, GPS_NORMAL_RADIUS, point) and z_check:
            return State.NORMAL

        elif points_in_cylinder(point1,point2, GPS_HIGH_RADIUS, point) and z_check:
            return State.MINOR_FAULT

    
    #Check if the point is not in a corner
    rng = [0,len(wp_x)-1]
    rng += range(1, len(wp_x)-1, 2)
    
    for k in rng:
        z_check = wp_z[k] - point[2] < M_RADIUS

        if in_sphere(point,[ wp_x[k], wp_y[k] ], GPS_NORMAL_RADIUS) and z_check:
            return State.NORMAL

        elif in_sphere(point,[ wp_x[k], wp_y[k] ], GPS_HIGH_RADIUS) and z_check:
            return State.MINOR_FAULT
    
    return State.MAJOR_FAULT