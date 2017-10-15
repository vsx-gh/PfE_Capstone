#!/usr/bin/env python3

'''
Program:      collectTemp.py
Author:       Jeff VanSickle
Created:      20160813
Modified:     20170730

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
    20170730 JV - Convert to Python3
                  Replace Postgres RDS with DynamoDB
                  Configure for input parameters

INSTRUCTIONS:
    - Set up SYSLAT and SYSLON environment variables for your location
'''

from weatherAPIs import WeatherAPI
import os
import time
import datetime
import sqlite3
import boto3
import argparse
from decimal import *

getcontext().prec = 2

# Get input(s)
inputs = argparse.ArgumentParser()
inputs.add_argument('-l', '--localdb',
                    required=True,
                    help='Name of local SQLite DB to use')
inputs.add_argument('-d', '--awsdb',
                   required=True,
                   help='Name of DynamoDB table to use')
args = inputs.parse_args()
dynamo_table = args.awsdb
local_db = args.localdb

# Set up SQLite DB
temps_db = sqlite3.connect(local_db)
sqlite_cursor = temps_db.cursor()

# Create DynamoDB client
dynamo_db = boto3.resource('dynamodb')

# Connect to DynamoDB table
try:
    aws_cursor = dynamo_db.Table(dynamo_table)
except:
    print('Error connecting to DynamoDB table. Check name and try again.')
    quit()

# Create main DB table if it doesn't exist
sqlite_cursor.execute('''
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
            ds18b20_delta REAL)'''
)

# Geo coordinates (approx) of my home location
lat = os.getenv('SYSLAT', None)
lon = os.getenv('SYSLON', None)

# Can't proceed without a proper location
if lat is None or lon is None:
    print('System geo coordinates not defined. Exiting....')
    quit()

# Temperature object
tempf_obj = WeatherAPI(lat, lon)

timestamp = datetime.datetime.utcnow().strftime('%Y%m%d%H%M%S')
    
# Read from sources
DSAPI_read = tempf_obj.get_DSAPI()
OWM_read = tempf_obj.get_OWM()
W2_read =  tempf_obj.get_W2()
WG_read =  tempf_obj.get_WG()
DS18B20_read = tempf_obj.get_DS18B20()

# Get mean
temps_mean = tempf_obj.get_mean(DSAPI_read, OWM_read, W2_read, WG_read, DS18B20_read)

# Get deltas from the mean
DSAPI_delta = tempf_obj.get_delta(DSAPI_read, temps_mean)
OWM_delta = tempf_obj.get_delta(OWM_read, temps_mean)
W2_delta = tempf_obj.get_delta(W2_read, temps_mean)
WG_delta = tempf_obj.get_delta(WG_read, temps_mean)
DS18B20_delta = tempf_obj.get_delta(DS18B20_read, temps_mean)

# Write to local DB
sqlite_cursor.execute('''INSERT INTO Temps 
        (rectime, dsapi_read, owm_read, w2_read, wg_read, ds18b20_read, 
        temps_mean, dsapi_delta, owm_delta, w2_delta, wg_delta, ds18b20_delta)
        VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)''',
        (timestamp, DSAPI_read, OWM_read, W2_read, WG_read, DS18B20_read,
        temps_mean, DSAPI_delta, OWM_delta, W2_delta, WG_delta, DS18B20_delta))

# Write to DynamoDB
try:
    aws_cursor.put_item(
        Item={
            'rectime': str(timestamp),
            'dsapi_read': Decimal(str(DSAPI_read)),
            'owm_read': Decimal(str(OWM_read)),
            'w2_read': Decimal(str(W2_read)),
            'wg_read': Decimal(str(WG_read)),
            'ds18b20_read': Decimal(str(DS18B20_read)),
            'temps_mean': Decimal(str(temps_mean)),
            'dsapi_delta': Decimal(str(DSAPI_delta)),
            'owm_delta': Decimal(str(OWM_delta)),
            'w2_delta': Decimal(str(W2_delta)),
            'wg_delta': Decimal(str(WG_delta)),
            'ds18b20_delta': Decimal(str(DS18B20_delta))
            }
        )
except:
    print('{}: Error writing DynamoDB.'.format(datetime.datetime.utcnow()))

# Clean up SQLite cursor
sqlite_cursor.close()
