#include <iostream>
#include <string>
#include <sstream>
#include <iomanip>
#include <stdint.h>

#define ERROR_RESOLVED "Errors Resolved"
#define FAILSAFE_TRIGGERED "Failsafe Triggered"
#define FAILSAFE_RESOLVED "Failsafe Resolved"

using namespace std;

string errors[30];

enum subsystem {
    RADIO_CHECK         = 2,
    COMPASS_CHECK       = 3,
    RADIO_FAILSAFE      = 5,
    BATTERY_FAILSAFE    = 6,
    GCS_FAILSAFE        = 8,
    FENCE_FAILSAFE      = 9,
    FLIGHTMODE_FAILURE  = 10,
    GPS_CHECK           = 11,
    CRASH_CHECK         = 12,
    FLIP_CHECK          = 13,
    PARACHUTE           = 15,
    EKF_CHECK           = 16,
    EKF_FAILSAFE        = 17,
    BAROMETER           = 18,
    CPU_LOAD            = 19,
    ADSB_FAILSAFE       = 20,
    TERRAIN_DATA        = 21,
    NAVIGATION          = 22,
    TERRAIN_FAILSAFE    = 23,
    EKF_PRIMARY_CHANGED = 24,
    THRUST_LOSS_CHECK   = 25,
    VIBRATION_FAILSAFE  = 29,
};

string * initEnumIdentifiers(){
    errors[2]            = "RADIO_CHECK";
    errors[3]            = "COMPASS_CHECK"; 
    errors[5]            = "RADIO_FAILSAFE"; 
    errors[6]            = "BATTERY_FAILSAFE"; 
    errors[8]            = "GCS_FAILSAFE"; 
    errors[9]            = "FENCE_FAILSAFE"; 
    errors[10]           = "FLIGHTMODE_FAILURE"; 
    errors[11]           = "GPS_CHECK"; 
    errors[12]           = "CRASH_CHECK"; 
    errors[13]           = "FLIP_CHECK";
    errors[15]           = "PARACHUTE";
    errors[16]           = "EKF_CHECK";
    errors[17]           = "EKF_FAILSAFE";
    errors[18]           = "BAROMETER";
    errors[19]           = "CPU_LOAD";
    errors[20]           = "ADSB_FAILSAFE"; 
    errors[21]           = "TERRAIN_DATA";
    errors[22]           = "NAVIGATION";
    errors[23]           = "TERRAIN_FAILSAFE";
    errors[24]           = "EKF_PRIMARY_CHANGED";
    errors[25]           = "THRUST_LOSS_CHECK";
    errors[29]           = "VIBRATION_FAILSAFE";
}

string getErrorDescription(uint16_t subsystem, uint16_t error){
    switch(subsystem){
        case EKF_CHECK:
            if(error == 0)
                return "Variance cleared (position estimate OK)";
            else if(error == 2)
                return "Bad Variance (position estimate bad)";
            break;

        case EKF_FAILSAFE:
            if(error == 0)
                return FAILSAFE_RESOLVED;
            else if(error == 1)
                return FAILSAFE_TRIGGERED;
            break;

        case EKF_PRIMARY_CHANGED:
            if(error == 0)
                return "1st EKF has become primary";
            else if(error == 1)
                return "2st EKF has become primary";
            break;

        case GPS_CHECK:
            if(error == 0)
                return "Glitch cleared";
            else if(error == 2)
                return "GPS Glitch occurred";
            break;

        case RADIO_CHECK:
            if(error == 0)
                return ERROR_RESOLVED;
            else if(error == 2)
                return "Late Frame : no updates received from receiver for two seconds";
            break;

        case RADIO_FAILSAFE:
            if(error == 0)
                return FAILSAFE_RESOLVED;
            else if(error == 2)
                return FAILSAFE_RESOLVED;
            break;

        case COMPASS_CHECK:
            if(error == 0)
                return ERROR_RESOLVED;
            else if(error == 1)
                return "Failed to initialise (probably a hardware issue)";
            else if(error == 4)
                return "Unhealthy : failed to read from the sensor";
            break;

        case BAROMETER:
            if(error == 0)
                return ERROR_RESOLVED;
            else if(error == 4)
                return "Unhealthy : failed to read from the sensor";
            break;
        
        case CRASH_CHECK:
            if(error == 1)
                return "Crash into ground detected. Normally vehicle is disarmed soon after";
            else if(error == 2)
                return "Loss of control detected. Normally parachute is released soon after";
            break;
        
        case BATTERY_FAILSAFE:
            if(error == 0)
                return FAILSAFE_RESOLVED;
            else if(error == 1)
                return FAILSAFE_TRIGGERED;
            break;
        
        case GCS_FAILSAFE:
            if(error == 0)
                return FAILSAFE_RESOLVED;
            else if(error == 1)
                return FAILSAFE_TRIGGERED;
            break;
        
        case FENCE_FAILSAFE:
            if(error == 0)
                return FAILSAFE_RESOLVED;
            else if(error == 1)
                return "Altitude fence breach, Failsafe Triggered";
            else if(error == 2)
                return "Circular fence breach, Failsafe Triggered";
            else if(error == 3)
                return "Both Alt and Circular fence breached, Failsafe Triggered";
            else if(error == 4)
                return "Polygon fence breached, Failsafe Triggered";
            break;

        case FLIGHTMODE_FAILURE:
            return "Vehicle was unable to enter the desired flight mode normally because of a bad position estimate";
        
        case FLIP_CHECK:
            return "Flip abandoned (not armed, pilot input or timeout)";

        case PARACHUTE:
            if(error == 2)
                return "Not Deployed, vehicle too low";
            else if(error == 3)
                return "Not Deployed, vehicle landed";
            break;

        case CPU_LOAD:
            if(error == 0)
                return FAILSAFE_RESOLVED;
            else if(error == 1)
                return "Failsafe Triggered (normally vehicle disarms)";
            break;

        case ADSB_FAILSAFE:
            if(error == 0)
                return FAILSAFE_RESOLVED;
            else if(error == 1)
                return "No action just report to Pilot";
            else if(error == 2)
                return "Vehicle avoids by climbing or descending";
            else if(error == 3)
                return "Vehicle avoids by moving horizontally";
            else if(error == 4)
                return "Vehicle avoids by moving perpendicular to other vehicle";
            else if(error == 5)
                return "RTL invoked";
            break;

        case TERRAIN_DATA:
            return "missing terrain data";
            break;

        case TERRAIN_FAILSAFE:
            if(error == 0)
                return FAILSAFE_RESOLVED;
            else if(error == 1)
                return "Failsafe Triggered (normally vehicle RTLs)";
            break;

        case NAVIGATION:
            if(error == 2)
                return "Failed to set destination";
            else if(error == 3)
                return "RTL restarted";
            else if(error == 4)
                return "Circle initialisation failed";
            else if(error == 5)
                return "Destination outside fence";
            break;

        case THRUST_LOSS_CHECK:
            if(error == 0)
                return "Thrust Restored";
            else if(error == 1)
                return "Thrust Loss Detected (altitude may be prioritised over yaw control)";
            break;

        case VIBRATION_FAILSAFE:
            if(error == 0)
                return "Excessive Vibration Compensation De-activated";
            else if(error == 1)
                return "Excessive Vibration Compenstaion Activated";
            break;
    }

    return "UNKNOWN";
}

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
    uint16_t subsystem = 0, error = 0;
    string error_msg;

    std::stringstream ss;

    initEnumIdentifiers();

    cout.precision(2);
    cout << "#TIMESTAMP,ERROR,ERROR_DESC,INJ_X,INJ_Y,INJ_Z,POS_X,POS_Y,POS_Z,GYRO_X,GYRO_Y,GYRO_Z,MAG_X,MAG_Y,MAG_Z,ACC_X,ACC_Y,ACC_Z,BAR_X,BAR_Y,BAR_Z,CUR_COMPASS,CUR_ACCEL,CUR_GPS,CUR_BARO,CUR_GYRO" << endl;
    while(getline(cin, lineInput)){

        splitFields(array, lineInput, delimiters, it);
        cout << array[0] << " " << array[1] << ":" << array[2] << ":" << array[3]; //Timestamp
        
        if(array[4][0] == 'E'){ //if it starts with E it means it's ERR message
            ss.clear();
            ss.str(array[8]);
            ss >> subsystem;

            ss.clear();
            ss.str(array[10]);
            ss >> error;

            error_msg = getErrorDescription(subsystem, error);

            cout << "," << errors[subsystem] << "," << error_msg << endl;
            continue;
        }

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

            x = (x - init_x)*110000;
            y = (y - init_y)*110000;
        }
        cout << ",,";
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