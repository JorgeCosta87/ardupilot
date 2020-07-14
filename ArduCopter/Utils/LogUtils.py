from collections import namedtuple
from enum import IntEnum
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

        x.append(float(split[2]));
        y.append(float(split[3]));
        z.append(float(split[4]));

    file.close();

    return x, y, z;


class WPaction(IntEnum):
    VERTICAL_UP     = 0
    VERTICAL_DOWN   = 1
    HORIZONTAL      = 2
    ROTATE          = 3
    

def GetMissionWaypoints(filename):
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
    rotate  = 115;

    #Reads first line and set's up variables
    line = file.readline();
    split = line.split("\t");

    default = namedtuple("coord", "lng lat alt");
    default.lng = float(split[9]);
    default.lat = float(split[8]);
    default.alt = float(0);
    initialHeight = float(split[10]);
    

    last = namedtuple("coord", "x y z x1 y1 z1 type delay");
    last.x1 = default.lng;
    last.y1 = default.lat;
    last.z1 = default.alt;

    #Coordinates list
    coords = [];
    for line in file:
        split = line.split("\t"); 

        #The drone action
        action = int(split[3]);

        data = namedtuple("coord", "x y z x1 y1 z1 type delay");
        data.delay = 0.0
        
        if(action == waypoint):

            #Get Current position
            data.x = last.x1;
            data.y = last.y1;
            data.z = last.z1;
            
            #Get next way point 
            data.x1 = float(split[9]);
            data.y1 = float(split[8]);
            data.z1 = float(default.alt + float(split[10]));

            #Get delay
            data.delay = float(split[4]);
            
            #if the drone is going up and down in the exact same position
            if data.x == data.x1 and data.y == data.y1:
                if data.z < data.z1:
                    data.type = WPaction.VERTICAL_UP
                else:
                    data.type = WPaction.VERTICAL_DOWN

            else:
                data.type = WPaction.HORIZONTAL


        elif(action == takeoff or action == landing):
            
            #Get Current position
            data.x = last.x1;
            data.y = last.y1;
            data.z = last.z1;

            #Get next way point 
            data.x1 = last.x1;
            data.y1 = last.y1;
            data.z1 = float(default.alt + float(split[10]));

            data.type = WPaction.VERTICAL_UP

            if(action == landing):
                data.z1 = -(initialHeight - float(split[10]))
                data.type = WPaction.VERTICAL_DOWN

        else:
            continue
        
        #points to last waypoint so that it's possible to calculate the next one
        last = data;
        coords.append(data);

    file.close();
    return coords;


from datetime import datetime

def getFaultyPoints(timestampFilename, coordinatesFilename):
    if not os.path.isfile(timestampFilename):
        raise Exception("File" + timestampFilename + "does not exist");

    if not os.path.isfile(coordinatesFilename):
        raise Exception("File" + coordinatesFilename + "does not exist");

    coordinates = open(coordinatesFilename, "rt");
    timestamps = open(timestampFilename, "rt");

    #Tupple storage
    faults = [];

    stampContents = timestamps.read().splitlines();

    #Check if there's start and endpoints for all faults if not remove last point
    if (len(stampContents) % 2) == 1:
        myrange = len(stampContents) - 1;
    else:
        myrange = len(stampContents);

    for i in range(0,myrange,2):
        fault = namedtuple("coords", "x y z");
        fault.x = [];
        fault.y = [];
        fault.z = [];

        try:
            line = stampContents[i];
            tsSplit = line.split(",");
            injectionTimeStart = datetime.strptime(tsSplit[0], '%Y-%m-%d %H:%M:%S.%f');

            line = stampContents[i+1];
            tsSplit = line.split(",");
            injectionTimeEnd = datetime.strptime(tsSplit[0], '%Y-%m-%d %H:%M:%S.%f');

        except:
            if ((len(fault.x) % 2) != 0) and len(fault.x) > 0:
                fault.x.pop();
                fault.y.pop();
                fault.z.pop();
                break;

        while True:
            coord = coordinates.readline();
            coordSplit = coord.split(",");

            if len(coordSplit) < 5:
                break

            logTime = datetime.strptime(coordSplit[1], '%Y-%m-%d %H:%M:%S.%f')

            if logTime >= injectionTimeStart and logTime <= injectionTimeEnd:
                fault.x.append(float(coordSplit[2]));
                fault.y.append(float(coordSplit[3]));
                fault.z.append(float(coordSplit[4]));

            elif logTime > injectionTimeEnd:
                break;
        
        faults.append(fault);

    timestamps.close();
    coordinates.close();

    return faults;