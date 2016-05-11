================================================================================
Programming for Everybody (Python) - Capstone
Jeff VanSickle
Spring 2016
================================================================================

This project was completed as part of the Programming for Everybody specializat-
ion through Coursera, taken with Dr. Chuck Severance. The project demonstrates
mastery of the concepts learned in intermediate Python programming.

My project uses Python to collect temperature for a specific location (my home)
across five data sources: four APIs and one temperature sensor located at my
house. The temperature sensor is a DS18B20 digital sensor connected to a
Raspberry Pi through a custom shield that I soldered together. There is not much
special about the shield; if you can connect the sensor to GPIO BCM pin 25 on
the Pi, you will be good to go. I put the collected data into a SQLite database,
then extract data from the database to build a simple line graph with the D3
Javascript library.

Here is a simple rundown of how to run the code and what you will need:

1) Set up a simple Apache server on your Raspberry Pi. I am using a first-gen
Model B board, but you may have something different. Regardless, getting a basic
Web server up is fairly simple. I will leave this to the plethora of tutorials
on the Web.

2) Put webTemp.py on your Pi and run it. Make sure you go through the tutorials
linked in the comments section so you get your sensor reading correctly. After
your server is up, you can access the current temperature reading from the URL
specified in the code and comments.

3) I used a second machine to collect data both from the Pi and the APIs, but
that is not strictly necessary. You could collect from the sensor on the same
Pi that you use to grab data from the APIs. In my case, I had some physical
constraints with regard to networking, so I used two machines.

4) Register with the APIs in weatherAPIs.py and put your unique API keys in the
code where instructed. You should also put in the URL of your Pi server so you
can grab your local temperature reading.

5) Run collectTemp.py to grab data from all of your inputs and write it to a
SQLite database. Given the API daily limits, I set my interval to three minutes
between readings. If the APIs change their limits, you may need to adjust this
value.

6) Once you have collected some data, you can run tempsVis.py to prepare a
source file for your visualization. This will generate data.tsv, a tab-separated
file needed by d3Vis.html. d3Vis.html will be the line graph that represents the
data you collected. PLEASE NOTE: Google Chrome does not allow opening local
files by default, so you will have to do some finagling to get that to work. In
my experience, Firefox does not throw up the same roadblocks. If your d3Vis.html
is blank, try opening it in Firefox to see your graph.



--------
LICENSES
--------

d3Vis.html is not my code and belongs to Michael Bostock. His code is covered
by a BSD license, which can be found in D3_LICENSE.txt and at
https://github.com/mbostock/d3/blob/master/LICENSE.

I have not found licensing info for Simon Monk's DS18B20 code supplied through
the Adafruit website. In that case, I have included links to the tutorial where
I found the code as attribution. All rights to that code belong to its authors
and/or sponsors.

collectTemp.py, weatherAPIs.py, and tempsVis.py are covered by an MIT license.
Please see LICENSE.txt for info.

Point here is that all of the code is free for you to download, use, modify,
break, improve, or do anything else with as you see fit. If you choose to
redistribute it, make an effort to adhere to the licenses set forth here.
Thanks!



---------
API Terms
---------

In compliance with the terms of the various APIs I used, I am citing and
linking to them here:

Dark Sky API: https://developer.forecast.io/
OpenWeatherMap: http://openweathermap.org/
Weather2: http://www.myweather2.com/developer/apis.aspx?uref=becda844-8299-4bf6-899b-d771a92b9dbf
Wunderground: https://www.wunderground.com/weather/api/d/docs
