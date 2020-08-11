#!/bin/bash

usage(){
	printf "\n\033[1mUsage:\033[0m\n";
	printf "\033[1m -s \033[0m: Emulation Speed : range [1-5] : default [2]\n";
	printf "\033[1m -C \033[0m: Display Console Ouput : default [\033[1mOFF\033[0m]\n";
	printf "\033[1m -l \033[0m: path to store log results\n";
	printf "\033[1m -n \033[0m: Experiment count : range [1 - max faults file ] : default [ 1 ]\n";
	printf "\033[1m -r \033[0m: Experiment Repetition : range [ 1 - any ] : default [1]\n";
	printf "\033[1m -o \033[0m: Aditional address to connect a GCS: format [x.x.x.x:xxxx].\n";
	printf "\033[1m -h \033[0m: This help screen.\n";
}

argumentParsing(){
	# Move to ArduCopters root
	cd "${0%/*}"

	currentMission=1;
	CONSOLE=false;
	EMULATION_SPEED=2;
	nRep=1;
	nFault=1;

    while getopts ":s:l:Cr:n:ho:" opt; do
        case $opt in
            s) # emulation speed

				re='^[0-9]+([.][0-9]+)?$'
				if ! [[ $OPTARG =~ $re ]]; then
					echo "argument must be a number!"
					usage
					exit 1;
				fi

				if (($OPTARG > 5 )) || (( $OPTARG <= 1 )); then
					usage
					exit 1;
				fi

				EMULATION_SPEED=$OPTARG
                ;;
			
			C) # display console output
				CONSOLE=true;
                ;;

            l) # move log location
				if [ ! -d "$OPTARG" ]; then
					echo "Path: '$OPTARG' does not exist!"
					exit 1;
				fi

				logAlt=$(dirname "$OPTARG/.")
                ;;

			n) # number of tests to run

				re='[0-9]'
				if  [[ ! $OPTARG =~ $re ]] && [ ${OPTARG^^} != "ALL" ]; then
					echo "argument must be a number!"
					exit 1;
				fi

				# Get max lines
				local max=$(wc -l "Faults/faults.csv" | cut -d " " -f1)
				if [ ${OPTARG^^} == "ALL" ]; then
					nFault=$((max - 1))
				else

					if (( $OPTARG < 1 )); then
						nFault=1
					elif (( $OPTARG > max - 1 )); then
						nFault=$((max - 1))
					else
						nFault="$OPTARG"
					fi
				fi
				
                ;;
			
			r) # Repetition
				re='[0-9]'
				if ! [[ $OPTARG =~ $re ]]; then
					echo "argument must be a number!"
					exit 1;
				fi

				if (( $OPTARG < 1 )); then
					nRep=1
				else
					nRep=$OPTARG
				fi
                ;;

			o)
				local regex="^([0-9]{1,3})+(\.[0-9]{1,3}){3}:([0-9]{2,5})"
				if ! [[ $OPTARG =~ $regex ]]; then
					printf "\033[1;31mThe address '$OPTARG' is not valid!\n\033[0m"
					exit 1;
				fi
				
				#Get only the regex strig and ignore any extra data 
				OPTARG="${BASH_REMATCH[0]}"

				local IFS=".:";local -a a=($OPTARG)
				local quad
				for quad in {0..3}; do
					if [[ "${a[$quad]}" -gt 255 ]]; then
						printf "\033[1;31mThe address '$OPTARG' is not valid!\n\033[0m"
						exit 1;
					fi
				done

				IPADDRESS="$OPTARG"
				;;

			h)
				usage
				exit 0;
				;;

            \?)
                echo "Invalid option: -$OPTARG" >&2
                exit 1;
                ;;
            
            :)
                echo "Option -$OPTARG requires an argument." >&2
                exit 1
                ;;
        esac
    done
	
	printf "\033[1m\n\n---------------------------------------------\n\n"

	printf "Executing:\n"
	printf "Test Count: \t\t$nFault\n"
	printf "Repetition: \t\t$nRep\n"
	printf "Emulation Speed: \t$EMULATION_SPEED""x\n"
	printf "Console enabled: \t$CONSOLE\n"

	if [ ! -z $logAlt ]; then
		printf "Alternative log Location: $logAlt\n"
	fi

	[[ -z $IPADDRESS ]] || printf "GCS IP: \t\t$IPADDRESS\n"

	printf "\n---------------------------------------------\n\n\033[0m"

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
	timestamp=$(date +"%Y%m%d_%H%M%S")
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

	if [[ ! -f "logs/00000001.BIN" ]]; then
		printf "\033[1;31mThe mission was not ran!\n\033[0m";
		return;
	fi

	mv "logs/"*.BIN $rawLog;

	# Convert log to txt format
	./Utils/ExtractLog.sh -f "$rawLog" -s "$unfilteredLog";

	# Obtains sensor specific logs
	#./Utils/FilterLogs.sh -f "$unfilteredLog" -s "$runFolder/gps.log" -p;
	grep ": GPS {" "$unfilteredLog" | ./Utils/FilterGPSLogs > "$runFolder/gps.log"
	
	#./Utils/FilterLogs.sh -f "$unfilteredLog" -s "$runFolder/accelerometer.log" -a;
	#./Utils/FilterLogs.sh -f "$unfilteredLog" -s "$runFolder/barometer.log" -b;
	#./Utils/FilterLogs.sh -f "$unfilteredLog" -s "$runFolder/compass.log" -c;
	#./Utils/FilterLogs.sh -f "$unfilteredLog" -s "$runFolder/gyroscope.log" -g;
	
	#if fault injection is active then extract the fault injection logs
	if ((${array[1]} == 1)); then
		#./Utils/FilterLogs.sh -f "$unfilteredLog" -s "$runFolder/faultUnfiltered.log" -j;
		grep ": INJT {\|: ERR {" "$unfilteredLog" | ./Utils/FilterLogs > "$runFolder/faults.csv"
		
		#remove unnecessary entrances from fault.log
		sed -e 2p -e '$!d' "$runFolder/faults.csv" > "$runFolder/fault_interval.log"
	fi

	mv "logs/faultLog_$currentMission.log" "$runFolder/console.log";
	mv "logs/simulations_report.csv" "$runFolder/";
	rm "logs/"*.TXT;
	rm "$runFolder/unfilteredLog.log"
}

checkIfStuck(){
    # Get last log line and line from 15 seconds ago
    lastLine=$(tail -1 "$runFolder/gps.log" | head -1)
    coordsInit=$(echo "$lastLine" | cut -d "," -f3,4,5)
    
    stuck=$(tail -75 "$runFolder/gps.log" | head -1)
    coordsFinal=$(echo "$stuck" | cut -d "," -f3,4,5)

    coords="$coordsInit,$coordsFinal"
    
    # Test if it's in the same position within a radius of 30 cm
    stuck=$(./DroneCrossedWaypoint.py "$runFolder/gps.log" -c "$coords")
}

getMissionResult(){
	local CRASH="CRASH"
	local STUCK="STUCK"
	local LOST_PATH="LOST_PATH"
    local MAJOR_FAULT="MAJOR_FAULT"

	crashCount=$(grep -i "crash" "$runFolder/console.log" | wc -l)
	if (($crashCount > 0)); then
		result=$CRASH
		return
	fi

	# Read report and check if there was a timeout or not
	{
		IFS=","
		read
		read -ra pos
		timeout=${pos[3]};
	} < "$runFolder/simulations_report.csv"

	# if there was a timeout
	if [ "$timeout" == "Y" ]; then

		# get mission evaluation
		eval=$(./Utils/EvaluateMission.py "$currentMissionFileName" "$runFolder/gps.log")

        # Check if the drone is stuck or lost path
        checkIfStuck
		if [ "$stuck" == "True" ]; then
			result=$STUCK
		else
			result=$LOST_PATH
		fi
	else
		result=$(./Utils/EvaluateMission.py "$currentMissionFileName" "$runFolder/gps.log")
	fi
}

writeResults(){
	
	if [ ! -f "$runFolder/gps.log" ]; then
		return
	fi

	resultFile="$mainLogPath/Results.csv"
	
	local sensor
	local injection
	local method
	local result

	#if log file doesn't exist, write header and create file.
	if [ ! -f "$resultFile" ]; then
		printf "ID,REPETITION,INJECTION,MISSION_NAME,RADIUS,SENSOR,METHOD,DEALY_START" > "$resultFile" 
		printf ",INJECTION_DURATION,WP_TRIGGER,X,Y,Z,MIN,MAX,NOISE_D,NOISE_M,RUN_DURATION,MISSION_RESULT\n" >> "$resultFile"
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

		case ${array[5]} in
			0)
				method="STATIC"
				;;

			1)
				method="RANDOM"
				;;
			
			2)
				method="NOISE"
				;;
			
			3)
				method="REPEAT_LAST"
				;;
			
			4)
				method="DOUBLE_LAST"
				;;
			
			5)
				method="HALF_LAST"
				;;

			6)
				method="MAX_VALUE"
				;;

			7)
				method="DOUBLE_MAX"
				;;

			8)
				method="MIN_VALUE"
				;;

			9)
				method="OFFSET"
				;;

			10)
				method="SCALE_MULTIPLY"
				;;

			11)
				method="SCALE_DIVIDE"
				;;

			?)
				method="UNKNOWN"
				;;
		esac
	else
		injection="FALSE"
		sensor="NONE"
		method="NONE"
	fi

	#Evaluate Mission and obtain result
	getMissionResult

	#Get the run duration
	local firstLine=$(head -1 "$runFolder/gps.log" | cut -d "," -f2)
	local lastLine=$(sed -e '$!d' "$runFolder/gps.log" | cut -d "," -f2)
	local difference=$(./Utils/GetTimeDifference.py $firstLine $lastLine)

	array[15]=$(echo "${array[15]//[$'\t\r\n ']}")
	printf "$currentMission,$i,$injection,${array[2]},${array[3]},$sensor,$method," >> "$resultFile"
	printf "${array[6]},${array[7]},${array[8]},${array[9]},${array[10]},${array[11]}," >> "$resultFile"
	printf "${array[12]},${array[13]},${array[14]},${array[15]},$difference,$result\n" >> "$resultFile"
}

runTests(){
	for ((i=1; i<= $nRep ; i++)); do
		echo “Repetition $i”
		
		#Create folder for current repetition
		createRepetitionFolders $i

		#start simulation
		IFS=""
		simCommand="sim_vehicle.py -j4 -l $lat,$lng,0,0 -S $EMULATION_SPEED"
		[[ -z $IPADDRESS ]] || simCommand=$simCommand" --out=udp:$IPADDRESS"
		simCommand=$simCommand" > logs/faultLog_$currentMission.log 2>&1"
		xterm -hold -e $simCommand &

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

	# Moves logs to the alternate folder
	if [ ! -z $logAlt ]; then

		if (($nFault > 1)); then
			if [ ! -d "$logAlt/$mainLogPath" ]; then
				mkdir -p "$logAlt/$mainLogPath"
			fi
			mv "$missionLogFolder" "$logAlt/$mainLogPath"

		else
			if [ ! -d "$logAlt/logs" ]; then
				mkdir -p "$logAlt/logs"
			fi

			mv "$missionLogFolder" "$logAlt/logs"
		fi
	fi
}

#This creates the top level folder that will hold all the experiments of the execution
createExperimentsFolder(){
	getTimestap

	#check if the logs folder exists, if it doesn't, create it.
	if [ ! -d "logs" ]; then
		mkdir "logs"
	fi

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

	currentMissionFileName="$missionLogFolder/$missionName""_mission.txt"
	#copy mission file to current missionLogFolder
	cp $missionFilename "$currentMissionFileName"
}

generateOverviewFile(){

	# If we are using an alternative log storage directory from the default, set the variables according to the location
	local baseExperimentName=$(basename $missionLogFolder)
	if [ ! -z $logAlt ]; then

		resultFile="$logAlt/$mainLogPath/Results.csv"
		results_overview="$logAlt/$mainLogPath/Results_Overview.html"
		results_cleaned="$logAlt/$mainLogPath/Results_Cleaned.csv"

	else
		results_overview="$mainLogPath/Results_Overview.html"
		results_cleaned="$mainLogPath/Results_Cleaned.csv"
	fi

	# check if there are missions that failed to start
	failed=$(grep ",$" "$resultFile" | wc -l)

	if (($failed > 0)); then
		grep -v ",$" "$resultFile" >> "$results_cleaned"
		./Utils/GenerateOverviewPage.py "$results_cleaned" > "$results_overview"
	else
		./Utils/GenerateOverviewPage.py "$resultFile" > "$results_overview"
	fi
}

main(){
	argumentParsing "$@"

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

		if [ ! -z $logAlt ] && (($nFault > 1)); then
			mv $resultFile "$logAlt/$mainLogPath"

			rm -r $mainLogPath
		fi

		generateOverviewFile

	} < "$HOME/ardupilot/ArduCopter/Faults/faults.csv"
}

main "$@"
