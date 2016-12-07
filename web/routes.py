from bottle import route, static_file, HTTPResponse
from access_modules import solar, weather, pushover, alarmlog
import subprocess
import logging
import urllib
import requests
import configparser

cfg = configparser.ConfigParser()
cfg.read('/home/pi/base/tools/config.txt')

logger = logging.getLogger("base_logger")


@route('/')
def index():
    return static_file('index.html', root='/home/pi/base/web')


# ----------------------------------------------------------------------------------------------
# Solar and weather API
# ----------------------------------------------------------------------------------------------
@route('/solar/current')
def current_solarproduction():
    current_data = solar.read_data()  # returns a dictionary, will be transformed to JSON by bottle
    if current_data:
        return current_data
    else:
        return HTTPResponse(dict(error="Could not read solar production values"), status=500)


@route('/weather/current')
def current_weather():
    current_data = weather.read_data()
    if current_data:
        return current_data
    else:
        return HTTPResponse(dict(error="Could not read weather data values"), status=500)


# ----------------------------------------------------------------------------------------------
# Alarm control
# ----------------------------------------------------------------------------------------------
@route('/alarmOn')
def alarm_on():
    subprocess.call(["sudo", "systemctl", "start", "alarm.service"])
    # update the E Paper alarm display
    try:
        requests.get(cfg['ccu2']['update_alarm_on'], timeout=3)
    except Exception:
        pass
    return dict(status="OK")


@route('/alarmOff')
def alarm_off():
    subprocess.call(["sudo", "systemctl", "stop", "alarm.service"])
    # update the E Paper alarm display
    try:
        requests.get(cfg['ccu2']['update_alarm_off'], timeout=3)
    except Exception:
        pass
    return dict(status="OK")


@route('/alarmStatus')
def alarm_status():
    try:
        subprocess.check_call(["systemctl", "status", "alarm.service"])  # if $? is != 0 raises CalledProcessError
        return dict(status="an")
    except subprocess.CalledProcessError:
        return dict(status="aus")


@route('/alarmLog')
def alarm_log():
    log_data = alarmlog.get_log()
    if log_data:
        return log_data
    else:
        return HTTPResponse(dict(error="Could not read log data from alarm service"), status=500)


# ----------------------------------------------------------------------------------------------
# Pushover API
# ----------------------------------------------------------------------------------------------
@route('/pushOver/<message_type>/<message>')  # message_type = alarm | standard
def send_pushover_message(message_type, message):
    message = urllib.parse.unquote_plus(message)
    ret_value = pushover.send_message(message_type, message)  # returns a dictionary, will be transformed to JSON by bottle
    if ret_value:
        return ret_value
    else:
        return HTTPResponse(dict(error="Could not send pushover message"), status=500)
