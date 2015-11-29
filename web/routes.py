from bottle import route, static_file, request, HTTPResponse
import random
import subprocess


@route('/')
def index():
    return static_file('index.html', root='./audiospeech/web')


@route('/playsound/<file>')
def play_sound(file):
    subprocess.call("aplay ./audiospeech/sounds/" + file + ".wav", shell=True)
    return dict(status="OK")


@route('/recognize')
def speech_recognizer():
    subprocess.call('. ./audiospeech/recognize_speech.sh', shell=True)
    with open("./audiospeech/stt.txt") as f:
        out = f.read()

    return dict(recognized=out)
