#!/bin/bash

usage(){
	echo "usage: $0 <optional: speed of simulation [0-5]> <option: output to console [1]>"
}

checkArguments(){
	if (($# == 0 )); then
		EMULATION_SPEED=1
		return;
	fi

	if [ $# == 2 ]; then
		CONSOLE=true;
	else
		CONSOLE=false;
	fi

	re='^[0-9]+([.][0-9]+)?$'
	if ! [[ $1 =~ $re ]]; then
		echo "argument must be a number!"
		usage
		exit 1;
	fi

	if (($1 > 5 )) || (( $1 <= 0 )); then
		usage
		exit 1;
	fi

	EMULATION_SPEED=$1
}

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
		
		#TODO: Check if this redirection, together with the constant output of information is altering the behaviour of the emulator.
		#start simulation

		if [ $CONSOLE==false ]; then
			xterm -hold -e "$HOME/ardupilot/Tools/autotest/sim_vehicle.py -j4 -l $lat,$lng,0,0 -S $EMULATION_SPEED > logs/faultLog_$currentMission.log 2>&1" &
		else
			xterm -hold -e "$HOME/ardupilot/Tools/autotest/sim_vehicle.py -j4 -l $lat,$lng,0,0 -S $EMULATION_SPEED" &
		fi

		#Wait for SITL to boot up
		sleep 30

		#Start fault injector, This does not mean it will inject faults.
		start=$SECONDS
		python runInjector.py $currentMission

		#Show duration of experiment
		duration=$((SECONDS-start))
		echo “Experiment $a took $duration seconds”
		
		killProcesses
	done
}

main(){
	checkArguments "$@"
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

main "$@"