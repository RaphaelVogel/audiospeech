import logging, configparser
from collections import OrderedDict

from tinkerforge.ip_connection import IPConnection
from tinkerforge.bricklet_temperature import Temperature
from tinkerforge.bricklet_humidity import Humidity
from tinkerforge.bricklet_barometer import Barometer

cfg = configparser.ConfigParser()
cfg.read('/home/pi/base/tools/config.txt')

logger = logging.getLogger("base_logger")
weather_data = OrderedDict()


def read_data():
    try:
        ipcon = IPConnection()
        temp_bricklet = Temperature('qnk', ipcon)
        humidity_bricklet = Humidity('nLC', ipcon)
        barometer_bricklet = Barometer('k5g', ipcon)
        ipcon.connect(cfg['weather']['host'], int(cfg['weather']['port']))
        temp_bricklet.set_i2c_mode(Temperature.I2C_MODE_SLOW)

        temp = temp_bricklet.get_temperature() / 100.0
        if 45 < temp < -30:
            weather_data['temperature'] = None
            logger.warn('Got temperature value of %s Grade which is out of range' % temp)
        else:
            weather_data['temperature'] = temp

        humidity = humidity_bricklet.get_humidity() / 10.0
        if humidity < 5:
            weather_data['humidity'] = None
            logger.warn('Got humidity value of %s RH which is out of range' % humidity)
        else:
            weather_data['humidity'] = humidity

        pressure = barometer_bricklet.get_air_pressure() / 1000.0
        if 1090 < pressure < 920:
            weather_data['pressure'] = None
            logger.warn('Got pressure value of %s mbar which is out of range' % pressure)
        else:
            weather_data['pressure'] = pressure

        ipcon.disconnect()
        return weather_data

    except Exception as e:
        logger.error('Cloud not connect to weather sensors: %s' % str(e))
        return
