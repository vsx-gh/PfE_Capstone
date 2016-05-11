#!/usr/bin/env python

'''
Program:      webTemp.py
Author:       Simon Monk, Jeff VanSickle
Created:      20160506
Modified:     20160510

Program runs on a Raspberry Pi Model B (1st generation). Reads input from
DS18B20 digital temperature sensor, then puts out temp to an Apache server.

The Apache output is admittedly pretty low-fi, but the intent is to make the
string available for fetching by a client machine for use elsewhere.

The vast majority of this code is from Simon Monk's Adafruit tutorial on how
to interface with the DS18B20. I made additions and added code that utilizes
Simon's functions.

In addtion to Simon's DS18B20 tutorial, which includes the modprobe
commands to recognize the temp sensor, it is also right to recognize Matt
at Raspberry Pi Spi, whose post helped me get over reading the correct pin
on my board. That included adding something (the ",gpiopin=25") to what I
found in Simon's post to /boot/config.txt:

    dtoverlay=w1-gpio,gpiopin=25

Adafruit DS18B20 Tutorial:
https://learn.adafruit.com/adafruits-raspberry-pi-lesson-11-ds18b20-
temperature-sensing/

Matt's Raspberry Pi Spi post:
http://www.raspberrypi-spy.co.uk/2013/03/raspberry-pi-1-wire-digital-
thermometer-sensor/#prettyPhoto/3/

UPDATES:
    20160510 JV - Remove most debug code and other stuff that didn't work or is
    superfluous

INSTRUCTIONS:
    - Run this code after you set up a basic Apache server on your Pi. Access
    the data at http://<YOUR_PI_SERVER>/temp.txt

'''

import RPi.GPIO as GPIO
import time
import os
import glob

GPIO.setmode(GPIO.BCM)
os.system('modprobe w1-gpio')
os.system('modprobe w1-therm')

base_dir = '/sys/bus/w1/devices/'
device_folder = glob.glob(base_dir + '28*')[0]
device_file = device_folder + '/w1_slave'

def read_temp_raw():
    f = open(device_file, 'r')
    lines = f.readlines()
    f.close()

    return lines

def read_temp():
    lines = read_temp_raw()

    while lines[0].strip()[-3:] != 'YES':
        time.sleep(0.2)
        lines = read_temp_raw()

    equals_pos = lines[1].find('t=')

    if equals_pos != -1:
        temp_string = lines[1][equals_pos+2:]
        temp_c = float(temp_string) / 1000.0
        temp_f = temp_c * 9.0 / 5.0 + 32.0

    return temp_c, temp_f


while True:
    # Get temperatures from sensor
    temps = read_temp()
    temp_C = "%.2f" % temps[0]     # Set precision 2
    temp_F = "%.2f" % temps[1]     # Set precision 2
    #print temp_C, " ", temp_F     # Debug

    os.system('echo "" > /var/www/html/temp.txt')
    fhandle = open('/var/www/html/temp.txt', 'r+')
    fhandle.write(temp_F)
    fhandle.close()

    #print temp_F
    time.sleep(10)
