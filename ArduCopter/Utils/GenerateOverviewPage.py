#!/usr/bin/env python

# chart imports
import json # used to convert dictornaries to json

# OS tools
import os.path
import sys

# Enum
from enum import IntEnum
from PointValidation import State

# Data collections
from collections import namedtuple

class ChartHandler:
    def __init__(self):
        self.charts = []

    _header="""
    <!DOCTYPE html>
    <html>
        <head>
            <title>Tests Overview</title>

            <script type="text/javascript" src="https://www.amcharts.com/lib/3/amcharts.js"></script>
            <script type="text/javascript" src="https://www.amcharts.com/lib/3/serial.js"></script>

            <script type="text/javascript">
    """

    _bodyTop="""
            </script>
        </head>
        <body>
    """

    _bodyBottom="""
            </body>
        </html>
    """

    def _generateScript(self, title, data, divname):
        return """
        AmCharts.makeChart(\""""+divname+"""\",
        {
            "type": "serial",
            "categoryField": "Mission",
            "startDuration": 1,
            "theme": "default",
            "categoryAxis": {
                "gridPosition": "start"
            },
            "trendLines": [],
            "graphs": [
                {
                    "accessibleLabel": "[[title]] [[Mission]] [[value]]",
                    "balloonText": "[[title]] of [[Mission]]:[[value]]",
                    "fillAlphas": 1,
                    "fillColors": "#B0DE09",
                    "fontSize": 11,
                    "id": "Normal",
                    "labelText": "[[value]]",
                    "lineColor": "#B0DE09",
                    "title": "Normal",
                    "type": "column",
                    "valueField": "Normal"
                },
                {
                    "accessibleLabel": "[[title]] [[Mission]] [[value]]",
                    "balloonText": "[[title]] of [[category]]:[[value]]",
                    "fillAlphas": 1,
                    "fillColors": "#FFFF00",
                    "id": "Minor Fault",
                    "labelText": "[[value]]",
                    "lineColor": "#FFFF00",
                    "title": "Minor Fault",
                    "type": "column",
                    "valueField": "Minor Fault"
                },
                {
                    "accessibleLabel": "[[title]] [[Mission]] [[value]]",
                    "balloonText": "[[title]] of [[Mission]]:[[value]]",
                    "fillAlphas": 1,
                    "fillColors": "#FFA600",
                    "id": "Major Fault",
                    "labelText": "[[value]]",
                    "lineColor": "#FFA600",
                    "title": "Major Fault",
                    "type": "column",
                    "valueField": "Major Fault"
                },
                {
                    "accessibleLabel": "[[title]] [[Mission]] [[value]]",
                    "balloonText": "[[title]] of [[Mission]]:[[value]]",
                    "fillAlphas": 1,
                    "fillColors": "#e36464",
                    "id": "Crash",
                    "labelText": "[[value]]",
                    "lineColor": "#e36464",
                    "title": "Crash",
                    "type": "column",
                    "valueField": "Crash"
                }
            ],
            "guides": [],
            "valueAxes": [
                {
                    "id": "ValueAxis-1",
                    "stackType": "regular",
                    "title": "Tests"
                }
            ],
            "allLabels": [],
            "balloon": {},
            "legend": {
                "enabled": true,
                "useGraphSettings": true
            },
            "titles": [
                {
                    "id": "Title",
                    "size": 15,
                    "text": \""""+title+"""\"
                }
            ],"""+data+"""    
        });"""

    def AddChart(self, title, data):
        self.charts.append([ title, data ])

    def GetPage(self):
        divname = "chartdiv"

        # define html header
        page = self._header

        # add chart scripts
        for i, chart in enumerate(self.charts):
            page += self._generateScript(chart[0], chart[1],divname+str(i))
        
        # add body and div components
        page += self._bodyTop
        for i, chart in enumerate(self.charts):
            page += """<div id=\""""+divname+str(i)+"""\" style="width: 100%; height: 400px; background-color: #FFFFFF;" ></div>"""
        page += self._bodyBottom

        return page

class Sensor(IntEnum):
    COMPASS         = 0
    GYROSCOPE       = 1
    ACCELEROMETER   = 2
    BAROMETER       = 3
    TEMPERATURE     = 4
    UNKNOWN         = 5
    NONE            = 6


# Convert result file to data
def read_results(filename):
    #check file existence
    if not os.path.isfile(filename):
        raise Exception("File " + filename + " does not exist!")
    
    file = open(filename, "rt");
    file.readline()

    results = []
    for line in file:
        split = line.split(",")
        
        #structure to store each entry
        data = namedtuple("run", "id repetition mission_name injection_enabled sensor result")

        data.id                 = int(split[0])
        data.repetition         = int(split[1])
        data.mission_name       = split[2]
        data.injection_enabled  = split[3].lower == "true"
        data.sensor             = Sensor[split[4]]
        data.result             = State[split[5].rstrip('\n')]

        results.append(data)

    return results   


# Get data by mission file
def get_existing_mission_data(missions, name):
    for mission in missions:
        if mission.name == name:
            return True, mission
    
    temp = namedtuple("mission", "name normal minor major crash")
    temp.name   = name
    temp.normal = 0
    temp.minor  = 0
    temp.major  = 0
    temp.crash  = 0

    return False, temp

def organize_data_by_mission(data):
    missions = []

    for block in data:
        exists, mission = get_existing_mission_data(missions, block.mission_name)

        if block.result == State.NORMAL:
            mission.normal += 1

        elif block.result == State.MINOR_FAULT:
            mission.minor += 1

        elif block.result == State.MAJOR_FAULT:
            mission.major += 1

        else:
            mission.crash += 1
    
        if not exists:
            missions.append(mission)

    # Creates dictionary with data to plot
    results = {}
    for mission in missions:    
        results[mission.name] = {   
            "Mission"    : mission.name,
            "Normal"      : mission.normal,
            "Minor Fault" : mission.minor,
            "Major Fault" : mission.major,
            "Crash"       : mission.crash
        }

    return results


# Get data by sensor type
def get_existing_sensor_data(sensors, sensorType):
    for sensor in sensors:
        if sensor.type == sensorType:
            return True, sensor
    
    temp = namedtuple("sensor", "type normal minor major crash")
    temp.type   = sensorType
    temp.normal = 0
    temp.minor  = 0
    temp.major  = 0
    temp.crash  = 0

    return False, temp

def organize_data_by_sensor(data):
    sensors = []

    for block in data:
        exists, sensor = get_existing_sensor_data(sensors, block.sensor)

        if block.result == State.NORMAL:
            sensor.normal += 1

        elif block.result == State.MINOR_FAULT:
            sensor.minor += 1

        elif block.result == State.MAJOR_FAULT:
            sensor.major += 1

        else:
            sensor.crash += 1
    
        if not exists:
            sensors.append(sensor)

    # Creates dictionary with data to plot
    results = {}
    for sensor in sensors:
        results[sensor.type.name] = {   
            "Mission"    : sensor.type.name,
            "Normal"      : sensor.normal,
            "Minor Fault" : sensor.minor,
            "Major Fault" : sensor.major,
            "Crash"       : sensor.crash
        }

    return results

def prepare_JSON_data(results):
    dataArray = []
    for key in results.keys():
        dataArray.append(results[key])
    
    return json.dumps({ "dataProvider": dataArray })[1:-1] # Removes { } from the begining and end

def GenerateChartPage(filename):
    # read data from results file
    dataset = read_results(filename)
    
    # Get parent directory of results file, so that the charts can be stored next to it
    path = os.path.abspath(os.path.join(filename,os.path.pardir))

    mission_results = organize_data_by_mission(dataset)
    sensor_results  = organize_data_by_sensor(dataset)
    
    #print chart_data_provider
    chart = ChartHandler()
    chart.AddChart("Mission Overview", prepare_JSON_data(mission_results))
    chart.AddChart("Sensor Overview", prepare_JSON_data(sensor_results))
    print chart.GetPage()

GenerateChartPage(sys.argv[1])