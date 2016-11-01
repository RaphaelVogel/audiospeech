#!/usr/bin/python3
from tinkerforge.ip_connection import IPConnection
from tinkerforge.bricklet_ambient_light_v2 import BrickletAmbientLightV2
from tinkerforge.ip_connection import Error
import logging
import sys
import os
import signal
import configparser
from logging.handlers import RotatingFileHandler
import time
import socket


# logger configuration
log = logging.getLogger("brightness_logger")
log.setLevel(logging.INFO)
filehandler = RotatingFileHandler('/home/pi/base/brightness_log.txt', maxBytes=10000, backupCount=2)
formatter = logging.Formatter('%(asctime)s : %(levelname)s : %(message)s', datefmt='%d-%m-%Y %H:%M:%S')
filehandler.setFormatter(formatter)
log.addHandler(filehandler)

cfg = configparser.ConfigParser()
cfg.read('/home/pi/base/tools/config.txt')


ipcon = IPConnection()
its_day = "/home/pi/base/tools/its_day"


def brightness_callback(brighness):
    if (brighness / 100.0) > 80.0:  # 80 Lux
        # day
        if not os.path.exists(its_day):
            open(its_day, 'w').close()
    else:
        # night
        if os.path.exists(its_day):
            os.remove(its_day)


def cb_enumerate(uid, connected_uid, position, hardware_version, firmware_version, device_identifier, enumeration_type):
    if enumeration_type == IPConnection.ENUMERATION_TYPE_CONNECTED or enumeration_type == IPConnection.ENUMERATION_TYPE_AVAILABLE:
        if device_identifier == BrickletAmbientLightV2.DEVICE_IDENTIFIER:
            try:
                al = BrickletAmbientLightV2('xxxxxxxxxx', ipcon)
                al.register_callback(al.CALLBACK_ILLUMINANCE, brightness_callback)
                al.set_illuminance_callback_period(300000)  # 5 min
            except Error as e:
                log.error('Ambient Light Bricklet init failed: ' + str(e.description))


def cb_connected(connected_reason):
    if connected_reason == IPConnection.CONNECT_REASON_AUTO_RECONNECT:
        log.info('Auto Reconnect triggered')
        while True:
            try:
                ipcon.enumerate()
                break
            except Error as e:
                log.error('Enumerate Error: ' + str(e.description))
                time.sleep(1)


def start_brightness_check():
    while True:
        try:
            ipcon.connect(cfg['weather']['host'], int(cfg['weather']['port']))
            break
        except Error as e:
            log.error('Connection Error: ' + str(e.description))
            time.sleep(1)
        except socket.error as e:
            log.error('Socket error: ' + str(e))
            time.sleep(1)

    ipcon.register_callback(IPConnection.CALLBACK_ENUMERATE, cb_enumerate)
    ipcon.register_callback(IPConnection.CALLBACK_CONNECTED, cb_connected)

    while True:
        try:
            ipcon.enumerate()
            log.info("Brightness Service started")
            break
        except Error as e:
            log.error('Enumerate Error: ' + str(e.description))
            time.sleep(1)


def signal_handler(signal_type, frame):
    log.info("Brightness Service stopped")
    ipcon.disconnect()
    sys.exit(0)


if __name__ == "__main__":
    signal.signal(signal.SIGTERM, signal_handler)
    start_brightness_check()
    while True:
        time.sleep(1)

    ipcon.disconnect()
