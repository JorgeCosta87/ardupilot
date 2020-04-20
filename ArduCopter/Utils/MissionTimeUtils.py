from geopy.distance import distance
from LogUtils import GetMissionWaypoints
from LogUtils import WPaction as movement
import math

def calculate_acceleration(dist_xy, dist_z, vel, accel_xy, accel_z):
    return math.sqrt( (vel ** 2) / (((accel_xy * dist_xy) ** 2) + ((accel_z * dist_z) ** 2)) )

def getEstimatedMissionTime(filename, accel_xy = 100, accel_z = 100, up_speed = 2.5, dn_speed = 1.5, wp_speed = 5.0, emulation_speed = 1):
    waypointSpeed = ([up_speed * emulation_speed, dn_speed * emulation_speed, wp_speed * emulation_speed])
    time_in_seconds = 0

    #Since we aren't compensating for gravity, we use these constants to simulate the error caused by it
    GRAVITY_Z = 0.7
    GRAVITY_XY = 0.35

    mission = GetMissionWaypoints(filename);
    for waypoint in mission:
        z_distance = abs(waypoint.z1 - waypoint.z)
        xy_distance = distance((waypoint.y,waypoint.x),(waypoint.y1, waypoint.x1)).meters

        accelTime = calculate_acceleration(xy_distance, z_distance, waypointSpeed[waypoint.type], accel_xy, accel_z)

        if waypoint.type == movement.HORIZONTAL:
            #Calculate mission time without acceleration
            time_in_seconds += ( (xy_distance / waypointSpeed[waypoint.type]))

            #Add acceleration to time
            time_in_seconds += accelTime * 2
            time_in_seconds += (xy_distance * GRAVITY_XY)

            #Check if the drone is flying diagonally and add compensation for it
            if z_distance > 0:
                if waypoint.z1 > waypoint.z:
                    accelTime = calculate_acceleration(0, z_distance, waypointSpeed[movement.VERTICAL_UP], 0, accel_z)
                    time_in_seconds += ( (z_distance / waypointSpeed[movement.VERTICAL_UP]) )

                else:
                    accelTime = calculate_acceleration(0, z_distance, waypointSpeed[movement.VERTICAL_DOWN], 0, accel_z)
                    time_in_seconds += ( (z_distance / waypointSpeed[movement.VERTICAL_DOWN]) )

                time_in_seconds += accelTime * 2 
                time_in_seconds += (z_distance * GRAVITY_Z)

        else:
            time_in_seconds += ( z_distance / waypointSpeed[waypoint.type] )
            time_in_seconds += (z_distance * GRAVITY_Z)
            time_in_seconds += accelTime * 2

    return time_in_seconds;