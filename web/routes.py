from bottle import route, static_file, HTTPResponse
from access_modules import solar, weather
import subprocess
import logging


logger = logging.getLogger("base_logger")
radio = 1


# ------------------------------------------------------------------------------------------
# Sound, Radio and Speech Recognition API
# ------------------------------------------------------------------------------------------
@route('/')
def index():
    return static_file('index.html', root='/home/pi/base/web')


@route('/playsound/<file>')
def play_sound(file):
    stop_radio()
    filename = "/home/pi/base/sounds/" + file + ".wav"
    subprocess.call(["aplay", filename])
    return dict(status="OK")


@route('/playRadio')
def play_radio():
    global radio
    if radio > 6:
        radio = 1
    out = subprocess.check_output("mpc play " + str(radio), shell=True)
    out = out.split(b'\n')[0].decode('utf-8')
    radio += 1
    if "hr3" in out:
        say("H, R, 3")
    elif "SWR3" in out:
        say("S, W, R, 3")
    elif "SWR1" in out:
        say("S, W, R, 1")
    elif "SWR2" in out:
        say("S, W, R, 2")
    elif "Bayern 3" in out:
        say("Bayern, 3")
    elif "DASDING" in out:
        say("Das Ding")

    return dict(playing=out)


@route('/stopRadio')
def stop_radio():
    subprocess.call(["mpc", "stop"])
    return dict(status="OK")


@route('/increaseVolume')
def increase_volume():
    subprocess.call(["mpc", "volume", "+10"])
    return dict(status="OK")


@route('/decreaseVolume')
def decrease_volume():
    subprocess.call(["mpc", "volume", "-10"])
    return dict(status="OK")


# ----------------------------------------------------------------------------------------------
# Solar and weather API
# ----------------------------------------------------------------------------------------------
@route('/solar/current')
def current_solarproduction():
    current_data = solar.read_data(False)  # returns a dictionary, will be transformed to JSON by bottle
    if current_data:
        return current_data
    else:
        return HTTPResponse(dict(error="Could not read solar production values"), status=500)


@route('/weather/current')
def current_weather():
    current_data = weather.read_data(False)
    if current_data:
        return current_data
    else:
        return HTTPResponse(dict(error="Could not read weather data values"), status=500)


# ----------------------------------------------------------------------------------------------
# Functions
# ----------------------------------------------------------------------------------------------
def say(text):
    subprocess.call(["amixer", "sset", "PCM,0", "75%"])
    subprocess.call('pico2wave --lang=de-DE --wave=/tmp/test.wav "' + text + '" && aplay /tmp/test.wav && rm /tmp/test.wav', shell=True)
    subprocess.call(["amixer", "sset", "PCM,0", "60%"])
