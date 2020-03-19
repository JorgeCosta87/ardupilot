#!/bin/bash

echo -n "Enter number of faults > "
read nFault
a=1 


echo -n "Enter number of repetions per fault> "
read nRep

while [ $a -le $nFault ]  
do

echo "Start fault $a,  with $nRep repetitions"

for ((i=1; i<= $nRep ; i++))
do

	echo “Repetition $i”

	#start simulation
	xterm -hold -e ~/ardupilot/Tools/autotest/sim_vehicle.py -j4 -l 40.1846674593393,-8.41455034911633,0,0 & 

	sleep 30

	start=$SECONDS
	python runInjector.py $a

	duration=$((SECONDS-start))
	echo $duration

	duration=$((SECONDS-start))

	echo “Experiment $a took $duration seconds”
	echo killing the processes
	pkill -9 xterm
	pkill -9 python

	sleep 10
	done

a=$((a+1))
done


