#!/usr/bin/env python3

'''
Program:      weatherAPIs.py
Author:       Jeff VanSickle
Created:      20160813
Modified:     20170730

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
                  get_DS18B20() now pulling data locally instead of from remote
                  Web server
    20160823 JV - Correct "used before defined" error in API read functions;
                  return value inside if when JSON data is missing and exit
                  function, continue processing and return variable inside
                  else if we got workable JSON
    20161024 JV - Update to new Dark Sky API URL
    20170130 JV - Use list comprehension to simplify mean calculation
                  Make error reading (999.99) a class global
    20170730 JV - Convert to Python 3
                  Refactor variable names - eliminate camelcase
INSTRUCTIONS:
    - Configure API key environment variables for your accounts

'''
import urllib
import json
import os
import webTemp

class WeatherAPI:
    """ Fetch and store weather data from selected APIs """

    def __init__(self, lat, lon):
        self.latitude = lat
        self.longitude = lon
        self.err_reading = 999.99

    def fetch_JSON(self, fetch_URL):
        """ Query API address and return JSON results """

        # Pull data from API
        try:
            open_URL = urllib.request.urlopen(fetch_URL)
            data_in = open_URL.read().decode('utf-8')

        except:
            results_JSON = None
            return results_JSON

        # Grab JSON from retrieved page, if any exists
        try: 
            results_JSON = json.loads(str(data_in))
        except:
            results_JSON = None

        # Pretty-print JSON output
        #print(json.dumps(results_JSON, indent=4))

        return results_JSON

    def get_DSAPI(self):
        """ Retrieve current temperature from Dark Sky API """

        # Construct API URL with key and location
        base_URL = 'https://api.darksky.net/forecast/'
        api_key = os.getenv('DS_APIKEY', None)
        data_URL = base_URL + api_key + '/' + self.latitude + ',' + self.longitude
       
        # Get JSON from URL
        output_JSON = self.fetch_JSON(data_URL)

        # We didn't get any JSON
        if output_JSON is None or len(output_JSON) < 1:
            return self.err_reading
        else:
            try:
                curr_temp = output_JSON['currently']['temperature']
                return_temp = float(curr_temp)
            except:
                return_temp = self.err_reading

            # Retrieve current temperature from JSON output
            #print 'Current temp: ', curr_temp
            return return_temp

    def get_OWM(self):
        """ Retrieve current temperature from OpenWeatherMap API """

        # Construct URL with key, location, and units
        base_URL = 'http://api.openweathermap.org/data/2.5/weather?'
        api_key = os.getenv('OWM_APIKEY', None)
        data_URL = base_URL + urllib.parse.urlencode({'lat': self.latitude, \
            'lon': self.longitude, 'APPID': api_key, 'units': 'imperial'})
        
        # Get JSON from URL
        output_JSON = self.fetch_JSON(data_URL)

        # We didn't get any JSON
        if output_JSON is None or len(output_JSON) < 1:
            return self.err_reading
        else:
            try:
                curr_temp = output_JSON['main']['temp']
                return_temp = float(curr_temp)
            except:
                return_temp = self.err_reading

            # Retrieve current temperature from JSON output
            #print 'Current temp: ', curr_temp
            return return_temp

    def get_W2(self):
        """ Retrieve current temperature from Weather2 API """

        # Construct URL with key, location, units
        base_URL = 'http://www.myweather2.com/developer/forecast.ashx?'
        api_key = os.getenv('W2_APIKEY', None)
        loc = self.latitude + ',' + self.longitude
        data_URL = base_URL + urllib.parse.urlencode({'uac': api_key, 'output': 'json', \
                'query': loc, 'temp_unit': 'f'})

        # Get JSON from URL
        output_JSON = self.fetch_JSON(data_URL)

        if output_JSON is None or len(output_JSON) < 1:
            return self.err_reading
        else:
            try:
                # NOT a typo in the JSON path; "curren_weather" is correct
                curr_temp = output_JSON['weather']['curren_weather'][0]['temp']
                return_temp = float(curr_temp)
            except:
                return_temp = self.err_reading

            # Retrieve current temperature from JSON output
            #print 'Current temp: ', curr_temp
            return return_temp

    def get_WG(self):
        """ Retrieve current temperature from Wunderground API """

        # Contstruct URL with key, geo options
        base_URL = 'http://api.wunderground.com/api/'
        api_key = os.getenv('WG_APIKEY', None)
        data_URL = base_URL + api_key + '/' + 'geolookup/conditions/q/' + \
                self.latitude + ',' + self.longitude + '.json'

        # Get JSON from URL
        output_JSON = self.fetch_JSON(data_URL)

        if output_JSON is None or len(output_JSON) < 1:
            return self.err_reading
        else:
            try:
                curr_temp = output_JSON['current_observation']['temp_f']
                return_temp = float(curr_temp)
            except:
                return_temp = self.err_reading

            # Retrieve current temperature from JSON output
            #print 'Current temp: ', curr_temp
            return return_temp

    def get_DS18B20(self):
        """ Retrieve current temperature from DS18B20 sensor at home base """

        # Grab reading from DS18B20 sensor
        temps = webTemp.read_temp()
        if temps == None:
            return temps

        temp_F = "%.2f" % temps[1]     # Set precision 2

        if temp_F is None or len(temp_F) < 1:
            return self.err_reading
        
        try:
            temp_F = float(temp_F)
        except:
            temp_F = self.err_reading

        return temp_F

    def get_mean(self, read_1, read_2, read_3, read_4, read_5):
        """ Find mean of non-error readings read_[1-5] """

        # Readings of 999.99 (error reading) should not affect means
        readings = [item for item in [read_1, read_2, read_3, read_4, read_5] if item != self.err_reading]

        if len(readings) == 0:
            return 0.00
        else:
            read_mean = sum(readings) / len(readings)
            return read_mean

    def get_delta(self, temp_reading, temp_mean):
        """ Calculate and returns difference of temp_reading from temp_mean """

        if temp_reading < self.err_reading:
            temp_delta = temp_reading - temp_mean
        else:
            temp_delta = self.err_reading

        return temp_delta
