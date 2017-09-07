#pragma once

#include <inttypes.h>

#include <stdio.h>

#include <AP_Compass/AP_Compass.h> 
#include <AP_Common/AP_Common.h>
#include <AP_HAL/AP_HAL.h>
#include <AP_Math/AP_Math.h>
#include <AP_Param/AP_Param.h>
#include <GCS_MAVLink/GCS_MAVLink.h>

 

//Methods
#define INJECT_STATIC_VALUES                    0
#define INJECT_RANDOM_VALUES                    1
#define INJECT_NOISE                            2
#define INJECT_REPEAT_LAST_KNOWN_VALUE          3

//type
#define INJECT_COMPASS                          0
#define INJECT_BARO                             1

#define SENSOR_COMPASS                          0
#define SENSOR_GYRO                             1
#define SENSOR_ACCEL                            2
#define SENSOR_BARO                             3

class Compass;

class AP_FaultInjection
{

public:

    AP_FaultInjection(void);
    AP_FaultInjection(Compass &_compass);

    void init(Compass *compass);
    void start_fault_injection();
    void stop_fault_injection();

    //compass
    void manipulate_compass_values(Vector3f *rawField);


    //Utils (move to another lib)
    float random_float(float min, float max);
    void gaussian_noise(Vector3f *rawField, float mean, float std);

    static const struct AP_Param::GroupInfo var_info[];

private:

    bool _isRunning_compass_faultIjection = false;
    Compass *_compass;

    uint64_t time_to_start;
    uint64_t time_to_stop;


    AP_Int8         _type;
    AP_Int8         _comp_method;


    //compass values
    AP_Vector3f    _comp_static_rawField;
    AP_Float       _comp_noise_mean;
    AP_Float       _comp_noise_std;
    AP_Vector3f    _comp_min_mag;
    AP_Vector3f    _comp_max_mag;

    bool           _comp_readLastValue = false;
    Vector3f       _comp_last_value;


    void set_compass(Compass  *compass) {_compass = compass;}
};