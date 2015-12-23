#!/usr/bin/env python
# coding: utf8
from bottle import route, static_file
import random
import json
import subprocess
import logging
import requests
import wit

access_token = ""
logger = logging.getLogger("audiospeech_logger")


@route('/')
def index():
    return static_file('index.html', root='./audiospeech/web')


@route('/playsound/<file>')
def play_sound(file):
    subprocess.call("aplay ./audiospeech/sounds/" + file + ".wav", shell=True)
    return dict(status="OK")


@route('/recognize')
def speech_recognizer():
    wit.init()
    say("Ja?")
    response = wit.voice_query_auto(access_token)
    wit.close()
    try:
        intent = json.loads(response)
        evaluate_intent(intent['outcomes'][0]['intent'])
    except ValueError:
        say("Entschuldigung, ich habe das nicht verstanden")
        return dict(recognized_text="Could not recognize anything")

    return dict(recognized_intent=intent)


def say(text):
    subprocess.call('pico2wave --lang=de-DE --wave=/tmp/test.wav "' + text + '"; aplay /tmp/test.wav;rm /tmp/test.wav', shell=True)


# ---- EVALUATION ------------------------------------------------------------------------------------------
def evaluate_intent(intent):
    was_machen = ['Wir könnten heute ins Freibad oder Hallenbad gehen',
                  'Wir könnten heute Fahrrad fahren',
                  'Wir könnten heute ins Kino gehen',
                  'Wir könnten heute ganz viele Süßigkeiten essen',
                  'Wir könnte heute Fussball spielen',
                  'Wir könnten heute zocken']

    if intent == 'erste_bundesliga':
        requests.get('http://192.168.1.18:8080/soccerTable/1')
    elif intent == 'zweite_bundesliga':
        requests.get('http://192.168.1.18:8080/soccerTable/2')
    elif intent == 'was_machen':
        say(random.choice(was_machen))
    else:
        say("Diesen Befehl kenne ich nicht")
