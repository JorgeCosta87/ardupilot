#!/bin/bash

echo -n "Enter number of experiments > "
read noe
a=1 
while [ $a -le $noe ]  
do

echo “Experiment $a”

fileName=faults/FaultDef$a.csv
echo $fileName
cp $fileName FaultDef.csv

gnome-terminal -e ./sim_vehicle.sh &
#sim_pid=$!
#echo $sim_pid
sleep 30

start=$SECONDS
python runInjector.py &
#python_pid=$!
#echo $python_pid

duration=$((SECONDS-start))
echo $duration

while [ $duration -lt 60 ]
do
	sleep 1
	duration=$((SECONDS-start))
done

echo “Experiment $a took $duration seconds”
echo killing the processes
pkill -9 xterm
pkill -9 python
#kill -9 $python_pid
#kill -9 $sim_pid

sleep 10

a=$((a+1))


done
