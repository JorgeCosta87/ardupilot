#!/bin/bash

if (($# < 1)); then
    printf "\033[1mUsage: $0 < Results.csv file >\033[0m\n";
    exit 1
fi

cd "${0%/*}"
mypath="$(dirname "$1")"

writeResults(){
    IFS=""
    fullLine="${array[0]}"
    for (( i = 1; i < ${#array[@]}; i++)); do
        fullLine="$fullLine,${array[i]//[$'\t\r\n ']}"
    done

    printf "$fullLine\n"
}

checkIfStuck(){
    # Get last log line and line from 15 seconds ago
    lastLine=$(tail -1 "$testFolder/gps.log" | head -1)
    coordsInit=$(echo "$lastLine" | cut -d "," -f3,4,5)
    
    stuck=$(tail -75 "$testFolder/gps.log" | head -1)
    coordsFinal=$(echo "$stuck" | cut -d "," -f3,4,5)

    coords="$coordsInit,$coordsFinal"
    
    # Test if it's in the same position within a radius of 30 cm
    stuck=$(./DroneCrossedWaypoint.py "$testFolder/gps.log" -c "$coords")
}

getMissionResult(){
	local CRASH="CRASH"
	local STUCK="STUCK"
	local LOST_PATH="LOST_PATH"
    local MAJOR_FAULT="MAJOR_FAULT"

	crashCount=$(grep -i "crash" "$testFolder/console.log" | wc -l)
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
	} < "$testFolder/simulations_report.csv"

	# if there was a timeout
	if [ "$timeout" == "Y" ]; then

		# get mission evaluation
		eval=$(./EvaluateMission.py "../Missions/$missionName"".txt" "$testFolder/gps.log")

        # Check if the drone is stuck or lost path
        checkIfStuck
		if [ "$stuck" == "True" ]; then
			result=$STUCK
		else
            #check if eval is MAJOR_FAULT then it's lost path, otherwise it's stuck
            if [ "$eval" == "$MAJOR_FAULT" ]; then
			    result=$LOST_PATH
            else
                result=$STUCK
            fi
		fi
	else
		result=$(./EvaluateMission.py "../Missions/$missionName"".txt" "$testFolder/gps.log")
	fi
}

getTestFolder(){
    missionName="${3%.*}"
	missionName="${missionName// /_}"

    testFolder="$mypath/$missionName""_$1/Run_$2"
    if [ ! -d "$testFolder" ]; then
        testFolder="$mypath/$missionName""_$1"
    fi
}

evaluateRun(){
    getMissionResult
    array[((${#array[@]}-1))]="$result"
}

getLastWaypoint(){
    array[19]=$(./DroneCrossedWaypoint.py "$testFolder/gps.log" -m "../Missions/$missionName"".txt")

    line=1
    while [ True ]; do
        array[20]=$(tail -$line "$testFolder/faults.csv" | head -1 | cut -d "," -f23)

        re='^[0-9]+$'
        if [[ ${array[20]} =~ $re ]] ; then
            break;
        fi
        ((line++))
    done
}

main(){
    {
        read
        while [ True ]; do
            IFS=","
            read -ra array
            if ((${#array[@]} < 3)); then
                break;
            fi

            getTestFolder "${array[0]}" "${array[1]}" "${array[3]}"

            evaluateRun

            #if [ ${array[18]} == "NORMAL" ]; then
            #    evaluateRun
            #fi
            
            #if [ "${array[18]//[$'\t\r\n ']}" == "CRASH" ]; then
            #    getLastWaypoint
            #else
                #Hard coding at it's finest
            #    array[19]="True"
            #    array[20]="14"
            #fi

            writeResults
        done

    } < "$1"
}



main "$@"