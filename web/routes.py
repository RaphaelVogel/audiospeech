#!/usr/bin/env python
# coding: utf8
from bottle import route, static_file, HTTPResponse
from access_modules import solar, weather
import random
import json
import subprocess
import logging
import requests
import time
import wit


@route('/')
def index():
    return static_file('index.html', root='/home/pi/base/web')


# ------------------------------------------------------------------------------------------
# Sound, Radio and Speech Recognition API
# ------------------------------------------------------------------------------------------
access_token = ""
logger = logging.getLogger("base_logger")

was_machen = ['Wir könnten heute ins Freibad oder Hallenbad gehen',
              'Wir könnten heute Fahrrad fahren',
              'Wir könnten heute ins Kino gehen',
              'Wir könnten heute ganz viele Süßigkeiten essen',
              'Wir könnte heute Fussball spielen',
              'Die Kinder sollten heute ihr Zimmer aufräumen',
              'Die Kinder können jetzt Mathe und Deutsch üben',
              'Wir könnten jetzt Fernsehen schauen']
radio = 1


@route('/playsound/<file>')
def play_sound(file):
    filename = "/home/pi/base/sounds/" + file + ".wav"
    subprocess.call(["aplay", filename])
    return dict(status="OK")


# http://hr-mp3-m-h3.akacast.akamaistream.net/7/785/142133/v1/gnl.akacast.akamaistream.net/hr-mp3-m-h3
# http://swr-mp3-m-swr3.akacast.akamaistream.net/7/720/137136/v1/gnl.akacast.akamaistream.net/swr-mp3-m-swr3
# http://swr-mp3-m-swr2.akacast.akamaistream.net/7/721/137135/v1/gnl.akacast.akamaistream.net/swr-mp3-m-swr2
# http://mp3.ffh.de/radioffh/hqlivestream.mp3
# http://srv05.bigstreams.de/bigfm-mp3-96
# http://217.151.151.91:80/live
@route('/playRadio')
def play_radio():
    global radio
    if radio > 6:
        radio = 1
    subprocess.call("mpc -q play " + str(radio), shell=True)
    radio += 1
    return dict(status="OK", playing=str(radio - 1))


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


@route('/recognize')
def speech_recognizer():
    logger.info("In speech_recognizer method")
    stop_radio()
    try:
        wit.init()
        say("Ja?")
        wit.voice_query_start(access_token)
        time.sleep(3)
        response = wit.voice_query_stop()
        wit.close()
        intent = json.loads(response)
        evaluate_speech_intent(intent['outcomes'][0]['intent'], intent['outcomes'][0]['confidence'],
                               intent['outcomes'][0]['entities'])
    except Exception as e:
        logger.error("Got exception: %s", str(e))
        say("Entschuldigung, ich habe das nicht verstanden")
        return dict(recognized_text="Could not recognize anything")

    return dict(recognized_intent=intent)


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
    subprocess.call(["amixer", "sset", "PCM,0", "50%"])


def evaluate_speech_intent(intent, confidence, entities):
    logger.info("In evaluate_intent: %s  %s  %s", str(intent), str(confidence), str(entities))
    if entities:
        entity_name = entities.keys()[0]
        value = entities[entity_name][0]['value']
    if float(confidence) < 0.6 or intent == "UNKNOWN":
        logger.info("Confidence %s smaller than 0.6", confidence)
        say("Diesen Befehl kenne ich nicht")
        return
    if intent == 'erste_bundesliga':
        requests.get('http://192.168.1.18:8080/soccerTable/1')
    elif intent == 'zweite_bundesliga':
        requests.get('http://192.168.1.18:8080/soccerTable/2')
    elif intent == 'was_machen':
        global was_machen
        say(random.choice(was_machen))
    elif intent == 'dein_name':
        say("Ich bin Prinzessin Lea")
    elif intent == "bild_des_tages":
        requests.get('http://192.168.1.18:8080/picOfTheDay')
    elif intent == "radio_an":
        play_radio()
    elif intent == "radio_lauter":
        increase_volume()
    elif intent == "radio_leiser":
        decrease_volume()
    else:
        logger.info("Intent %s is nor known", intent)
        say("Diesen Befehl kenne ich nicht")
