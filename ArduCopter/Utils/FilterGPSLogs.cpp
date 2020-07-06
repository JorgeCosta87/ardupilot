#include <iostream>
#include <string>
#include <sstream>
#include <iomanip>
#include <stdint.h>

using namespace std;

void splitFields(string * array, string &lineInput, const string &delimiters, size_t &it){
    it = 0;

    //First line
    for(size_t beginning = 0, pos = 0; (beginning = lineInput.find_first_not_of(delimiters, pos)) != string::npos;)
    {
        pos = lineInput.find_first_of(delimiters, beginning + 1);
        array[it++] = lineInput.substr(beginning, pos - beginning);
        //cout << it-1 << ": " << array[it-1] << endl;
    }
}

int main(int argc, char ** argv){
    string array[33];
    string lineInput;
    string delimiters(" ,{}:");
    size_t it;


    while(getline(cin, lineInput)){

        splitFields(array, lineInput, delimiters, it);
        cout << "GPS," << array[0] << " " << array[1] << ":" << array[2] << ":" << array[3] << ","; //Timestamp
        cout << array[20] << "," << array[18] << "," << array[22] << endl;
    }

    return 0;
}