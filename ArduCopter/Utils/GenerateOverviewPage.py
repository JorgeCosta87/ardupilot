#!/usr/bin/env python

# chart imports
import json # used to convert dictornaries to json

# OS tools
import os.path
import sys

# Enum
from enum import IntEnum
from PointValidation import State
from Enumerators import Sensor, Method

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
        

class Filter(IntEnum):
    ID          = 0
    REPETITION  = 1
    INJECTION   = 2
    MISSION     = 3
    RADIUS      = 4
    SENSOR      = 5
    METHOD      = 6
    DELAY       = 7
    DURATION    = 8
    TRIGGER     = 9
    X           = 10
    Y           = 11
    Z           = 12
    MIN         = 13
    MAX         = 14
    NOISE_D     = 15
    NOISE_M     = 16
    RESULT      = 17


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
        
        data = {}

        data[Filter.ID]         = int(split[Filter.ID])
        data[Filter.REPETITION] = int(split[Filter.REPETITION])
        data[Filter.INJECTION]  = split[Filter.INJECTION].lower == "true"
        data[Filter.MISSION]    = split[Filter.MISSION]
        data[Filter.RADIUS]     = split[Filter.RADIUS]
        data[Filter.SENSOR]     = Sensor[split[Filter.SENSOR]].name
        data[Filter.METHOD]     = Method[split[Filter.METHOD]].name
        data[Filter.DELAY]      = int(split[Filter.DELAY])
        data[Filter.DURATION]   = int(split[Filter.DURATION])
        data[Filter.TRIGGER]    = int(split[Filter.TRIGGER])
        data[Filter.X]          = float(split[Filter.X])
        data[Filter.Y]          = float(split[Filter.Y])
        data[Filter.Z]          = float(split[Filter.Z])
        data[Filter.MIN]        = int(split[Filter.MIN])
        data[Filter.MAX]        = int(split[Filter.MAX])
        data[Filter.NOISE_D]    = float(split[Filter.NOISE_D])
        data[Filter.NOISE_M]    = float(split[Filter.NOISE_M])
        data[Filter.RESULT]     = State[split[Filter.RESULT].rstrip('\n')]

        results.append(data)

    return results


# Get data by sensor type
def get_existing(array, val):
    for value in array:
        if value.header == val:
            return True, value
    
    temp = namedtuple("value", "header normal minor major crash")
    temp.header = val
    temp.normal = 0
    temp.minor  = 0
    temp.major  = 0
    temp.crash  = 0

    return False, temp


def prepare_JSON_data(results):
    dataArray = []
    for key in results.keys():
        dataArray.append(results[key])
    
    return json.dumps({ "dataProvider": dataArray })[1:-1] # Removes { } from the begining and end


def organize_data(field,data):
    values = []

    for block in data:
        exists, value = get_existing(values, block[field])
        result = block[Filter.RESULT]

        if result == State.NORMAL:
            value.normal += 1

        elif result == State.MINOR_FAULT:
            value.minor += 1

        elif result == State.MAJOR_FAULT:
            value.major += 1

        else:
            value.crash += 1

        if not exists:
            values.append(value)

    # Creates dictionary with data to plot
    results = {}
    for stat in values:
        results[stat.header] = {   
            "Mission"     : stat.header,
            "Normal"      : stat.normal,
            "Minor Fault" : stat.minor,
            "Major Fault" : stat.major,
            "Crash"       : stat.crash
        }
    
    return prepare_JSON_data(results)


def GenerateChartPage(filename):
    # read data from results file
    dataset = read_results(filename)

    # Get parent directory of results file, so that the charts can be stored next to it
    path = os.path.abspath(os.path.join(filename,os.path.pardir))

    # Filter Data
    mission_results = organize_data(Filter.MISSION, dataset)
    sensor_results  = organize_data(Filter.SENSOR, dataset)
    method_results  = organize_data(Filter.METHOD, dataset)
    delay_results   = organize_data(Filter.DELAY, dataset)
    duration_results = organize_data(Filter.DURATION, dataset)
    noiseD_results = organize_data(Filter.NOISE_D, dataset)
    noiseM_results = organize_data(Filter.NOISE_M, dataset)
    

    # Generate HTML
    chart = ChartHandler()
    chart.AddChart("Missions Overview", mission_results)
    chart.AddChart("Sensors Overview", sensor_results)
    chart.AddChart("Methods Overview", method_results)
    chart.AddChart("Delays Overview", delay_results)
    chart.AddChart("Durations Overview", duration_results)
    chart.AddChart("Noise Deviation Overview", noiseD_results)
    chart.AddChart("Noise Mean Overview", noiseM_results)
    
    print chart.GetPage()

GenerateChartPage(sys.argv[1])
