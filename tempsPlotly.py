#!/usr/bin/env python

'''
Program:      tempsPlotly.py
Author:       Jeff VanSickle
Created:      20160811
Modified:     20160811

Program creates visualization of temperature data using tempsDB.sqlite as
source. Visualization created using Plotly, cribbed from examples that were
themselves cribbed from examples.

https://plot.ly/python/line-charts/

UPDATES:
     yyyymmdd JV - Changed something, commenting here

INSTRUCTIONS:

'''

import sqlite3
import time
import datetime
import plotly as py
import plotly.graph_objs as go

# Function to create plot trace objects
def createPlotTrace(scatterXVal, scatterYVal, traceName):
    plotTrace = go.Scatter(
        x = scatterXVal,
        y = scatterYVal,
        name = traceName,
        line = dict(
            width = 4,
            ),
        )

    return plotTrace

# Chop leading zero off date elements
def cutLeadZero(inputStr):
    if int(inputStr) < 10:
        return inputStr[-1]
    else:
        return inputStr

# Function to format datestamps for Plotly
def castToDatetime(dateStr):
    year = dateStr[0:4]
    month = cutLeadZero(dateStr[4:6])
    day = cutLeadZero(dateStr[6:8])
    hours = cutLeadZero(dateStr[8:10])
    minutes = cutLeadZero(dateStr[10:12])
    seconds = cutLeadZero(dateStr[12:14])

    return datetime.datetime(int(year), int(month), int(day), int(hours),
            int(minutes), int(seconds))

# Connect to SQLite DB
try:
    tempsDB = sqlite3.connect('tempsDB.sqlite')
    tempsDB.text_factory = str
    cursor = tempsDB.cursor()
except:
    print 'Unable to open database. Please try again. Exiting....'
    quit()

# Lists to hold readings from each source
timestamps = []
DSAPI_reads = []
OWM_reads = []
W2_reads = []
WG_reads = []
DS18B20_reads = []
temps_means = []

# Get all data in DB
cursor.execute('SELECT * FROM Temps WHERE temps_mean < 150.00')

# Start building array data
for msg_row in cursor:
    timestamps.append(castToDatetime(msg_row[1]))
    DSAPI_reads.append(str(msg_row[2]))
    OWM_reads.append(str(msg_row[3]))
    W2_reads.append(str(msg_row[4]))
    WG_reads.append(str(msg_row[5]))
    DS18B20_reads.append(str(msg_row[6]))
    temps_means.append(str(msg_row[7]))

# Clean up DB connection
tempsDB.close()

# Scatter plot axis and title labels
graphTitle = 'Local and API Temperature Readings'
xAxisTitle = 'Timestamp'
yAxisTitle = 'Temperature (F)'

# Output filenames for scatterplot HTML files
graphOutFile = 'tempsOut_Plotly.html'

# Create traces for each reading
DSAPI_trace = createPlotTrace(timestamps, DSAPI_reads, 'Dark Sky API')
OWM_trace = createPlotTrace(timestamps, OWM_reads, 'OpenWeatherMap')
W2_trace = createPlotTrace(timestamps, W2_reads, 'Weather2')
WG_trace = createPlotTrace(timestamps, WG_reads, 'Wunderground')
DS18B20_trace = createPlotTrace(timestamps, DS18B20_reads, 'RasPi_DS18B20')
temps_means_trace = createPlotTrace(timestamps, temps_means, "Means")

# Set data for graph
tempsGraphData = [DSAPI_trace, OWM_trace, W2_trace, WG_trace, DS18B20_trace,
                  temps_means_trace]

# Define layout for graph
tempsGraphLayout = go.Layout(
        showlegend = True,
        title = graphTitle,
        xaxis = dict(title = xAxisTitle),
        yaxis = dict(title = yAxisTitle)
        )

# Generate graph
tempsGraphFig = go.Figure(data = tempsGraphData, layout = tempsGraphLayout)
py.offline.plot(tempsGraphFig, filename = graphOutFile)
