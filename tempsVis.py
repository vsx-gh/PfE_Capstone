#!/usr/bin/env python

'''
Program:      tempsVis.py
Author:       Jeff VanSickle
Created:      20160508
Modified:     20160510

Program creates visualization of temperature data using tempsDB.sqlite as
source. Visualization created using D3.js, cribbed from examples that were
themselves cribbed from examples. Credits belong to D3.js site and Chuck
Severance.

UPDATES:
    20160510 JV - Remove data specific to my location and filesystem

INSTRUCTIONS:
    - Replace '<YOUR_SQLITE_DB>' with the location of your SQLite DB where all
    of your readings reside.
    - After running this code, you will have a flat file, data.tsv, that will
    serve as source for your D3 Javascript page. Open d3Vis.html after you run
    this code to see your D3 visualization.
'''

import sqlite3
import time

# Connect to SQLite DB
tempsDB = sqlite3.connect('<YOUR_SQLITE_DB>')
tempsDB.text_factory = str
cursor = tempsDB.cursor()

# Get all data in DB
cursor.execute('SELECT * FROM Temps WHERE temps_mean < 150.00')

# Write first part of JS source file
fHandleJS = open('data.tsv','w')
fHandleJS.write("date\tDark Sky API\tOpenWeatherMap\tWeather2\tWunderground\tHome\tMean\n")

# Start building array data
# Could be more elegant but is more readable this way
for msg_row in cursor:
    timestamp = str(msg_row[1])
    DSAPI_read = str(msg_row[2])
    OWM_read = str(msg_row[3])
    W2_read = str(msg_row[4])
    WG_read = str(msg_row[5])
    DS18B20_read = str(msg_row[6])
    temps_mean = str(msg_row[7])

    lineOut = timestamp + "\t" + DSAPI_read + "\t" + OWM_read + "\t" + \
              W2_read + "\t" + WG_read + "\t" + DS18B20_read + "\t" + \
              temps_mean + "\n"
    fHandleJS.write(lineOut)

# Close out array data
#fHandleJS.write("];")
fHandleJS.close()

# Clean up DB connection
tempsDB.close()
