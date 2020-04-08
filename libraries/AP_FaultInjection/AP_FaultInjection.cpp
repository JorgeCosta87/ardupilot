#include <random>
#include <stdio.h>
#include <chrono>

#include <AP_HAL/AP_HAL.h>

#include "AP_FaultInjection.h"

extern AP_HAL::HAL& hal;

bool AP_FaultInjection::isEnableFaultInjection = false;
bool AP_FaultInjection::isRunningFaultInjection = false;

int8_t AP_FaultInjection::sensors = 0;
int8_t AP_FaultInjection::method = 0;
int8_t AP_FaultInjection::wp_trigger = 0;
bool AP_FaultInjection::onStart = false;
bool AP_FaultInjection::isArmed = false;
int8_t AP_FaultInjection::current_WP = 0;
uint32_t AP_FaultInjection::delay = 0;
uint32_t AP_FaultInjection::duration = 0;
uint64_t AP_FaultInjection::time_to_stop = 0;
int8_t AP_FaultInjection::wp_fault_triggered = -1;

float AP_FaultInjection::noise_mean = 0;
float AP_FaultInjection::noise_std = 0;
Vector3f AP_FaultInjection::static_rawField;
float AP_FaultInjection::min_value;
float AP_FaultInjection::max_value;

bool AP_FaultInjection::readLastValue = false;
Vector3f AP_FaultInjection::last_value;


AP_FaultInjection::AP_FaultInjection(void)
{
}

void AP_FaultInjection::incrementWaypoit()
{
    current_WP++;
    hal.console->printf("WAYPOINT: %d ", current_WP);
}

void AP_FaultInjection::resetWaypoitCount()
{
    current_WP = 0;
}

void AP_FaultInjection::checkState(AP_Int8 inj_enabled, bool armed)
{
    if(inj_enabled == 0)
    {
        isEnableFaultInjection = false;
    }
    else
    {
        isEnableFaultInjection = true;
    }

    isArmed = armed;
}

void AP_FaultInjection::loadValues(
    AP_Int8 inj_sensors, AP_Int8 inj_method,
    AP_Int32 inj_delay_to_start, AP_Int8  inj_wp_trigger,
    AP_Int32 inj_duration, AP_Float static_valueX,
    AP_Float static_valueY, AP_Float static_valueZ,
    AP_Float inj_noise_mean, AP_Float inj_noise_std,
    AP_Float inj_min_value, AP_Float inj_max_value)
{

    //load values
    sensors = inj_sensors;
    method = inj_method;

    wp_trigger = inj_wp_trigger;
    delay = inj_delay_to_start;
    duration = inj_duration;

    static_rawField.x = static_valueX;
    static_rawField.y = static_valueY;
    static_rawField.z = static_valueZ;
    noise_mean = inj_noise_mean;
    noise_std = inj_noise_std;
    min_value = inj_min_value;
    max_value = inj_max_value;

/*
    hal.console->printf("update:"
    "\n\t enabled: %d"
    "\n\t sensors: %d"
    "\n\t method: %d"
    "\n\t delay : %d"
    "\n\t duration : %d"
    "\n\t static_rawField x: %.2f - y: %.2f - z: %.2f"
    "\n\t noise_mean : %.2f"
    "\n\t noise_std : %.2f"
    "\n\t min_value : %.2f"
    "\n\t max_value : %.2f"
    "\n",
     isEnableFaultInjection, sensors, method,
     delay, duration, 
     static_rawField.x, static_rawField.y, static_rawField.z,
     noise_mean, noise_std, min_value, max_value
    );
*/
}

//TODO: This needs to be faster, basically use micros and leave the parsing for the python script
void AP_FaultInjection::log_fault_injection(const char * str){
    auto now = std::chrono::system_clock::now();
    auto nowMs = std::chrono::duration_cast<std::chrono::milliseconds>(now.time_since_epoch()) % 1000;

    time_t rawtime = std::chrono::system_clock::to_time_t(now);

    struct tm * timeinfo;
    char buffer [80];
    timeinfo = localtime (&rawtime);
    strftime (buffer, 80,"%Y-%m-%d %H:%M:%S",timeinfo);

    hal.console->printf("\n%s:%s.%d\n",str,buffer,(int) (nowMs.count() /10));
}

void AP_FaultInjection::update()
{
    if(isEnableFaultInjection)
    {   
        if(isRunningFaultInjection){
          
            if(AP_HAL::millis() > time_to_stop && duration != INFINITE)
            {
                stop_fault_injection();
                log_fault_injection("end_fault_injection");
            }
        }
        else{
            if(current_WP == wp_trigger && wp_fault_triggered != current_WP)
            {
                wp_fault_triggered = current_WP;
                start_fault_injection();
                log_fault_injection("start_fault_injection");
            }
        }
    }
}

void AP_FaultInjection::start_fault_injection(){

    if(!isEnableFaultInjection){
        return;
    }

    isRunningFaultInjection = true;
    readLastValue = false;
    last_value.zero();
    time_to_stop = AP_HAL::millis() + duration;
}

void AP_FaultInjection::stop_fault_injection(){
    
    isEnableFaultInjection = false;
    isRunningFaultInjection = false;
    readLastValue = false;
    last_value.zero();
}

void AP_FaultInjection::manipulate_values(Vector3f *rawField, uint8_t sens){

    //verify if the fault injector is enabled
    if(!isEnableFaultInjection){
       return;
    }

    if(!isRunningFaultInjection){
        return;
    }

    //check if it's the chosen sensor
    if(sens != sensors){
        return;
    }

    switch(method)
    {
        case INJECT_STATIC_VALUES : {
            rawField->x = static_rawField.x;
            rawField->y = static_rawField.y;
            rawField->z = static_rawField.z;
            break;
        }
        case INJECT_RANDOM_VALUES : {
            rawField->x = random_float(min_value, max_value);
            rawField->y = random_float(min_value, max_value);
            rawField->z = random_float(min_value, max_value);
            break;
        }
        case INJECT_NOISE : {
            gaussian_noise(rawField, noise_mean, noise_std);
            break;
        }
        case INJECT_REPEAT_LAST_KNOWN_VALUE : {
            if(!readLastValue){
                last_value.x = rawField->x;
                last_value.y = rawField->y;
                last_value.z = rawField->z;

                readLastValue = true;
            }
            rawField->x = last_value.x; 
            rawField->y = last_value.y;
            rawField->z = last_value.z;
            break;
        }
        case INJECT_DOUBLE : {
            rawField->x = rawField->x * 2.0;
            rawField->y = rawField->y * 2.0;
            rawField->z = rawField->z * 2.0;

            break;
        }
        case INJECT_HALF : {
            rawField->x = rawField->x / 2.0;
            rawField->y = rawField->y / 2.0;
            rawField->z = rawField->z / 2.0;
            break;
        }
        case INJECT_MAX_VALUE : {
            rawField->x = max_value;
            rawField->y = max_value;
            rawField->z = max_value;
            break;
        }
        case INJECT_DOUBLE_MAX : {
            rawField->x = max_value * 2.0;
            rawField->y = max_value * 2.0;
            rawField->z = max_value * 2.0;
            break;
        }
        case INJECT_MIN_VALUE : {
            rawField->x = min_value * 2.0;
            rawField->y = min_value * 2.0;
            rawField->z = min_value * 2.0;
            break;
        }
    }
}

void AP_FaultInjection::manipulate_single_Value(float *value, uint8_t sens){
    
        if(!isEnableFaultInjection){
           return;
        }
    
        if(sens != sensors){
            return;
        }

        if(AP_HAL::millis() >= time_to_stop){
            stop_fault_injection();
            return;
        }
    
        if(isRunningFaultInjection)
        {
            switch(method)
            {
                case INJECT_STATIC_VALUES : {
                    *value = static_rawField.x;
                    break;
                }

                case INJECT_RANDOM_VALUES : {
                    *value = random_float(min_value, max_value);
                    break;
                }

                case INJECT_NOISE : {
                    //gaussian_noise(rawField, noise_mean, noise_std);
                    break;
                }

                case INJECT_REPEAT_LAST_KNOWN_VALUE : {
                    if(!readLastValue){
                        last_value.x = *value;

                        readLastValue = true;
                    }
                    *value = last_value.x; 
                    break;
                }

                case INJECT_DOUBLE : {
                    *value = *value * 2.0f;
                    break;
                }

                case INJECT_HALF : {
                    *value = *value / 2.0f;
                    break;
                }

                case INJECT_MAX_VALUE : {
                    *value = max_value;
                    break;
                }
                
                case INJECT_DOUBLE_MAX : {
                    *value = max_value * 2.0f;
                    break;
                }
                case INJECT_MIN_VALUE : {
                    *value = min_value * 2.0f;
                    break;
                }
            }
        }
    }
    

//************************************UTILS******************************

float AP_FaultInjection::random_float(float min, float max){
    std::random_device rd;
    std::mt19937 gen(rd());
    std::uniform_real_distribution<> dist(min, max);

    return dist(gen);
} 

void AP_FaultInjection::gaussian_noise(Vector3f *rawField, float mean, float std){   
    std::random_device rd;
    std::mt19937 gen(rd());
    std::normal_distribution<float> dist(mean, std);

    rawField->x += dist(gen);
    rawField->y += dist(gen);
    rawField->z += dist(gen);
} 