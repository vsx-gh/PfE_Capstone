#!/usr/bin/env python

'''
Program:      collectTemp.py
Author:       Jeff VanSickle
Created:      20160813
Modified:     20170130

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
    20160813 JV - Replace static latitude and longitude with reads from
                  environment variables
                  Update SQLite DB location for local system
    20170130 JV - Use datetime module to build timestamp; drop leadZero function
    20170130 JV - Add pgaws module for writing to AWS PostgreSQL instance

INSTRUCTIONS:
    - Replace <YOUR_TEMPS_DB> with location of your SQLite database
    - Replace <YOUR_DB> with your RDS database
    - Replace <YOUR_TABLE> with your RDS table in the target database

'''

from weatherAPIs import WeatherAPI
import os
import time
import datetime
import sqlite3
import pgaws

# Set up SQLite DB
tempsDB = sqlite3.connect('<YOUR_TEMPS_DB>')
cursor = tempsDB.cursor()

# Get cursor for AWS PostgreSQL DB
try:
    pgcursor = pgaws.create_cursor()
except:
    dtime_now = datetime.datetime.now().strftime('%Y%m%d%H%M%S')
    print '{}: Failed to create psql cursor.'.format(dtime_now)

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
latIn = os.getenv('SYSLAT', None)
lonIn = os.getenv('SYSLON', None)

# Can't proceed without a proper location
if latIn is None or lonIn is None:
    print 'System geo coordinates not defined. Exiting....'
    quit()

# Determine how often to commit DB
commitCounter = 0

# Temperature object
tempFObj = WeatherAPI(latIn, lonIn)

while True:
    timestamp = datetime.datetime.now().strftime('%Y%m%d%H%M%S')
    
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

    # Get max ID for psql DB, then write to it
    try:
        pgcursor.execute("SELECT MAX(id) FROM <YOUR_DB>.<YOUR_TABLE>;")
        pgmax_id = pgcursor.fetchall()
        pgrow_id = pgmax_id[0][0] + 1

        pgcursor.execute("""
            INSERT INTO <YOUR_DB>.<YOUR_TABLE>
            (id, rectime, dsapi_read, owm_read, w2_read, wg_read,
            ds18b20_read, temps_mean, dsapi_delta, owm_delta,
            w2_delta, wg_delta, ds18b20_delta) VALUES
            (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s);""",
            (pgrow_id, timestamp, DSAPI_read, OWM_read, W2_read, WG_read, 
            DS18B20_read, temps_mean, DSAPI_delta, OWM_delta, W2_delta, 
            WG_delta, DS18B20_delta)
        )

        # Committing more frequently because we're going over the wire
        pgcursor.execute("COMMIT")
    except:
        dtime_now = datetime.datetime.now().strftime('%Y%m%d%H%M%S')
        print '{}: Error writing to AWS psql.'.format(dtime_now)

    commitCounter = commitCounter + 1
    
    # Commit DB ~15 minutes
    if commitCounter == 4:
        tempsDB.commit()
        commitCounter = 0

    time.sleep(180)

# Clean up
cursor.close()
pgcursor.close()
