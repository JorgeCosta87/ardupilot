#!/usr/bin/env python

missions    = [ "straightLine.txt" ]
methods     = [ 2 ]
sensors     = [ 0, 1, 2, 3, 4 ]
delays      = [ 0,15000 ]
durations   = [ 100, 500, 1000, 10000, 120000 ]
noises      = [ [0.0, 20.0], [0.0, 50.0], [0.0, 80.0], [0.0, 100.0], [20.0, 0.0], [50.0, 0.0],[80.0, 0.0], [100.0, 0.0] ]
minvals     = [ 1.0 ]
maxvals     = [ 100.0 ]
xyz_vals    = [ [0.0,0.0,0.0] ]
radiuses    = [ 5.0 ]
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
                                                                    valmin, valmax, noise[0], noise[1])
                                        )
                                        idcounter += 1

                    