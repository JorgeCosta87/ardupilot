#include <iostream>
#include <string>

using namespace std;

int main(int argc, char ** argv){
    string lineInput;
    string delimiters(" ,{}:");
    string array[14];

    //cout << "#LOG_TYPE,TIMESTAMP,X,Y,Z"
    while(getline(cin, lineInput)){
        size_t beginning, it = 0 ,pos = 0;

        while((beginning = lineInput.find_first_not_of(delimiters, pos)) != string::npos)
        {
            pos = lineInput.find_first_of(delimiters, beginning + 1);
            array[it++] = lineInput.substr(beginning, pos - beginning);
        }

        cout << "F_INJECTION," << array[0] << " " << array[1] << ":" << array[2] << ":" << array[3] << "," << array[8] << array[10] << array[12] << endl;
    }

    return 0;
}