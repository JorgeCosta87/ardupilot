#include <random>

#include <AP_HAL/AP_HAL.h>

#include "AP_FaultInjection.h"

extern AP_HAL::HAL& hal;

const AP_Param::GroupInfo AP_FaultInjection::var_info[] = {

    // @Param: INJ_TYPE
    // @DisplayName: Sensors to apply fault injection
    // @Description: Used to choose the sensors that will be applied the fault injection
    // @Values: 0:compass,1:barometer
    // @User: Advancedbbbb
    AP_GROUPINFO("TYPE", 1, AP_FaultInjection, _type, INJECT_COMPASS),    

    // @Param: INJ_METHOD
    // @DisplayName: Method to apply the fault injection
    // @Description: Fail injection allow differents ways to generate errors on the sensors, static values, noise over the sensor values, random values(min max) and repeat the last known value.
    // @Values: 0:static_values,1:random_values,2:noise,3:repeat_last_known_value
    // @Range: 0 1
    // @Increment: 1
    // @User: Advanced
    AP_GROUPINFO("METHOD", 2, AP_FaultInjection, _comp_method, INJECT_STATIC_VALUES),

//*************************************COMPASS PARAMS**************************

    // @Param: INJ_COMP_FIELD
    // @DisplayName: 
    // @Description:
    // @Values: Vector3f
    // @Range: 
    // @Increment: 
    // @User: Advanced
    AP_GROUPINFO("COMP_FIELD", 3, AP_FaultInjection, _comp_static_rawField, 0),
    
    // @Param: COMP_NOISE_U
    // @DisplayName: Mean
    // @Description:
    // @Values: Vector3f
    // @Range: 
    // @Increment: 
    // @User: Advanced
    AP_GROUPINFO("COMP_NOISE_M", 4, AP_FaultInjection, _comp_noise_mean, 0),

    // @Param: COMP_NOi_D
    // @DisplayName: standard deviation
    // @Description:
    // @Values: Vector3f
    // @Range: 
    // @Increment: 
    // @User: Advanced
    AP_GROUPINFO("COMP_NOiSE_D", 5, AP_FaultInjection, _comp_noise_std, 1),

    // @Param: INJ_COMP_MINX
    // @DisplayName: 
    // @Description:
    // @Values: Vector3f
    // @Range: 
    // @Increment: 
    // @User: Advanced
    AP_GROUPINFO("COMP_MIN", 6, AP_FaultInjection, _comp_min_mag, 0),
    
    // @Param: INJ_COMP_MAX
    // @DisplayName: 
    // @Description:
    // @Values: Vector3f
    // @Range: 
    // @Increment: 
    // @User: Advanced
    AP_GROUPINFO("COMP_MAX", 7, AP_FaultInjection, _comp_max_mag, 1000),
        
    
    AP_GROUPEND
};

AP_FaultInjection::AP_FaultInjection(void)
{
    AP_Param::setup_object_defaults(this, var_info);
    this->_compass = nullptr;
    _comp_last_value.zero();
}

void AP_FaultInjection::init(Compass *compass){
    set_compass(compass);

    for (uint8_t i=0; i< compass->get_backends_count(); i++) {
        compass->get_backends()[i]->set_faultInjection(this);
    }
}


void AP_FaultInjection::start_fault_injection(){

    if(_isRunning_compass_faultIjection){
        //time_to_start = g2.delay_to_start + AP_HAL::millis();
        return;
    }

 //   if(AP_HAL::millis() < time_to_start){
 //       return;
 //   }

    _comp_readLastValue = false;
    _comp_last_value.zero();

    switch(_type){
        
        case INJECT_COMPASS:
            _isRunning_compass_faultIjection = true;
            break;
            
        case INJECT_BARO:

            break;

    }
}

void AP_FaultInjection::stop_fault_injection(){
    
        _isRunning_compass_faultIjection = false;
        _comp_readLastValue = false;
        _comp_last_value.zero();
}

void AP_FaultInjection::manipulate_compass_values(Vector3f *rawField){


    if(!_isRunning_compass_faultIjection){
       return;
    }

    switch(_comp_method)
    {
        case INJECT_STATIC_VALUES : {
            const Vector3f aux = _comp_static_rawField.get();
            rawField->x = aux.x;
            rawField->y = aux.y;
            rawField->z = aux.z;
            break;
        }
        case INJECT_RANDOM_VALUES : {
            const Vector3f min = _comp_min_mag.get();
            const Vector3f max = _comp_max_mag.get();
            rawField->x = random_float(min.x, max.x);
            rawField->y = random_float(min.y, max.y);
            rawField->z = random_float(min.z, max.z);
            break;
        }
        case INJECT_NOISE : {
            gaussian_noise(rawField, _comp_noise_mean, _comp_noise_std);
            break;
        }
        case INJECT_REPEAT_LAST_KNOWN_VALUE : {
             if(!_comp_readLastValue){
                 _comp_last_value.x = rawField->x;
                 _comp_last_value.y = rawField->y;
                 _comp_last_value.z = rawField->z;

                 _comp_readLastValue = true;
             }
             rawField->x = _comp_last_value.x; 
             rawField->y = _comp_last_value.y;
             rawField->z = _comp_last_value.z;
            break;
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
