from bottle import route, static_file, request, HTTPResponse
from threading import Thread
import json
import subprocess
import logging
import requests

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
    say("Ja?")
    subprocess.call('. ./audiospeech/recognize_speech.sh', shell=True)
    with open("./audiospeech/stt.txt") as f:
        out = f.read()
    try:
        response = out.split('\n', 1)
        text = json.loads(response[1])['result'][0]['alternative'][0]['transcript']
        evaluate_text(text)
    except ValueError:
        say("Entschuldigung, ich habe das nicht verstanden")
        return dict(recognized_text="Could not recognize anything")

    return dict(recognized_text=text)


def say(text):
    subprocess.call('pico2wave --lang=de-DE --wave=/tmp/test.wav "' + text + '"; aplay /tmp/test.wav;rm /tmp/test.wav', shell=True)


def evaluate_text(text):
    if 'zeig' in text and 'Uhr' in text:
        requests.get('http://192.168.1.18:8080/currentTime')
    if 'zeig' in text and 'Bundesliga' in text and 'Tabelle' in text:
        requests.get('http://192.168.1.18:8080/soccerTable/1')
    if 'zeig' in text and 'Bundesliga' in text and 'Tabelle' in text and 'zweite' in text:
        requests.get('http://192.168.1.18:8080/soccerTable/2')
