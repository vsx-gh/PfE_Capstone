#!/usr/bin/env python

'''
Program:      collectTemp.py
Author:       Jeff VanSickle
Created:      20160506
Modified:     20160514

Script imports the WeatherAPI class and uses its functions to pull data from
five sources (four APIs and a local temp sensor):

    Dark Sky API (forecast.io)
    OpenWeatherMap
    Weather2
    Wunderground
    Raspberry Pi weather station with DS18B20 digital sensor

Every three minutes, each of the five sources is polled for Fahrenheit
temperature to two points of precision. These items, along with a timestamp,
are put into a SQLite database for later evaluation.

UPDATES:
    20160510 JV - Remove specific references to file paths and my location
    20160514 JV - Clean up some spacing

INSTRUCTIONS:

'''

from weatherAPIs import WeatherAPI
import time
import sqlite3

def leadZero(timeStr):
    """ Prepends a zero to time components less than 10 """
    if timeStr < 10:
        return '0' + str(timeStr)
    else:
        return str(timeStr)

# Set up SQLite DB
tempsDB = sqlite3.connect('<path_to_SQLite_DB>')
cursor = tempsDB.cursor()

# Create main DB table
cursor.execute(
        '''
        CREATE TABLE IF NOT EXISTS Temps(
            id INTEGER NOT NULL PRIMARY KEY AUTOINCREMENT UNIQUE,
            rectime TEXT UNIQUE,
            dsapi_read REAL,
            owm_read REAL,
            w2_read REAL,
            wg_read REAL,
            ds18b20_read REAL,
            temps_mean REAL,
            dsapi_delta REAL,
            owm_delta REAL,
            w2_delta REAL,
            wg_delta REAL,
            ds18b20_delta REAL)
        '''
)

# Geo coordinates (approx) of my home location
latIn = '<YOUR_LATITUDE>'
lonIn = '<YOUR_LONGITUDE>'

# Determine how often to commit DB
commitCounter = 0

# Temperature object
tempFObj = WeatherAPI(latIn, lonIn)

while True:
    # Build timestamp
    currTime = time.localtime()
    currYear = str(currTime.tm_year)
    currMonth = leadZero(currTime.tm_mon)
    currDay = leadZero(currTime.tm_mday)
    currHour = leadZero(currTime.tm_hour)
    currMin = leadZero(currTime.tm_min)
    currSec = leadZero(currTime.tm_sec)
    timestamp = currYear + currMonth + currDay + currHour + currMin + currSec

    # Read from sources
    DSAPI_read = tempFObj.getDSAPI()
    OWM_read = tempFObj.getOWM()
    W2_read =  tempFObj.getW2()
    WG_read =  tempFObj.getWG()
    DS18B20_read = tempFObj.getDS18B20()

    # Get mean
    temps_mean = tempFObj.getMean(DSAPI_read, OWM_read, W2_read, WG_read, DS18B20_read)

    # Get deltas from the mean
    DSAPI_delta = tempFObj.getDelta(DSAPI_read, temps_mean)
    OWM_delta = tempFObj.getDelta(OWM_read, temps_mean)
    W2_delta = tempFObj.getDelta(W2_read, temps_mean)
    WG_delta = tempFObj.getDelta(WG_read, temps_mean)
    DS18B20_delta = tempFObj.getDelta(DS18B20_read, temps_mean)

    # Write to DB
    cursor.execute('''INSERT INTO Temps
            (rectime, dsapi_read, owm_read, w2_read, wg_read, ds18b20_read,
            temps_mean, dsapi_delta, owm_delta, w2_delta, wg_delta, ds18b20_delta)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)''',
            (timestamp, DSAPI_read, OWM_read, W2_read, WG_read, DS18B20_read,
            temps_mean, DSAPI_delta, OWM_delta, W2_delta, WG_delta, DS18B20_delta))
    commitCounter = commitCounter + 1

    # Commit DB every ~15 minutes
    if commitCounter == 4:
        tempsDB.commit()
        commitCounter = 0

    time.sleep(180)

# Clean up
cursor.close()
