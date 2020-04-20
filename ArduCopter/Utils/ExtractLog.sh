#!/bin/bash

usage(){
    printf "\033[40mUsage: $0 -f filename -f filename2 -s savefile\n\n"
    printf "\033[1m-f \033[21mis used to specify a log file to c-onvert\n\n"
    printf "\033[1m-s \033[21mis used to override the path and filenames in order.\n\n"
    printf "\033[1mExamples:\033[21m"
    printf "$0 -f file.bin -f file2.bin -s save\n"
    printf "Output files: save, file2.log\n\n"
    printf "$0 -f file.bin -s save -f file2.bin\n"
    printf "Output files: save, file2.log\n\n\033[0m"
}

argumentParsing(){
    #if no arguments are supplied
    if [ $# == 0 ]; then
        usage
        exit 1;
    fi

    files=();
    savefiles=();
    while getopts ":hf:s:" opt; do
        case $opt in
            f) #adding more files to parse
                #check if file exists
                if [ ! -f "$OPTARG" ]; then
                    echo "File $OPTARG does not exist!";
                    exit 1;
                fi

                files+=("$OPTARG");
                ;;

            s) #this is the log save file 
                if [ -f "$OPTARG" ]; then
                    echo "A file with the name $OPTARG already exist!";
                    exit 1;
                fi

                if [ $OPTARG == "" ]; then
                    echo "Save file name cannot be \"$OPTARG\"."
                    exit 1;
                fi
                
                savefiles+=("$OPTARG");
                ;;

            h) #help message
                usage
                exit 1;
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
}

extractLogs(){
    for ((i=0; i < ${#files[@]}; i++)); do

        if [ -z "${savefiles[i]}" ]; then
            if [[ ! ${files[i],,} == *".bin" ]]; then #if the name does not have a .bin
                outFilename="${files[i]}.log"
            else
                outFilename=$(printf "${files[i]/%.*/.log}")
            fi
        else
            outFilename="${savefiles[i]}"
        fi

        mavlogdump.py --planner --format='csv'--csv_sep='tab' "${files[i]}" > "$outFilename"
    done 
}

main(){
    argumentParsing "$@"
    extractLogs
}

main "$@";