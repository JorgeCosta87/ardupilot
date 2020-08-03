#!/bin/bash
mypath="$(dirname "$1")"

writeResults(){
    IFS=""
    fullLine="${array[0]}"
    for (( i = 1; i < ${#array[@]}; i++)); do
        fullLine="$fullLine,${array[i]}"
    done

    printf "$fullLine\n"
}

getTestFolder(){
    missionName="${3%.*}"
	missionName="${missionName// /_}"

    testFolder="$missionName""_$1/Run_$2"
}

handleNormal(){
    getTestFolder "${array[0]}" "${array[1]}" "${array[3]}"
    array[((${#array[@]}-1))]=$(./EvaluateMission.py "../Missions/$missionName"".txt" "$mypath/$testFolder/gps.log")
}

getLastWaypoint(){
    getTestFolder "${array[0]}" "${array[1]}" "${array[3]}"
    array[19]=$(./DroneCrossedWaypoint.py "../Missions/$missionName"".txt" "$mypath/$testFolder/gps.log")

    line=1
    while [ True ]; do
        array[20]=$(tail -$line "$mypath/$testFolder/faults.log" | head -1 | cut -d "," -f23)

        re='^[0-9]+$'
        if [[ ${array[20]} =~ $re ]] ; then
            break;
        fi
        echo "increment\n\n"
        ((line++))
    done
}

main(){
    {
        while [ True ]; do
            IFS=","
            read -ra array
            if ((${#array[@]} < 3)); then
                break;
            fi

            #if [ ${array[18]} == "NORMAL" ]; then
            #    handleNormal
            #fi

            if [ ${array[18]} == "CRASH" ]; then
                getLastWaypoint
            else
                #Hard coding at it's finest
                array[19]="True"
                array[20]="14"
            fi

            writeResults
        done

    } < "$1"
}



main "$@"