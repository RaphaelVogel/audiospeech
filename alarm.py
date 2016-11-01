#!/usr/bin/python3
from tinkerforge.ip_connection import IPConnection
from tinkerforge.bricklet_io16 import BrickletIO16
from tinkerforge.ip_connection import Error
import logging
import sys
import signal
import configparser
from logging.handlers import RotatingFileHandler
import time
import socket
import requests
import urllib


# logger configuration
log = logging.getLogger("alarm_logger")
log.setLevel(logging.INFO)
filehandler = RotatingFileHandler('/home/pi/base/logs/alarm_log.txt', maxBytes=100000, backupCount=2)
formatter = logging.Formatter('%(asctime)s : %(levelname)s : %(message)s', datefmt='%d-%m-%Y %H:%M:%S')
filehandler.setFormatter(formatter)
log.addHandler(filehandler)

cfg = configparser.ConfigParser()
cfg.read('/home/pi/base/tools/config.txt')


ipcon = IPConnection()


def change_detected(port, interrupt_mask, value_mask):
    if interrupt_mask & 0b00000001:     # interrupt on pin 0
        if value_mask & 0b00000001:     # pin 0 is high: north side motion detector
            log.warn("Alarm on north side motion detector")
            message = urllib.parse.quote_plus("Bewegungsmelder Nord (Terasse)")
            requests.get("http://localhost:8080/pushOver/alarm/" + message)

    if interrupt_mask & 0b00000010:     # interrupt on pin 1
        if value_mask & 0b00000010:     # pin 1 is high: west side motion detector
            log.warn("Alarm on west side motion detector")
            message = urllib.parse.quote_plus("Bewegungsmelder West (Gartenhaus)")
            requests.get("http://localhost:8080/pushOver/alarm/" + message)


def cb_enumerate(uid, connected_uid, position, hardware_version, firmware_version, device_identifier, enumeration_type):
    if enumeration_type == IPConnection.ENUMERATION_TYPE_CONNECTED or enumeration_type == IPConnection.ENUMERATION_TYPE_AVAILABLE:
        if device_identifier == BrickletIO16.DEVICE_IDENTIFIER:
            try:
                io16 = BrickletIO16('b7Y', ipcon)
                io16.set_debounce_period(5000)
                io16.set_port_configuration('a', 0b11111111, 'i', True)
                io16.set_port_interrupt('a', 0b00000011)
                io16.register_callback(BrickletIO16.CALLBACK_INTERRUPT, change_detected)
            except Error as e:
                log.error('IO16 init failed: ' + str(e.description))


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


def start_alarm_check():
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
            log.info("Alarm Service started")
            break
        except Error as e:
            log.error('Enumerate Error: ' + str(e.description))
            time.sleep(1)


def signal_handler(signal_type, frame):
    log.info("Alarm Service stopped")
    ipcon.disconnect()
    sys.exit(0)


if __name__ == "__main__":
    signal.signal(signal.SIGTERM, signal_handler)
    start_alarm_check()
    while True:
        time.sleep(1)

    ipcon.disconnect()
