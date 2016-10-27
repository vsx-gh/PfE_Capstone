#!/usr/bin/env python

'''
Program:      weatherAPIs.py
Author:       Jeff VanSickle
Created:      20160813
Modified:     20161024

Module provides the functions needed to pull weather data from four
weather APIs:

    Dark Sky API
    OpenWeatherMap
    Weather2
    Wunderground

APIs output data in JSON.

UPDATES:
    20160813 JV - Replace static API key definitions with calls to environment
                  variables
                  getDS18B20() now pulling data locally instead of from remote
                  Web server
    20160823 JV - Correct "used before defined" error in API read functions;
                  return value inside if when JSON data is missing and exit
                  function, continue processing and return variable inside
                  else if we got workable JSON
    20161024 JV - Update to new Dark Sky API URL
INSTRUCTIONS:

'''
import urllib
import json
import os
import webTemp

class WeatherAPI:
    """ Fetches and stores weather data from selected APIs """

    def __init__(self, lat, lon):
        self.latitude = lat
        self.longitude = lon

    def fetchJSON(self, fetchURL):
        """ Query API addres and return JSON results """

        # Pull data from API
        try:
            openURL = urllib.urlopen(fetchURL)
            dataIn = openURL.read()
        except:
            resultsJSON = None
            return resultsJSON

        # Grab JSON from retrieved page, if any exists
        try: 
            resultsJSON = json.loads(str(dataIn))
        except:
            resultsJSON = None

        # Pretty-print JSON output
        #print json.dumps(resultsJSON, indent=4)

        return resultsJSON

    def getDSAPI(self):
        """ Retrieve current temperature from Dark Sky API """

        # Construct API URL with key and location
        baseURL = 'https://api.darksky.net/forecast/'
        APIkey = os.getenv('DS_APIKEY', None)
        dataURL = baseURL + APIkey + '/' + self.latitude + ',' + self.longitude
       
        # Get JSON from URL
        outputJSON = self.fetchJSON(dataURL)

        # We didn't get any JSON
        if outputJSON is None or len(outputJSON) < 1:
            return 999.99
        else:
            try:
                currentTemp = outputJSON['currently']['temperature']
                returnTemp = float(currentTemp)
            except:
                returnTemp = 999.99

            # Retrieve current temperature from JSON output
            #print 'Current temp: ', currentTemp
            return returnTemp

    def getOWM(self):
        """ Retrieve current temperature from OpenWeatherMap API """

        # Construct URL with key, location, and units
        baseURL = 'http://api.openweathermap.org/data/2.5/weather?'
        APIkey = os.getenv('OWM_APIKEY', None)
        dataURL = baseURL + urllib.urlencode({'lat': self.latitude, \
            'lon': self.longitude, 'APPID': APIkey, 'units': 'imperial'})
        
        # Get JSON from URL
        outputJSON = self.fetchJSON(dataURL)

        # We didn't get any JSON
        if outputJSON is None or len(outputJSON) < 1:
            return 999.99
        else:
            try:
                currentTemp = outputJSON['main']['temp']
                returnTemp = float(currentTemp)
            except:
                returnTemp = 999.99

            # Retrieve current temperature from JSON output
            #print 'Current temp: ', currentTemp
            return returnTemp

    def getW2(self):
        """ Retrieve current temperature from Weather2 API """

        # Construct URL with key, location, units
        baseURL = 'http://www.myweather2.com/developer/forecast.ashx?'
        APIkey = os.getenv('W2_APIKEY', None)
        loc = self.latitude + ',' + self.longitude
        dataURL = baseURL + urllib.urlencode({'uac': APIkey, 'output': 'json', \
                'query': loc, 'temp_unit': 'f'})

        # Get JSON from URL
        outputJSON = self.fetchJSON(dataURL)

        if outputJSON is None or len(outputJSON) < 1:
            return 999.99
        else:
            try:
                currentTemp = outputJSON['weather']['curren_weather'][0]['temp']
                returnTemp = float(currentTemp)
            except:
                returnTemp = 999.99

            # Retrieve current temperature from JSON output
            #print 'Current temp: ', currentTemp
            return returnTemp 

    def getWG(self):
        """ Retrieve current temperature from Wunderground API """

        # Contstruct URL with key, geo options
        baseURL = 'http://api.wunderground.com/api/'
        APIkey = os.getenv('WG_APIKEY', None)
        dataURL = baseURL + APIkey + '/' + 'geolookup/conditions/q/' + \
                self.latitude + ',' + self.longitude + '.json'

        # Get JSON from URL
        outputJSON = self.fetchJSON(dataURL)

        if outputJSON is None or len(outputJSON) < 1:
            return 999.99
        else:
            try:
                currentTemp = outputJSON['current_observation']['temp_f']
                returnTemp = float(currentTemp)
            except:
                returnTemp = 999.99

            # Retrieve current temperature from JSON output
            #print 'Current temp: ', currentTemp
            return returnTemp 

    def getDS18B20(self):
        """ Retrieve current temperature from DS18B20 sensor at home base """

        # Grab reading from DS18B20 sensor
        temps = webTemp.read_temp()
        temp_F = "%.2f" % temps[1]     # Set precision 2

        if temp_F is None or len(temp_F) < 1:
            return 999.99
        
        try:
            temp_F = float(temp_F)
        except:
            temp_F = 999.99

        return temp_F 

    def getMean(self, read_1, read_2, read_3, read_4, read_5):
        errReading = 999.99
        numReadings = 5

        # Readings of 0.00 (error reading) should not affect means
        if read_1 == errReading:
            numReadings = numReadings - 1
        if read_2 == errReading:
            numReadings = numReadings - 1
        if read_3 == errReading:
            numReadings = numReadings - 1
        if read_4 == errReading:
            numReadings = numReadings - 1
        if read_5 == errReading:
            numReadings = numReadings - 1

        if numReadings == 0:
            return 0.00
        else:
            readTotal = read_1 + read_2 + read_3 + read_4 + read_5
            readMean = readTotal / numReadings
            return readMean

    def getDelta(self, tempReading, tempMean):
        errReading = 999.99
        # Get delta from mean
        if tempReading < errReading:
            tempDelta = tempReading - tempMean
        else:
            tempDelta = errReading

        return tempDelta
