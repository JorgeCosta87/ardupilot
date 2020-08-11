
from enum import IntEnum

class Sensor(IntEnum):
    COMPASS         = 0
    GYROSCOPE       = 1
    ACCELEROMETER   = 2
    BAROMETER       = 3
    TEMPERATURE     = 4
    UNKNOWN         = 5
    NONE            = 6

class Method(IntEnum):
    STATIC          = 0
    RANDOM          = 1
    NOISE           = 2
    REPEAT_LAST     = 3
    DOUBLE_LAST     = 4
    HALF_LAST       = 5
    MAX_VALUE       = 6
    DOUBLE_MAX      = 7
    MIN_VALUE       = 8
    OFFSET          = 9
    SCALE_MULTIPLY  = 10
    SCALE_DIVIDE    = 11
    NONE            = 12

class State(IntEnum):
    NORMAL      = 0
    MINOR_FAULT = 1
    MAJOR_FAULT = 2
    CRASH       = 3
    STUCK       = 4
    LOST_PATH   = 5