#!/usr/bin/env python
# coding: utf8
from bottle import route, static_file
import random
import json
import subprocess
import logging
import requests
import time
import wit

access_token = ""
logger = logging.getLogger("audiospeech_logger")

was_machen = ['Wir könnten heute ins Freibad oder Hallenbad gehen',
              'Wir könnten heute Fahrrad fahren',
              'Wir könnten heute ins Kino gehen',
              'Wir könnten heute ganz viele Süßigkeiten essen',
              'Wir könnte heute Fussball spielen',
              'Die Kinder sollten heute ihr Zimmer aufräumen',
              'Die Kinder können jetzt Mathe und Deutsch üben',
              'Wir könnten jetzt Fernsehen schauen']

radio = 1


@route('/')
def index():
    return static_file('index.html', root='./audiospeech/web')


@route('/playsound/<file>')
def play_sound(file):
    subprocess.call("aplay ./audiospeech/sounds/" + file + ".wav", shell=True)
    return dict(status="OK")


@route('/playRadio')
def play_radio():
    global radio
    subprocess.call("mpc play " + str(radio), shell=True)
    radio += 1
    if radio > 4:
        radio = 1


@route('/stopRadio')
def stop_radio():
    subprocess.call("mpc stop", shell=True)


@route('/increaseVolume')
def stop_radio():
    subprocess.call("mpc volume +10", shell=True)


@route('/decreaseVolume')
def stop_radio():
    subprocess.call("mpc volume -10", shell=True)


@route('/recognize')
def speech_recognizer():
    intent = None
    try:
        wit.init()
        say("Ja?")
        wit.voice_query_start(access_token)
        time.sleep(3)
        response = wit.voice_query_stop()
        wit.close()
        intent = json.loads(response)
        evaluate_intent(intent['outcomes'][0]['intent'], intent['outcomes'][0]['confidence'],
                        intent['outcomes'][0]['entities'])
    except Exception as e:
        logger.error("Response: " + str(intent))
        logger.error("Got exception: " + str(e))
        say("Entschuldigung, ich habe das nicht verstanden")
        return dict(recognized_text="Could not recognize anything")

    return dict(recognized_intent=intent)


def say(text):
    subprocess.call('pico2wave --lang=de-DE --wave=/tmp/test.wav "' + text + '"; aplay /tmp/test.wav;rm /tmp/test.wav', shell=True)


# ---- EVALUATION ------------------------------------------------------------------------------------------
def evaluate_intent(intent, confidence, entities):
    if entities:
        entity_name = entities.keys()[0]
        value = entities[entity_name][0]['value']
    if float(confidence) < 0.6 or intent == "UNKNOWN":
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
    elif intent == 'reminder':
        requests.get('http://192.168.1.18:8080/currentTime')
        if value == "1":
            say("Ok, Alarm in einer Minute")
        else:
            say("Ok, Alarm in " + value + " Minuten")
    else:
        say("Diesen Befehl kenne ich nicht")
