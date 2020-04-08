from geopy.distance import distance
from LogUtils import GetMissionWaypoints

def getEstimatedMissionTime(filename, up_speed = 2.5, dn_speed = 1.5, wp_speed = 5.0):
    waypointSpeed = ([dn_speed, up_speed, wp_speed]);
    time_in_seconds = 0;

    mission = GetMissionWaypoints(filename);
    for waypoint in mission:
        time_in_seconds += (distance((waypoint.y,waypoint.x),(waypoint.y1, waypoint.x1)).meters / waypointSpeed[waypoint.type])

    return time_in_seconds;