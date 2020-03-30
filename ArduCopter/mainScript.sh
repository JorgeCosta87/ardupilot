#!/bin/bash

askForInput(){
	echo -n "Enter number of faults > "
	read nFault

	echo -n "Enter number of repetions per fault> "
	read nRep

	#this is here for commodity of not creating a function just for it
	currentMission=1
}

killProcesses(){
	echo killing the processes
	
	pkill -9 xterm
	pkill -9 python

	#wait a while for the processes to be killed
	sleep 10
}

getMissionCoordinatesFromMissionFile() {

	{
		IFS=$(printf "\t")
		read
		read -ra pos
		lat=${pos[8]};
		lng=${pos[9]};

	} < $1
}

runTests(){
	for ((i=1; i<= $nRep ; i++)); do
		echo “Repetition $i”
		
		#start simulation
		xterm -hold -e ~/ardupilot/Tools/autotest/sim_vehicle.py -j4 -l $lat,$lng,0,0 &
		
		#Wait for SITL to boot up
		sleep 30

		#Start fault injector, This does not mean it will inject faults.
		start=$SECONDS
		python runInjector.py $a

		#Show duration of experiment
		duration=$((SECONDS-start))
		echo “Experiment $a took $duration seconds”
		
		killProcesses
	done
}

main(){
	askForInput

	{ #This is required so the redirection know it's targets
		read #Reads header of file
		while [ $currentMission -le $nFault ]; do
		
			IFS=';'
			read -ra array;
			
			#get current mission running
			filename="$HOME/ardupilot/ArduCopter/Missions/${array[2]}"
			
			#Gets lat and long from mission file
			getMissionCoordinatesFromMissionFile $filename

			#Run mission with n repetitions
			echo "Running mission $currentMission: ${array[2]},  with $nRep repetitions"
			runTests

			#go to next mission
			currentMission=$((currentMission+1))
		done

	} < "$HOME/ardupilot/ArduCopter/Faults/faults.csv"
}

main