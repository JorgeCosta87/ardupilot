
import dronekit_sitl
from dronekit_sitl import SITL
import time
from dronekit import connect, VehicleMode, LocationGlobalRelative, LocationGlobal, Command, Parameters
from pymavlink import mavutil
import math

def arm_and_takeoff(aTargetAltitude):
    
    print "Basic pre-arm checks"
    # Don't let the user try to arm until autopilot is ready


    while not vehicle.is_armable:
        print " Waiting for vehicle to initialise..."
        time.sleep(1)
        
    print "Arming motors"
    # Copter should arm in GUIDED mode
    vehicle.mode = VehicleMode("GUIDED")
    vehicle.armed = True

    while not vehicle.armed:      
        print " Waiting for arming..."
        time.sleep(1)

    print "Taking off!"
    vehicle.simple_takeoff(aTargetAltitude) # Take off to target altitude
    
    while True:
        print " Altitude: ", vehicle.location.global_relative_frame.alt      
        if vehicle.location.global_relative_frame.alt>=aTargetAltitude*0.95: #Trigger just below target alt.
            print "Reached target altitude"
            break
        time.sleep(1)
def distance_to_current_waypoint():
    """
    Gets distance in metres to the current waypoint. 
    It returns None for the first waypoint (Home location).
    """
    nextwaypoint = vehicle.commands.next
    if nextwaypoint==0:
        return None
    missionitem=vehicle.commands[nextwaypoint-1] #commands are zero indexed
    lat = missionitem.x
    lon = missionitem.y
    alt = missionitem.z
    targetWaypointLocation = LocationGlobalRelative(lat,lon,alt)
    distancetopoint = get_distance_metres(vehicle.location.global_frame, targetWaypointLocation)
    return distancetopoint

def get_distance_metres(aLocation1, aLocation2):
    """
    Returns the ground distance in metres between two LocationGlobal objects.

    This method is an approximation, and will not be accurate over large distances and close to the 
    earth's poles. It comes from the ArduPilot test code: 
    https://github.com/diydrones/ardupilot/blob/master/Tools/autotest/common.py
    """
    dlat = aLocation2.lat - aLocation1.lat
    dlong = aLocation2.lon - aLocation1.lon
    return math.sqrt((dlat*dlat) + (dlong*dlong)) * 1.113195e5


def readmission(filename):
    """
    Load a mission from a file into a list. The mission definition is in the Waypoint file
    format (http://qgroundcontrol.org/mavlink/waypoint_protocol#waypoint_file_format).

    This function is used by upload_mission().
    """
    print "\nReading mission from file: %s" % filename
    cmds = vehicle.commands
    missionlist=[]
    with open(filename) as f:
        for i, line in enumerate(f):
            if i==0:
                if not line.startswith('QGC WPL 110'):
                    raise Exception('File is not supported WP version')
            else:
                linearray=line.split('\t')
                ln_index=int(linearray[0])
                ln_currentwp=int(linearray[1])
                ln_frame=int(linearray[2])
                ln_command=int(linearray[3])
                ln_param1=float(linearray[4])
                ln_param2=float(linearray[5])
                ln_param3=float(linearray[6])
                ln_param4=float(linearray[7])
                ln_param5=float(linearray[8])
                ln_param6=float(linearray[9])
                ln_param7=float(linearray[10])
                ln_autocontinue=int(linearray[11].strip())
                cmd = Command( 0, 0, 0, ln_frame, ln_command, ln_currentwp, 11, ln_param1, ln_param2, ln_param3, ln_param4, ln_param5, ln_param6, ln_param7)
                missionlist.append(cmd)
    return missionlist


def upload_mission(fileName):
        
        #Read mission from file
        missionlist = readmission(fileName)

        print "\nUpload mission from a file: %s" % fileName
        #Clear existing mission from vehicle
        print ' Clear mission'
        cmds = vehicle.commands
        cmds.clear()
        #Add new mission to vehicle
        for command in missionlist:
            cmds.add(command)
        print ' Upload mission'
        vehicle.commands.upload()

def setFaultInjectorParams(id, filename):

    print "Load fault injector params"

    with open(filename) as f:
        for i, line in enumerate(f):
            if i == 0 :
                continue;

            if i == id : 
                
                linearray=line.split(';')

                #check if the next line is empty
                if linearray[0] == '':
                    break;

                vehicle.parameters['INJ_ENABLED'] = int(linearray[1])
                missionName = str(linearray[2])

                vehicle.parameters['WPNAV_RADIUS'] = int(linearray[3])
                vehicle.parameters['INJ_SENSORS'] = int(linearray[4])
                vehicle.parameters['INJ_METHOD'] = int(linearray[5])
                vehicle.parameters['INJ_DELAY'] = int(linearray[6])
                vehicle.parameters['INJ_DURATION'] = int (linearray[7])
                vehicle.parameters['INJ_WP_TRIG'] = int(linearray[8])
                wp_trigger = int(linearray[8])
                vehicle.parameters['INJ_FIELD_X'] = float(linearray[9])
                vehicle.parameters['INJ_FIELD_Y'] = float(linearray[10])
                vehicle.parameters['INJ_FIELD_Z'] = float(linearray[11])
                vehicle.parameters['INJ_MIN'] = int(linearray[12])
                vehicle.parameters['INJ_MAX'] = int(linearray[13])
                vehicle.parameters['INJ_NOISE_D'] = float(linearray[14])
                vehicle.parameters['INJ_NOISE_M'] = float(linearray[15])


    print "Fault injector params loaded successful id: %d" % id

    print "*********** fault parms **************"

    print "INJECT ENABLED: %s" % vehicle.parameters['INJ_ENABLED']
    print "MISSION: %s" % missionName
    print "RADIUS: %s" % vehicle.parameters['WPNAV_RADIUS']
    print "SENSOR: %s" % vehicle.parameters['INJ_SENSORS']
    print "METHOD: %s" % vehicle.parameters['INJ_METHOD']
    print "DELAY: %s" % vehicle.parameters['INJ_DELAY']
    print "DURATION: %s" % vehicle.parameters['INJ_DURATION']
    print "WP_TRIGGER: %s" % vehicle.parameters['INJ_WP_TRIG']
    print "X: %s" % vehicle.parameters['INJ_FIELD_X']
    print "Y: %s" % vehicle.parameters['INJ_FIELD_Y']
    print "Z: %s" % vehicle.parameters['INJ_FIELD_Z']
    print "MIN: %s" % vehicle.parameters['INJ_MIN']
    print "MAX: %s" % vehicle.parameters['INJ_MAX']
    print "NOISE_D: %s" % vehicle.parameters['INJ_NOISE_D']
    print "NOISE_M: %s" % vehicle.parameters['INJ_NOISE_M']
    print "***********  END **************"


    return missionName, wp_trigger
#%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%


#sitl = SITL('/home/sergio/ardupilot/build/sitl/bin/arducopter')
#lat = 40.1849000;
#lon = -8.41522000;
#args = ['--model','quad','--home','%f,%f,0,0' % (lat,lon,),'--defaults','/home/sergio/ardupilot/Tools/autotest/default_params/copter.parm','--autotest-dir','/home/sergio/ardupilot/build/sitl/bin/eeprom'] 
#sitl.launch(args, verbose=False, await_ready=False, restart=False, use_saved_data= True)
#sitl.block_until_ready(verbose=False) # explicitly wait until receiving commands

#sitl.poll() # returns None or return code

#connection_string = sitl.connection_string()
#print connection_string


# Import DroneKit-Python
from dronekit import connect, VehicleMode
import os.path
import sys, csv

print " Start simulator (SITL)"


argv = sys.argv

# Connect to the Vehicle.
vehicle = connect('udp:127.0.0.1:14551', wait_ready=True)

# set fault parms
print "Fault id: %d" % int(argv[1])
missionName, wp_trigger = setFaultInjectorParams(int(argv[1]),'Faults/faults.csv')

# Upload a mission
upload_mission('Missions/' + missionName)



# Arm and Takeoff
arm_and_takeoff(1.5)

print "Starting mission"
# Reset mission set to first (0) waypoint
vehicle.commands.next=0

# Set the vehicle into auto mode
vehicle.mode = VehicleMode("AUTO")
print " Mode: %s" % vehicle.mode.name

# Monitor mission. 
# Demonstrates getting and setting the command number 
# Uses distance_to_current_waypoint(), a convenience function for finding the 
#   distance to the next waypoint.

nextwaypoint=vehicle.commands.next
lastWP = nextwaypoint
start_time = time.time()
crash = 'N'

while nextwaypoint <= vehicle.commands.count:

    nextwaypoint=vehicle.commands.next

    # Start fault injecto at the wanted WP
    #if (nextwaypoint - 1) == wp_trigger and wp_trigger != -1:
    #    print "Start fault injenctor."
    #    #vehicle.parameters['INJ_ENABLED'] = 1

    #check if it's the last wapoint
    if(lastWP == vehicle.commands.count and nextwaypoint == 0):
        break;

    #Track the duration of each WP
    if(lastWP != nextwaypoint):
        start_time = time.time()
    
    #After 60 seconds in the same WP let's assume that we had a crash
    if((time.time() - start_time) >= 60):
        crash = 'Y'
        break;

    print 'Distance to waypoint (%s): %s' % (nextwaypoint, distance_to_current_waypoint())

    lastWP = nextwaypoint
    time.sleep(0.20)


    
print " Mode: %s" % vehicle.mode.name

# Shut down simulator
#sitl.stop()

has_header = False
fileExist = os.path.isfile("logs/simulations_report.csv")

with open('logs/simulations_report.csv', 'a+') as outcsv:
    writer = csv.DictWriter(outcsv, fieldnames = ["ID", "INJECTOR", "MISSION", "CRASH", "RADIUS", "SENSOR", "METHOD", "DELAY", "DURATION","WP_TRIGGER","X","Y", "Z", "MIN", "MAX", "NOISE_D", "NOISE_M"])
    
    if fileExist :
        sniffer = csv.Sniffer()
        has_header = sniffer.has_header(outcsv.read(2048))

    if not has_header :
        writer.writeheader()

    writer.writerow( {
        'ID': int(argv[1]), 'INJECTOR': vehicle.parameters['INJ_ENABLED'] ,'MISSION' : missionName, 'CRASH' : crash,
        'RADIUS': vehicle.parameters['WPNAV_RADIUS'],'SENSOR': vehicle.parameters['INJ_SENSORS'],
        'METHOD': vehicle.parameters['INJ_METHOD'], 'DELAY': vehicle.parameters['INJ_DELAY'],
        'DURATION': vehicle.parameters['INJ_DURATION'],'WP_TRIGGER':vehicle.parameters['INJ_WP_TRIG'],
        'X': vehicle.parameters['INJ_FIELD_X'], 'Y': vehicle.parameters['INJ_FIELD_Y'], 'Z': vehicle.parameters['INJ_FIELD_Z'],
        'MIN' : vehicle.parameters['INJ_MIN'], 'MAX': vehicle.parameters['INJ_MAX'],
        'NOISE_D':vehicle.parameters['INJ_NOISE_D'], 'NOISE_M':vehicle.parameters['INJ_NOISE_M']
      })


# Close vehicle object before exiting script
vehicle.close()
print("Completed")



    #PRINT POSITION

    #print "\n*********\nGlobal Location: %s" % vehicle.location.global_frame
    #print "Global Location (relative altitude): %s" % vehicle.location.global_relative_frame
    #print "Local Location: %s" % vehicle.location.local_frame    #NED