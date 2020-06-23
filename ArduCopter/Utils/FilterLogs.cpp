#include <iostream>
#include <string>

using namespace std;

int main(int argc, char ** argv){
    string lineInput;
    string delimiters(" ,{}:");
    string array[33];

    cout << "#TIMESTAMP;INJ_X;INJ_Y;INJ_Z;POS_X;POS_Y;POS_Z;GYRO_X;GYRO_Y;GYRO_Z;SPEED;MAG_X;MAG_Y;MAG_Z" << endl;
    while(getline(cin, lineInput)){
        size_t beginning, it = 0 ,pos = 0;

        while((beginning = lineInput.find_first_not_of(delimiters, pos)) != string::npos)
        {
            pos = lineInput.find_first_of(delimiters, beginning + 1);
            array[it++] = lineInput.substr(beginning, pos - beginning);
            //cout << lineInput.substr(beginning, pos - beginning) << endl;
        }

        cout << array[0] << " " << array[1] << ":" << array[2] << ":" << array[3];
        for(int i = 8; i < it; i+=2)
            cout << "," << array[i];
        
        cout << endl;
    }

    return 0;
}