#!/bin/bash

usage(){
	echo "usage: $0 <optional: speed of simulation [0-5]> <option: output to console [1]>"
}

checkArguments(){
	if (($# == 0 )); then
		EMULATION_SPEED=1
		return;
	fi

	if (($# == 2)); then
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

	if (( $nFault < 1 )); then
		nFault=1
	fi

	if (( $nRep < 1 )); then
		nRep=1
	fi
}

killProcesses(){
	echo killing the processes
	
	pkill -9 xterm
	pkill -9 python

	#wait a while for the processes to be killed
	sleep 10
}

fileExists(){
	if [ ! -f $1 ]; then
		printf "\033[1;91mMission file \033[0;1m'$1'\033[1;91mdoes not exist, quitting...\033[0m\n"
		exit 1;
	fi
}

getTimestap(){
	timestamp=$(date +"%d%m%Y_%H%M%S")
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

createRepetitionFolders(){
	if (($nRep > 1)); then
		runFolder="$missionLogFolder""/Run_$1"

		if [ ! -d $runFolder ]; then
			mkdir $runFolder
		fi
	else
		runFolder="$missionLogFolder"
	fi
}

handleLogs(){
	local rawLog="$runFolder/log.bin"
	local unfilteredLog="$runFolder/unfilteredLog.log"

	mv "logs/"*.BIN $rawLog;

	./Utils/ExtractLog.sh -f "$rawLog" -s "$unfilteredLog";
	./Utils/FilterLogs.sh -f "$unfilteredLog" -s "$runFolder/gps.log" -p;

	#if fault injection is active then extract the fault injection logs
	if ((${array[1]} == 1)); then
		./Utils/FilterLogs.sh -f "$unfilteredLog" -s "$runFolder/faultUnfiltered.log" -j;

		#remove unnecessary entrances from fault.log
		sed -e 1b -e '$!d' "$runFolder/faultUnfiltered.log" > "$runFolder/fault.log"
	fi

	mv "logs/faultLog_$currentMission.log" "$runFolder/console.log";
	mv "logs/simulations_report.csv" "$runFolder/";
	rm "logs/"*.TXT;
}

CrashCheck() {

	{
		IFS=","
		read
		read -ra pos
		crash=${pos[3]};
	} < "$runFolder/simulations_report.csv"

	if [ "$crash" == "N" ]; then
		crashCount=$(grep -i "crash" "$runFolder/console.log" | wc -l)

		if (($crashCount > 0)); then
			crash="Y"
		fi
	fi
}

writeResults(){
	resultFile="$mainLogPath/Results.csv"
	
	local sensor
	local injection
	local result

	#if log file doesn't exist, write header and create file.
	if [ ! -f "$resultFile" ]; then
		printf "ID,REPETITION,INJECTION,MISSION_NAME,RADIUS,SENSOR,METHOD,DEALY_START" > "$resultFile" 
		printf ",DURATION,WP_TRIGGER,X,Y,Z,MIN,MAX,NOISE_D,NOISE_M,MISSION_RESULT\n" >> "$resultFile"
	fi

	if [ "${array[1]}" == 1 ]; then
		injection="TRUE"

		case ${array[4]} in
			0)
				sensor="COMPASS"
				;;

			1)
				sensor="GYROSCOPE"
				;;
			
			2)
				sensor="ACCELEROMETER"
				;;
			
			3)
				sensor="BAROMETER"
				;;
			
			4)
				sensor="TEMPERATURE"
				;;

			?)
				sensor="UNKNOWN"
				;;
		esac
	else
		injection="FALSE"
		sensor="NONE"
	fi

	#Check if drone crashed
	CrashCheck
	if [ "$crash" == "Y" ]; then
		result="CRASH"
	else
		result=$(python Utils/EvaluateMission.py "$missionFilename" "$runFolder/gps.log")
	fi

	printf "$currentMission,$i,$injection,${array[2]},${array[3]},$sensor,${array[5]}," >> "$resultFile"
	printf "${array[6]},${array[7]},${array[8]},${array[9]},${array[10]},${array[11]}," >> "$resultFile"
	printf "${array[12]},${array[13]},${array[14]},${array[15]},$result\n" >> "$resultFile"
}

runTests(){
	for ((i=1; i<= $nRep ; i++)); do
		echo “Repetition $i”
		
		#Create folder for current repetition
		createRepetitionFolders $i

		#start simulation
		xterm -hold -e "$HOME/ardupilot/Tools/autotest/sim_vehicle.py -j4 -l $lat,$lng,0,0 -S $EMULATION_SPEED > logs/faultLog_$currentMission.log 2>&1" &

		if [ "$CONSOLE" == true ]; then
			sleep 3
			xterm -hold -e "tail -f logs/faultLog_$currentMission.log" &
		fi

		#Wait for SITL to boot up
		sleep 30

		#Start fault injector, This does not mean it will inject faults.
		start=$SECONDS	
		python runInjector.py $currentMission $EMULATION_SPEED

		#Show duration of experiment
		duration=$((SECONDS-start))
		echo “Experiment $a took $duration seconds”
		
		killProcesses

		#move logs to current repetition folder and unpack them
		handleLogs
		#write results to file
		writeResults

	done
}

#This creates the top level folder that will hold all the experiments of the execution
createExperimentsFolder(){
	getTimestap

	if (($nFault > 1)); then
		mainLogPath="logs/Experiments_$timestamp"
	else
		mainLogPath="logs/Experiment_$timestamp"
	fi

	if [ ! -d $mainLogPath ]; then
		mkdir $mainLogPath
	fi
}

createMissionFolder(){
	missionName="${1%.*}"
	missionName="${missionName// /_}"

	if (($nFault > 1)); then
		missionLogFolder=$mainLogPath"/"$missionName"_"$currentMission

		if [ ! -d $missionLogFolder ]; then
			mkdir $missionLogFolder
		fi
	else
		mv $mainLogPath "logs/Experiment_$timestamp""_""$missionName"
		
		mainLogPath="logs/Experiment_$timestamp""_""$missionName"
		missionLogFolder="$mainLogPath"
	fi

	#copy mission file to current missionLogFolder
	cp $missionFilename "$missionLogFolder/$missionName""_mission.txt"
}

generateOverviewFile(){
	results_overview="$mainLogPath/Results_Overview.html"
	local resultFile="$mainLogPath/Results.csv"
	results_cleaned="$mainLogPath/Results_Cleaned.csv"

	# check if there are missions that failed to start
	failed=$(grep ",$" "$resultFile" | wc -l)

	if (($failed > 0)); then
		grep -v ",$" "$resultFile" >> "$Results_cleaned"
		./Utils/GenerateOverviewPage.py "$Results_cleaned" > "$results_overview"
	else
		./Utils/GenerateOverviewPage.py "$resultFile" > "$results_overview"
	fi
}

main(){
	checkArguments "$@"
	askForInput

	{ #This is required so the redirection know it's targets

		#Create experiments folder that will hold all the experiments for each run
		createExperimentsFolder

		read #Reads header of file
		while [ $currentMission -le $nFault ]; do
		
			IFS=';'
			read -ra array;
			
			#get current mission running
			missionFilename="$HOME/ardupilot/ArduCopter/Missions/${array[2]}"
			
			#check if mission file exists before going further
			fileExists $missionFilename

			#Create mission folder
			createMissionFolder "${array[2]}"

			#Gets lat and long from mission file
			getMissionCoordinatesFromMissionFile $missionFilename

			#Run mission with n repetitions
			echo "Running mission $currentMission: ${array[2]},  with $nRep repetitions"
			runTests

			#go to next mission
			currentMission=$((currentMission+1))
		done

		generateOverviewFile

	} < "$HOME/ardupilot/ArduCopter/Faults/faults.csv"
}

main "$@"