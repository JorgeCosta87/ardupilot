#!/usr/bin/env python
import sys
sys.path.append('../Utils')

from Enumerators import Sensor, Method

# Constants for code clarity
_DEVIATION  = 0
_MEAN       = 1



# Returns an array of arrays with the noise parameters for the Mean and Deviation
# example: gerNoiseArrayCombination([ 0.5, 1.0, 5.0, 10.0 ], [ 0.5, 1.0, 5.0, 10.0 ])
# output: [ [0.5, 0.5], [0.5, 1.0], [0.5, 5.0], [0.5, 10.0], [1.0, 0.5], ... , [ 10.0, 10.0 ]]
# The arrays don't need to be the same, but for the sake of simplicity that's what was used for this example
def getNoiseArrayCombination(arrayMean, arrayDeviation):
    array = []
    
    for mean in arrayMean:
        for deviation in arrayDeviation:
            array.append([ deviation, mean ])

    return array

missions    = [ "straightLine.txt" ]
methods     = [ Method.NOISE ]
sensors     = [ Sensor.ACCELEROMETER, Sensor.COMPASS, Sensor.GYROSCOPE ]
delays      = [ 0 ]
durations   = [ 50, 100, 500, 1200000 ]
noises      = getNoiseArrayCombination([ 0.5, 1.0, 5.0, 10.0 ], [ 1.0, 2.0, 5.0 ])
minvals     = [ 0 ]
maxvals     = [ 0 ]
xyz_vals    = [ [0.0,0.0,0.0] ]
radiuses    = [ 5 ]
injc_on     = 1
trigger     = 1
idcounter   = 1

print "ID;ENABLED;MISSION;RADIUS;SENSOR;METHOD;DEALY_START;DURATION;WP_TRIGGER;X;Y;Z;MIN;MAX;NOISE_D;NOISE_M"
for mission in missions:
    for sensor in sensors: 
        for method in methods:
            for delay in delays:
                for duration in durations:
                    for noise in noises:
                        for valmin in minvals:
                            for valmax in maxvals:
                                for xyz in xyz_vals:
                                    for radius in radiuses:
                                        print("%s;%s;%s;%s;%s;%s;%s;%s;%s;%s;%s;%s;%s;%s;%s;%s" % (
                                                                    idcounter, injc_on, mission, radius,
                                                                    sensor, method, delay, duration, 
                                                                    trigger, xyz[0],xyz[1],xyz[2],
                                                                    valmin, valmax, noise[_DEVIATION], noise[_MEAN])
                                        )
                                        idcounter += 1

                    