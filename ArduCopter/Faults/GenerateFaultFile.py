#!/usr/bin/env python
import sys
sys.path.append('../Utils')

from Enumerators import Sensor, Method


# Returns an array of arrays with the noise parameters for the Mean and Deviation
# example: gerNoiseArrayCombination([ 0.5, 1.0, 5.0, 10.0 ], [ 0.5, 1.0, 5.0, 10.0 ])
# output: [ [0.5, 0.5], [0.5, 1.0], [0.5, 5.0], [0.5, 10.0], [1.0, 0.5], ... , [ 10.0, 10.0 ]]
# The arrays don't need to be the same, but for the sake of simplicity that's what was used for this example
def getNoiseArrayCombination(arrayMean, arrayDeviation):
    array = []
    
    for mean in arrayMean:
        for deviation in arrayDeviation:
            array.append([ deviation * 1.0, mean * 1.0 ])

    return array

def getXYZCombo(arrayX, arrayY = [], arrayZ = []):
    array = []

    count = max([len(arrayX), len(arrayY), len(arrayZ)])

    for index in range(count):
        if index < len(arrayX):
            x = arrayX[index] * 1.0
        else:
            x = 0.0

        if index < len(arrayY):
            y = arrayY[index] * 1.0
        else:
            y = 0.0

        if index < len(arrayZ):
            z = arrayZ[index] * 1.0
        else:
            z = 0.0

        array.append([x,y,z])
    
    return array

def getParameterValues(method, sensor):
    minvals = None
    maxvals = None
    noises  = None

    if method == Method.MAX_VALUE or method == Method.DOUBLE_MAX:
        if sensor == Sensor.COMPASS:
            maxvals = [ 4900 ]

        elif sensor == Sensor.GYROSCOPE:
            maxvals = [ 34 ]

        elif sensor == Sensor.TEMPERATURE:
            maxvals = [ 85 ]
        
        elif sensor == Sensor.BAROMETER:
            maxvals = [ 120000 ]

        else: #acceleromenter
            maxvals = [ 156 ]

    else:
        maxvals = [ 0 ]

    if method == Method.MIN_VALUE:
        if sensor == Sensor.COMPASS:
            minvals = [ -4900 ]

        elif sensor == Sensor.GYROSCOPE:
            minvals = [ -90 ]

        elif sensor == Sensor.TEMPERATURE:
            minvals = [ -40 ]
        
        elif sensor == Sensor.BAROMETER:
            minvals = [ -120000 ]

        else: #acceleromenter
            minvals = [ 0 ]

    else:
        minvals = [ 0 ]

    if method == Method.NOISE:
        if sensor == Sensor.COMPASS:
            noises = getNoiseArrayCombination([ 50.0, 500.0, 1500.0 ], [ 1500.0 ])

        elif sensor == Sensor.GYROSCOPE:
            noises = getNoiseArrayCombination([ 5.0, 20.0, 40.0 ], [ 20.0 ])

        elif sensor == Sensor.TEMPERATURE:
            noises = getNoiseArrayCombination([ 5.0, 10.0, 20.0 ], [ 5.0 ])
        
        elif sensor == Sensor.BAROMETER:
            noises = getNoiseArrayCombination([ 1000.0, 10000.0, 30000.0 ], [ 5000.0 ])

        else: #acceleromenter
            noises = getNoiseArrayCombination([ 5.0, 10.0, 50.0 ], [ 15.0 ])
    
    else:
        noises = getNoiseArrayCombination([ 0.0 ], [ 0.0 ])

    if method == Method.OFFSET:

        if sensor == Sensor.COMPASS:
            xyz_vals = getXYZCombo([0.1, 1, 10, 100, 1000, -0.1, -1, -10, -100, -1000 ])
            xyz_vals += getXYZCombo([],[0.01, 0.1, 1, 10, 100, 1000, -0.01, -0.1, -1, -10, -100, -1000])
            xyz_vals += getXYZCombo([],[],[0.1, 1, 10, 100, 1000, -0.1, -1, -10, -100, -1000 ])

        elif sensor == Sensor.GYROSCOPE:
            xyz_vals = getXYZCombo([0.001, 0.01, 0.1, 1, 10, 100, 1000, -0.001, -0.01,-0.1, -1, -10, -100, -1000 ])
            xyz_vals += getXYZCombo([],[0.001, 0.01, 0.1, 1, 10, 100, 1000, -0.001, -0.01,-0.1, -1, -10, -100, -1000 ])
            xyz_vals += getXYZCombo([],[],[0.01, 0.1, 1, 10, 100, 1000, -0.01, -0.1, -1, -10, -100, -1000])

        elif sensor == Sensor.TEMPERATURE:
            xyz_vals = getXYZCombo([ 1, 10, 100, 1000, 10000, -1, -10, -100, -1000, -10000])
        
        elif sensor == Sensor.BAROMETER:
            xyz_vals = getXYZCombo([ 0.1, 1, 10, 100, 1000, -0.1, -1, -10, -100, -1000 ])

        else: #acceleromenter
            xyz_vals = getXYZCombo([0.0001, 0.001, 0.01, 0.1, 0.5, 1, 10, 100, -0.0001, -0.001, -0.01,-0.1, -0.5, -1, -10, -100 ]) 
            xyz_vals += getXYZCombo([],[0.0001, 0.001, 0.01, 0.1, 0.5, 1, 10, 100, -0.0001, -0.001, -0.01,-0.1, -0.5, -1, -10, -100 ])
            xyz_vals += getXYZCombo([],[],[0.0001, 0.001, 0.01, 0.1, 0.5, 1, 10, 100, 1000, -0.0001, -0.001, -0.01, -0.5, -0.1, -1, -10, -100, -1000])

    elif method == Method.SCALE_MULTIPLY or method == Method.SCALE_DIVIDE:
        if sensor == Sensor.COMPASS:
            xyz_vals = getXYZCombo([ 1.5, 2, 4, 8, 16, 32, 64, 128, 256, 512 ])
            xyz_vals += getXYZCombo([],[ 1.5, 2, 4, 8, 16, 32, 64, 128, 256, 512 ])
            xyz_vals += getXYZCombo([],[],[ 1.5, 2, 4, 8, 16, 32, 64, 128, 256, 512 ])

        elif sensor == Sensor.GYROSCOPE:
            xyz_vals = getXYZCombo([ 1.2, 1.5, 1.8, 2, 4, 8 ])
            xyz_vals += getXYZCombo([],[ 1.2, 1.5, 1.8, 2, 4, 8 ])
            xyz_vals += getXYZCombo([],[],[ 1.2, 1.5, 1.8, 2, 4, 8 ])

        elif sensor == Sensor.BAROMETER:
            xyz_vals = getXYZCombo([ 1.2, 1.5, 1.8, 2 ])

        elif sensor == Sensor.TEMPERATURE:
            xyz_vals = getXYZCombo([ 2, 16, 32, 64, 128, 256, 1024 ])

        else:
            xyz_vals = getXYZCombo([ 1.2, 1.5, 1.8, 2 ])
            xyz_vals += getXYZCombo([],[ 1.2, 1.5, 1.8, 2 ])
            xyz_vals += getXYZCombo([],[],[ 1.2, 1.5, 1.8, 2 ])


    elif method == Method.STATIC:
        xyz_vals = [ [0.0,0.0,0.0] ]

    else:
        xyz_vals = [ [0.0,0.0,0.0] ]

    return minvals, maxvals, noises, xyz_vals


# Constants for code clarity
_DEVIATION  = 0
_MEAN       = 1

# Parameters
missions    = [ "agraria_complex.txt" ]
methods     = [ Method.SCALE_DIVIDE, Method.SCALE_MULTIPLY ]
sensors     = [ Sensor.BAROMETER, Sensor.TEMPERATURE ]
delays      = [ 0 ]
durations   = [ 0 ]
radiuses    = [ 15 ]
injc_on     = 1
trigger     = 1
idcounter   = 1

print "ID;ENABLED;MISSION;RADIUS;SENSOR;METHOD;DEALY_START;DURATION;WP_TRIGGER;X;Y;Z;MIN;MAX;NOISE_D;NOISE_M"
for mission in missions:
    for sensor in sensors: 
        for method in methods:
            minvals, maxvals, noises, xyz_vals = getParameterValues(method, sensor)
            for delay in delays:
                for duration in durations:
                    for noise in noises:
                        for valmin in minvals:
                            for valmax in maxvals:
                                for xyz in xyz_vals:
                                    for radius in radiuses:
                                        print("%s;%s;%s;%s;%s;%s;%s;%s;%s;%s;%s;%s;%s;%s;%s;%s" % (
                                                                    idcounter, injc_on, mission, radius,
                                                                    sensor.value, method.value, delay, duration, 
                                                                    trigger, xyz[0],xyz[1],xyz[2],
                                                                    valmin, valmax, noise[_DEVIATION], noise[_MEAN])
                                        )
                                        idcounter += 1