#!/usr/bin/python3
from tinkerforge.ip_connection import IPConnection
from tinkerforge.bricklet_ambient_light_v2 import BrickletAmbientLightV2
from tinkerforge.ip_connection import Error
import logging
import os
import configparser
from logging.handlers import RotatingFileHandler
import socket


# logger configuration
log = logging.getLogger("brightness_logger")
log.setLevel(logging.INFO)
filehandler = RotatingFileHandler('/home/pi/base/logs/brightness_log.txt', maxBytes=10000, backupCount=2)
formatter = logging.Formatter('%(asctime)s : %(levelname)s : %(message)s', datefmt='%d-%m-%Y %H:%M:%S')
filehandler.setFormatter(formatter)
log.addHandler(filehandler)

cfg = configparser.ConfigParser()
cfg.read('/home/pi/base/tools/config.txt')


ipcon = IPConnection()
its_day = "/home/pi/base/tools/its_day"


def start_brightness_check():
    try:
        ipcon.connect(cfg['weather']['host'], int(cfg['weather']['port']))
        al = BrickletAmbientLightV2('xxxxxxxxxx', ipcon)
        brightness = al.get_illuminance()
        if (brightness / 100.0) > 80.0:  # 80 Lux
            # day
            if not os.path.exists(its_day):
                open(its_day, 'w').close()
        else:
            # night
            if os.path.exists(its_day):
                os.remove(its_day)

    except Error as e:
        log.error('Could not read Ambient Light Bricklet: ' + str(e.description))
        ipcon.disconnect()


if __name__ == "__main__":
    start_brightness_check()
    ipcon.disconnect()