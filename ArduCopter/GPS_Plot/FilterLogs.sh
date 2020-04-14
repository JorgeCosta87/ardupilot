#!/bin/bash

usage(){
    printf "\n\033[1;40mUsage:\033[0;40m\n";
    printf "\033[40m$0 <mandatory: -f filename.log> <optional: -s filetosave.log> \033[1;95;40m<optional:sensors -abcgp>\033[0;40m\n\n";
    printf "\033[40mSavefile: if the savefile -s argument is not specified the output is written directly into the console.\033[0m\n\n"
    printf "\033[1;40mSensors:\033[21m A sensor must be specified or the output will be null\n"
    printf "\033[1;95;40m -g Gyroscope\n"
    printf " -a  Accelerometer\n"
    printf " -b  Barometer\n"
    printf " -c  Compass\n"
    printf " -p  GPS\033[0;40m\n\n";
    printf "\033[1;40mExamples:\033[0m\n\033[1;32;40m$0 -f file.log -s savefile.txt -abcgp\033[0;40m\n";
	printf "\033[1;32;40m$0 -f file.log -g -a\033[0m\n\n";
}

writeToFile(){
    if [ -z $savefile ]; then
        echo "$data"
    else
        echo "$data" >> "$savefile";
    fi
}

parseArguments(){
    if [ $# == 0 ]; then
        usage
        exit 1;
    fi

    masks=();
    maskName=();
    while getopts ":h f: s: abcgpj" opt; do
        case $opt in
            f) #adding more files to parse
                #check if file exists
                if [ ! -f "$OPTARG" ]; then
                    echo "File $OPTARG does not exist!";
                    exit 1;
                fi

                filename="$OPTARG";
                ;;

            s) #this is the log,
                if [ -f "$OPTARG" ]; then
                    echo "A file with the name $OPTARG already exist!";
                    exit 1;
                fi

                if [ "$OPTARG" == "" ]; then
                    echo "Save file name cannot be \"$OPTARG\"."
                    exit 1;
                fi
                
                savefile="$OPTARG";
                ;;

            p) #GPS
                if [ ! -z $gps ]; then
                    continue;
                fi

                masks+=(": GPS {");
                maskName+=("GPS");

                local gps=true;
                ;;

            b) #Barometer
                if [ ! -z $barometer ]; then
                    continue;
                fi

                masks+=(": BARO {");
                maskName+=("BAROMETER");

                local barometer=true;
                ;;

            c) #compass
                if [ ! -z $compass ]; then
                    continue;
                fi

                masks+=(": MAG {");
                masks+=(": MAG2 {");
                maskName+=("COMPASS");
                maskName+=("COMPASS2");

                local compass=true;
                ;;

            a) #Accelerometer
                if [ ! -z $accelerometer ]; then
                    continue;
                fi

                masks+=(": IMU {");
                masks+=(": IMU2 {");
                maskName+=("GYRO/ACCEL");
                maskName+=("GYRO/ACCEL2");
                
                accelerometer=true;
                ;;

            g) #Gyroscope
                if [ ! -z $gyroscope ]; then
                    continue;
                fi

                masks+=(": IMU {");
                masks+=(": IMU2 {");
                maskName+=("GYRO/ACCEL");
                maskName+=("GYRO/ACCEL2");

                gyroscope=true;
                ;;

            j)
                if [ ! -z $injection ]; then
                    continue;
                fi

                masks+=(": INJT {");
                maskName+=("F_INJECTION");

                local injection=true;
                ;;
            
            h) #help message
                usage
                exit 1;
                ;;

            \?)
                echo "Invalid option: -$OPTARG. Try -h for help" >&2
                exit 1;
                ;;
            
            :)
                echo "Option -$OPTARG requires an argument." >&2
                exit 1
                ;;
        esac
    done

    if [ -z $filename ]; then
        printf "\033[1;31mThe filename is mandatory, try -h \033[0m\n"
        exit 1;
    fi

}

getSensorLogEntries(){
    IFS=','; #This is here so that the GREP on line 180 works properly
    for i in "${!masks[@]}"; do
        
        #Get Sensor Entries 
        while IFS=' {},' read -ra array; do
            stamp=$(echo "${maskName[i]},${array[0]} ${array[1]%?}");

            case "${array[2]}" in 
                "GPS")
                    data=$(echo "$stamp,${array[26]},${array[23]},${array[29]}");
                    writeToFile
                    ;;

                "IMU" | "IMU2") #ACE/GYRO
                    #Override stamp so that we can separate Gyro and Accel logs 
                    if [ ! -z $gyroscope ]; then
                        stamp=$(echo "GYRO,${array[0]} ${array[1]%?}");
                        data=$(echo "$stamp,${array[8]},${array[11]},${array[14]}");
                        writeToFile
                    fi
                    
                    if [ ! -z $accelerometer ];then
                        stamp=$(echo "ACCEL,${array[0]} ${array[1]%?}");
                        data=$(echo "$stamp,${array[17]},${array[20]},${array[23]}");
                        writeToFile
                    fi
                    ;;

                "BARO")
                    data=$(echo "$stamp,${array[8]},${array[11]},${array[14]},${array[26]}");
                    writeToFile
                    ;;

                "MAG" | "MAG2")
                    data=$(echo "$stamp,${array[8]},${array[11]},${array[15]}");
                    writeToFile
                    ;;

                "INJT")
                    data=$(echo "$stamp,${array[8]},${array[11]},${array[14]}");
                    writeToFile
                    ;;

                *)
                    printf "\033[1;45mLog format not valid\033[0m\n"
                    ;;
            esac
        done <<< $(grep "${masks[i]}" "$filename")
        
    done
}

main(){
    parseArguments "$@"
    getSensorLogEntries
}

main "$@"