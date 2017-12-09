#!/usr/bin/env python3

'''
Program:      webTemp.py
Author:       Simon Monk, Jeff VanSickle
Created:      20160506
Modified:     20170130

Program runs on a Raspberry Pi Model B (1st generation). Reads input from
DS18B20 digital temperature sensor.

In addtion to Simon's DS18B20 tutorial, which includes the modprobe
commands to recognize the temp sensor, it is also right to recognize Matt
at Raspberry Pi Spi, whose post helped me get over reading the correct pin
on my board. That included adding something (the ",gpiopin=25") to what I
found in Simon's post to /boot/config.txt:

    dtoverlay=w1-gpio,gpiopin=25

Adafruit DS18B20 Tutorial:
https://learn.adafruit.com/adafruits-raspberry-pi-lesson-11-ds18b20-
temperature-sensing/software

Matt's Raspberry Pi Spi post:
http://www.raspberrypi-spy.co.uk/2013/03/raspberry-pi-1-wire-digital-
thermometer-sensor/#prettyPhoto/3/

UPDATES:
    20170130 JV - Add test condition for bus device file; stop running
                  modprobe unnecessarily

INSTRUCTIONS:

''' 

import time
import os
import glob

def get_device():
    '''
    Finds device files for temp sensor
    Attempts to find the physical device if files not present
    '''

    # Find device file for temp sensor
    base_dir = '/sys/bus/w1/devices/'
    device_folder = glob.glob(base_dir + '28*')[0]
    device_file = device_folder + '/w1_slave'

    # Have OS scan for device if not represented in bus
    if not os.path.isfile(device_file):
        os.system('sudo modprobe w1-gpio')
        os.system('sudo modprobe w1-therm')

    if not os.path.isfile(device_file):
        return False

    return True


               
def read_temp_raw():
    f = open(device_file, 'r')
    lines = f.readlines()
    f.close()

    return lines



def read_temp():
    have_therm = get_device()     # Make sure probe available for reading

    if not have_therm:
        return None

    lines = read_temp_raw()

    while lines[0].strip()[-3:] != 'YES':
        time.sleep(0.2)
        lines = read_temp_raw()

    equals_pos = lines[1].find('t=')

    if equals_pos != -1:
        temp_string = lines[1][equals_pos + 2:]
        temp_c = float(temp_string) / 1000.0
        temp_f = temp_c * 9.0 / 5.0 + 32.0

    return temp_c, temp_f
