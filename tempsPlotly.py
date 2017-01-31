#!/usr/bin/env python

'''
Program:      tempsPlotly.py
Author:       Jeff VanSickle
Created:      20160811
Modified:     20170130

Program creates visualization of temperature data using tempsDB.sqlite as
source. Visualization created using Plotly, cribbed from examples that were
themselves cribbed from examples.

https://plot.ly/python/line-charts/

UPDATES:
    20160820 JV - Replace append/prepend zeroes functions with calls to std.
                  library functions
                  Add buildDBQuery function to generate SQLite query based
                  on desired timeframe (day, week, month, current month)
                  Add argument passing for calls from CLI
    20170130 JV - Replace monotonous date parsing with datetime strftime()
                  Remove try/except and let argparse do its thing
                  Add parameter for input SQLite database, default output 
                  graph in /tmp
                  Add parameter for graph output directory, pass to 
                  buildDBQuery
                  Concatenate output path intelligently with os.path.join()

INSTRUCTIONS:
    - Replace instances of '<YOUR...>' with information for your system
    - Ensure you can access the location of your SQLite DB

TO DO:
    - Revisit PEP8. These conventions are inconsistent.

'''

import sqlite3
import time
import datetime
import calendar
import plotly as py
import plotly.graph_objs as go
import argparse

# Function to process leading zeroes
def trimLeadZero(strIn):
    if strIn >= '10':
        return strIn
    elif strIn == '00':
        return '0'
    else:
        return strIn.lstrip('0')

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

# Function to build time-based query to SQLite DB
def buildDBQuery(timeIn, baseOutDir):
    timeframe = timeIn.lower()
    baseQuery = 'SELECT * FROM Temps WHERE temps_mean < 150.00 '

    # Build time constraint for target values
    timeNow = datetime.datetime.now()
    todayStart = timeNow.strftime('%Y%m%d000000')
    todayEnd = timeNow.strftime('%Y%m%d235959')

    if timeframe == 'all':
        dbQuery = baseQuery
        outFName = os.path.join(baseOutDir, 'tempsPlotly_All.html')
    elif timeframe == 'daily':
        # Get all readings for current day
        tomLong = timeNow + datetime.timedelta(days = 1)
        tomShort = tomLong.strftime('%Y%m%d000000')
        dbQuery = baseQuery + 'AND rectime >= ' + todayStart + \
                  ' AND rectime < ' + tomShort
        outFName = os.path.join(baseOutDir, 'tempsPlotly_Day.html')
    elif timeframe == 'weekly':
        # Get all readings for last week up to end of current day
        lastWkLong = timeNow + datetime.timedelta(days = -7)
        lastWkShort = lastWkLong.strftime('%Y%m%d000000')
        dbQuery = baseQuery + 'AND rectime >= ' + lastWkShort + \
                  ' AND rectime <= ' + todayEnd
        outFName = os.path.join(baseOutDir, 'tempsPlotly_Week.html')
    elif timeframe == 'monthly':
        # Get all readings one month back (i.e., 08/20 back to 07/20), up to 
        # end of current day 
        lastMonLong = timeNow + datetime.timedelta(days = \
                      calendar.monthrange(timeNow.year, timeNow.month)[1] * -1)
        lastMonShort = lastMonLong.strftime('%Y%m%d000000')
        dbQuery = baseQuery + 'AND rectime >= ' + lastMonShort + \
                  ' AND rectime <= ' + todayEnd
        outFName = os.path.join(baseOutDir, 'tempsPlotly_Month.html')
    elif timeframe == 'currmonth':
        # Get all readings for current calendar month (i.e., August 2016)
        startOfMonth = timeNow.replace(day = 1)
        startMonStr = startOfMonth.strftime('%Y%m%d000000')
        endOfMonth = timeNow.replace(day = calendar.monthrange(timeNow.year, \
                     timeNow.month)[1])
        endMonStr = endOfMonth.strftime('%Y%m%d235959')
        dbQuery = baseQuery + 'AND rectime >= ' + startMonStr + \
                  ' AND rectime <= ' + endMonStr
        outFName = os.path.join('tempsPlotly_currMonth.html')

    return dbQuery, outFName

# Function to format datestamps for Plotly
def castToDatetime(dateStr):
    year = dateStr[0:4]
    month = trimLeadZero(str(dateStr[4:6]))
    day = trimLeadZero(str(dateStr[6:8]))
    hours = trimLeadZero(str(dateStr[8:10]))
    minutes = trimLeadZero(str(dateStr[10:12]))
    seconds = trimLeadZero(str(dateStr[12:14]))

    return datetime.datetime(int(year), int(month), int(day), int(hours),
            int(minutes), int(seconds))

# Get timeframe from CLI args
parser = argparse.ArgumentParser()
parser.add_argument('-t', '--timeframe', 
                    choices = ['daily', 'weekly', 'monthly', 'currmonth'], 
                    required = True,
                    help = 'Timeframe to graph (day, week, month, current month)')
parser.add_argument('-d' '--db',
                    required = True,
                    help = 'SQLite database where data is stored')
parser.add_argument('-o' '--out',
                    required = True,
                    help = 'Output directory for your generated graph(s)')

# Get arguments - time to parse, DB to use, output location for graphs
args = parser.parse_args()
timeToGraph = args.timeframe
db_loc = args.db
out_dir = args.out

# Test existence of specified locations
if not os.path.isfile(db_loc):
    print 'SQLite DB {} does not exist. Exiting....'.format(db_loc)
    quit()
elif not os.path.isdir(out_dir):
    print 'Path {} does not exist. Exiting....'.format(out_dir)
    quit()

# Connect to SQLite DB
try:
    tempsDB = sqlite3.connect(db_loc)
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

# Get data from DB
try:
    queryInput, graphOutFile = buildDBQuery(timeToGraph, out_dir)
    cursor.execute(queryInput)
except:
    queryInput = 'SELECT * FROM Temps WHERE temps_mean < 150.00'
    graphOutFile = '/tmp/plotly_all.html'     # <YOUR_DEFAULT_OUTPUT_FILE>
    cursor.execute(queryInput)

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

# Create traces for each reading
DSAPI_trace = createPlotTrace(timestamps, DSAPI_reads, 'Dark Sky API')
OWM_trace = createPlotTrace(timestamps, OWM_reads, 'OpenWeatherMap')
W2_trace = createPlotTrace(timestamps, W2_reads, 'Weather2')
WG_trace = createPlotTrace(timestamps, WG_reads, 'Wunderground')
DS18B20_trace = createPlotTrace(timestamps, DS18B20_reads, 'RasPi_DS18B20')
temps_means_trace = createPlotTrace(timestamps, temps_means, "Mean")

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
