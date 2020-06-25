#include <iostream>
#include <string>
#include <sstream>
#include <iomanip>
#include <cmath>

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
    string array[31];
    string lineInput;
    string delimiters(" ,{}:");
    size_t it;

    bool first = true;
    float init_x, init_y;
    float x = 0, y = 0;
    std::stringstream ss;

    cout.precision(2);

    cout << "#TIMESTAMP,INJ_X,INJ_Y,INJ_Z,POS_X,POS_Y,POS_Z,GYRO_X,GYRO_Y,GYRO_Z,MAG_X,MAG_Y,MAG_Z,ACC_X,ACC_Y,ACC_Z,BAR_X,BAR_Y,BAR_Z" << endl;
    while(getline(cin, lineInput)){

        splitFields(array, lineInput, delimiters, it);
        cout << array[0] << " " << array[1] << ":" << array[2] << ":" << array[3];

        if(first){
            ss.clear();
            ss.str(array[14]);
            ss >> init_x;

            ss.clear();
            ss.str(array[16]);
            ss >> init_y;

            array[14] = "0";
            array[16] = "0";

            first = false;
        } else {
            ss.clear();
            ss.str(array[14]);
            ss >> x;

            ss.clear();
            ss.str(array[16]);
            ss >> y;

            x = abs((x - init_x)*110000);
            y = abs((y - init_y)*110000);
        }

        cout << fixed << "," << array[8] << "," << array[10] << "," << array[12] << "," << x << "," << y;
        for(int i = 18; i < it; i+=2)
            cout << "," << array[i];

        //Second line
        getline(cin, lineInput);
        splitFields(array, lineInput, delimiters, it);
        for(int i = 8; i < it; i+=2)
            cout << "," << array[i];
        
        cout << endl;
    }

    return 0;
}