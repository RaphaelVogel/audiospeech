from bottle import route, static_file
import random
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


# ---- EVALUATION ------------------------------------------------------------------------------------------
def evaluate_text(text):
    was_machen = ['Wir könnten heute ins Freibad oder Hallenbad gehen',
                  'Wir könnten heute Fahrrad fahren',
                  'Wir könnten heute ins Kino gehen',
                  'Wir könnten heute ganz viele Süßigkeiten essen',
                  'Wir könnte heute Fussball spielen',
                  'Wir könnten heute Playstation spielen'
                  ]
    if 'zeig' in text and 'Uhr' in text:
        requests.get('http://192.168.1.18:8080/currentTime')
    elif 'zeig' in text and 'Bundesliga' in text and 'Tabelle' in text:
        requests.get('http://192.168.1.18:8080/soccerTable/1')
    elif 'zeig' in text and 'Bundesliga' in text and 'Tabelle' in text and 'zweite' in text:
        requests.get('http://192.168.1.18:8080/soccerTable/2')
    elif 'was sollen' in text and 'machen' in text:
        say(random.choice(was_machen))
    else:
        say("Diesen Befehl kenne ich nicht")
