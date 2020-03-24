#!/bin/bash

if [ $# -lt 1 ]; then
	printf "Usage: $0 <filename.log> <optional: filetosave.log> \n";
	exit 1;
else
	filename=$1;

	if [ $# -gt 1 ]; then
		savefile=$2;
	fi
fi

#Create a simple temp with GPS entries only
stamp=$(date +"%m%d%Y%H%M");
tempFile=$(printf "/tmp/temp%s.txt" "$stamp");


grep ": GPS {" "$filename" >> "$tempFile"

#grep ": GPS {" "$filename" | uniq -u >> "$tempFile" # removes repeated entries
#printf "#\033[0;45mLatitude,Longitude,Altitude\033[0m\n";

#Get GPS data from each entry 
while IFS=',' read -ra array; do
	time=$(echo "${array[0]}" | cut -d ":" -f1,2,3);
	lat=$(echo "${array[6]}" | cut -d ":" -f2);
	lng=$(echo "${array[7]}" | cut -d ":" -f2);
	alt=$(echo "${array[8]}" | cut -d ":" -f2);

	if [ "$savefile" != "" ]; then
		echo "GPS,$time,$lng,$lat,$alt" >> $savefile;
	else
		echo "GPS,$time,$lng,$lat,$alt"
	fi
	
done < $tempFile

rm -f $tempFile