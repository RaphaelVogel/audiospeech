#!/usr/bin/python3
from tinkerforge.ip_connection import IPConnection
from tinkerforge.bricklet_io16 import BrickletIO16
import logging
import sys
import signal
import configparser
from logging.handlers import RotatingFileHandler
import time


# logger configuration
logger = logging.getLogger("alarm_logger")
logger.setLevel(logging.INFO)
filehandler = RotatingFileHandler('/home/pi/base/alarm_log.txt', maxBytes=100000, backupCount=2)
formatter = logging.Formatter('%(asctime)s : %(levelname)s : %(message)s', datefmt='%d-%m-%Y %H:%M:%S')
filehandler.setFormatter(formatter)
logger.addHandler(filehandler)

cfg = configparser.ConfigParser()
cfg.read('/home/pi/base/tools/config.txt')

ipcon = IPConnection()


def signal_handler(signal_type, frame):
    logger.info("Alarm Service stopped")
    ipcon.disconnect()
    sys.exit(0)


def change_detected(port, interrupt_mask, value_mask):
    if value_mask & 0b00000001:  # north side motion detector is high (open)
        logger.warn("Alarm on north side motion detector")
    if value_mask & 0b00000010:  # west side motion detector is high (open)
        logger.warn("Alarm on west side motion detector")


def start_alarm_check():
    try:
        ipcon.connect(cfg['weather']['host'], int(cfg['weather']['port']))
        time.sleep(1)
        io16 = BrickletIO16('sof', ipcon)
        io16.set_debounce_period(4000)
        io16.set_port_configuration('a', 0b11111111, 'i', True)
        io16.set_port_interrupt('a', 0b00000011)
        io16.register_callback(BrickletIO16.CALLBACK_INTERRUPT, change_detected)
        logger.info("Alarm Service started")
        while True:
            time.sleep(1.0)

        logger.info("Alarm Service stopped -> termination of while loop")
    except Exception as e:
        logger.error('Could not connect to alarm TF stack: %s' % str(e))
        return


if __name__ == "__main__":
    signal.signal(signal.SIGTERM, signal_handler)
    start_alarm_check()
