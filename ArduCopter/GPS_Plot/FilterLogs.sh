#!/bin/bash

printHelp(){
    printf "\n\033[1;40mUsage:\033[0;40m\n";
    printf "\033[40m$0 <filename.log> <optional: filetosave.log> \033[1;95;40m<optional:sensors>\033[0;40m\n\n";
    printf "\033[1;40mSensors:\033[0m\n"
    printf "\033[1;91;40mif no sensors are specified \033[1;95;40m(3rd argument)\033[1;91;40m, it will filter out every sensor\033[0;40m\n";
    printf "\033[1;40mIn order to specify multiple sensors, a \",\" must be used between the values. List of possible values:\n\033[0;40m";
    printf "\033[1;95;40mgyro - Gyroscope\nacce - Accelerometer\nbaro - Barometer\ncmps - Compass\nGPS - Global Positioning System\033[0;40m\n";
    printf "\n\033[1;40mExamples:\033[0m\n\033[1;32;40m$0 file.log savefile.txt \"baro,acce,gps\"\033[0;40m\n";
	printf "\033[1;32;40m$0 file.log savefile.txt\033[0m\n\n";
}

writeToFile(){
    if [ "$savefile" != "" ]; then
        echo "$data" >> $savefile;
    else
        echo "$data"
    fi
}

#Help and file check
if [ $# -lt 1 ] || [ $# -gt 3 ]; then
	printHelp;
    exit 1;
else
	filename=$1;
    if [ ! -f "$filename" ]; then
        echo "file \"$filename\" does not exist!";
        exit 1;
    fi 

	if [ $# -gt 1 ]; then
		savefile=$2;
        
        if [ -f "$savefile" ]; then
            echo "file \"$savefile\" already exists!";
            exit 1;
        fi

        if [ $savefile == "/dev/null" ]; then
            savefile="";
        fi

	fi
fi

#Check masks
IFS=','
read -ra params <<< "$3"
masks=()
maskName=()
for param in "${params[@]}"; do
    case "${param,,}" in
        "gps") #this is hard
            masks+=(": GPS {");
            maskName+=("GPS");
            ;;
            
        "baro") #Barometer
            masks+=(": BARO {");
            maskName+=("BAROMETER");
            ;;

        #"gyro") #Gyroscope
        "acce" | "gyro") #Accelerometer
            masks+=(": IMU {");
            masks+=(": IMU2 {");
            maskName+=("GYRO/ACCEL");
            maskName+=("GYRO/ACCEL2");
            ;;

        "cmps") #Compass
            masks+=(": MAG {");
            masks+=(": MAG2 {");
            maskName+=("COMPASS");
            maskName+=("COMPASS2");
            ;;
            
        *)
            printHelp
            exit 1;
    esac
done

IFS=","
#Remove duplicates with awk -- This is very hacky due to the format of the strings
masks=($(printf "%s,\n" "${masks[@]}" | awk '!a[$0]++')); 
maskName=($(printf "%s,\n" "${maskName[@]}" | awk '!a[$0]++'));

for x in ${!masks[@]}; do
    masks[$x]=$(echo "${masks[x]//[$'\t\r\n']}");
    maskName[$x]=$(echo "${maskName[x]//[$'\t\r\n']}");
done

for i in "${!masks[@]}"; do

    #Get Sensor Entries 
    while IFS=' ' read -ra array; do
        stamp=$(echo "${maskName[i]},${array[0]} ${array[1]}");

        case "${array[2]}" in 
            "GPS")
                data=$(echo "$stamp,${array[23]},${array[26]},${array[29]}");
                writeToFile
                ;;

            "IMU" | "IMU2") #ACE/GYRO
                #TODO: should I append them both in the same like?
                #Override stamp so that we can separate Gyro and Accel logs 
                stamp=$(echo "GYRO,${array[0]} ${array[1]}");
                data=$(echo "$stamp,${array[8]},${array[11]},${array[14]}");
                writeToFile

                stamp=$(echo "ACCEL,${array[0]} ${array[1]}");
                data=$(echo "$stamp,${array[17]},${array[20]},${array[23]}");
                writeToFile
                ;;

            #"BARO") TODO: what do I need from this?

            #   ;;

            #"MAG" | "MAG2")
            #    ;;

        esac
    done <<< $(grep "${masks[i]}" "$filename")
done