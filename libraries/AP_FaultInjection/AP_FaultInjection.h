#pragma once

#include <inttypes.h>

#include <AP_Compass/AP_Compass.h> 
#include <AP_Common/AP_Common.h>
#include <AP_HAL/AP_HAL.h>
#include <AP_Math/AP_Math.h>
#include <AP_Param/AP_Param.h>
#include <GCS_MAVLink/GCS_MAVLink.h>


#define INFINITE                                0

//Methods
#define INJECT_STATIC_VALUES                    0
#define INJECT_RANDOM_VALUES                    1
#define INJECT_NOISE                            2
#define INJECT_REPEAT_LAST_KNOWN_VALUE          3
#define INJECT_DOUBLE                           4
#define INJECT_HALF                             5
#define INJECT_MAX_VALUE                        6
#define INJECT_DOUBLE_MAX                       7
#define INJECT_MIN_VALUE                        8

//sensors
#define SENSOR_COMPASS                          0
#define SENSOR_GYRO                             1
#define SENSOR_ACCEL                            2
#define SENSOR_BARO                             3
#define SENSOR_TEMP                             4

class AP_FaultInjection
{

public:

    AP_FaultInjection(void);

    static void start_fault_injection();
    static void stop_fault_injection();
    static void loadValues(
        AP_Int8 inj_sensors, AP_Int8 inj_method,
        AP_Int32 inj_delay_to_start, AP_Int8  inj_wp_trigger,
        AP_Int32 inj_duration, AP_Float static_valueX,
        AP_Float static_valueY, AP_Float static_valueZ,
        AP_Float inj_noise_mean, AP_Float inj_noise_std,
        AP_Float inj_min_value, AP_Float inj_max_value);

    static void incrementWaypoit();
    static void resetWaypoitCount();
    static void checkState(AP_Int8 inj_enabled, bool armed);
    static void update();

    static void manipulate_values(Vector3f *rawField, uint8_t sens);
    static void manipulate_single_Value(float *value, uint8_t sens);


    static float random_float(float min, float max);
    static void gaussian_noise(Vector3f *rawField, float mean, float std);

    static bool isEnableFaultInjection;
    static bool isRunningFaultInjection;

    static const struct AP_Param::GroupInfo var_info[];
    static bool     readLastValue;
    static Vector3f last_value;

    static bool isArmed;
    static bool onStart;
    static int8_t countWP;
    static int8_t wp_trigger;
    static uint32_t delay;
    static uint32_t duration;
    static uint64_t time_to_start;
    static uint64_t time_to_stop;

    static int8_t         sensors;
    static int8_t         method;

    static Vector3f static_rawField;
    static float    noise_mean;
    static float    noise_std;
    static float    max_value;
    static float    min_value;

};