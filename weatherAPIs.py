#!/usr/bin/env python

'''
Program:      weatherAPIs.py
Author:       Jeff VanSickle
Created:      20160502
Modified:     20160514

Module provides the functions needed to pull weather data from four
weather APIs:

    Dark Sky API (forecast.io)
    OpenWeatherMap
    Weather2
    Wunderground

APIs output data in JSON.

UPDATES:
    20160510 JV - Remove info specific to me and my location
    20160514 JV - Clarify error condition as 999.99 in comments, clean spacing,
                  correct spelling error in comments

INSTRUCTIONS:
    - Replace '<YOUR_API_KEY>' with your API key for each API
    - Replace '<YOUR_PI_SERVER>' with the address of your RasPi Apache server

'''
import urllib
import json

class WeatherAPI:
    """ Fetches and stores weather data from selected APIs """

    def __init__(self, lat, lon):
        self.latitude = lat
        self.longitude = lon

    def fetchJSON(self, fetchURL):
        """ Query API address and return JSON results """

        # Pull data from API
        openURL = urllib.urlopen(fetchURL)
        dataIn = openURL.read()

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
        baseURL = 'https://api.forecast.io/forecast/'
        APIkey = '<YOUR_API_KEY>'
        dataURL = baseURL + APIkey + '/' + self.latitude + ',' + self.longitude

        # Get JSON from URL
        outputJSON = self.fetchJSON(dataURL)

        # We didn't get any JSON
        if len(outputJSON) < 1 or outputJSON == None:
            currentTemp = 'NULL'
        else:
            currentTemp = outputJSON['currently']['temperature']

        try:
            returnTemp = float(currentTemp)
        except:
            returnTemp = 999.99

        # Retrieve current temperature from JSON output
        #print 'Current temp: ', currentTemp
        return returnTemp

    def getOWM(self):
        """ Retrieve current temperature from OpenWeatherMap API """

        # Construct URL with key, location, and units
        APIkey = '<YOUR_API_KEY>'
        baseURL = 'http://api.openweathermap.org/data/2.5/weather?'
        dataURL = baseURL + urllib.urlencode({'lat': self.latitude, \
            'lon': self.longitude, 'APPID': APIkey, 'units': 'imperial'})

        # Get JSON from URL
        outputJSON = self.fetchJSON(dataURL)

        # We didn't get any JSON
        if len(outputJSON) < 1 or outputJSON == None:
            currentTemp = 'NULL'
        else:
            currentTemp = outputJSON['main']['temp']

        try:
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
        APIkey = '<YOUR_API_KEY>'
        loc = self.latitude + ',' + self.longitude
        dataURL = baseURL + urllib.urlencode({'uac': APIkey, 'output': 'json', \
                'query': loc, 'temp_unit': 'f'})

        # Get JSON from URL
        outputJSON = self.fetchJSON(dataURL)

        if len(outputJSON) < 1 or outputJSON == None:
            currentTemp = 'NULL'
        else:
            currentTemp = outputJSON['weather']['curren_weather'][0]['temp']

        try:
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
        APIkey = '<YOUR_API_KEY>'
        dataURL = baseURL + APIkey + '/' + 'geolookup/conditions/q/' + \
                self.latitude + ',' + self.longitude + '.json'

        # Get JSON from URL
        outputJSON = self.fetchJSON(dataURL)

        if len(outputJSON) < 1 or outputJSON == None:
            currentTemp = 'NULL'
        else:
            currentTemp = outputJSON['current_observation']['temp_f']

        try:
            returnTemp = float(currentTemp)
        except:
            returnTemp = 999.99

        # Retrieve current temperature from JSON output
        #print 'Current temp: ', currentTemp
        return returnTemp

    def getDS18B20(self):
        """ Retrieve current temperature from DS18B20 sensor at home base """
        fetchURL = 'http://<YOUR_PI_SERVER>/temp.txt'

        # Get webpage from Pi Apache server
        openURL = urllib.urlopen(fetchURL)
        dataIn = openURL.read()

        if len(dataIn) < 1 or dataIn == None:
            currentTemp = 'NULL'
        else:
            currentTemp = dataIn

        try:
            returnTemp = float(currentTemp)
        except:
            returnTemp = 999.99

        return returnTemp

    def getMean(self, read_1, read_2, read_3, read_4, read_5):
        errReading = 999.99
        numReadings = 5

        # Readings of 999.99 (error reading) should not affect means
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
