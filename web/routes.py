from bottle import route, static_file, request, HTTPResponse
import json
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
    response = json.loads(out).split('\n', 1)
    if len(response) <= 1:
        return dict(text="Could not recognize")
    text = json.loads(response[1])['result'][0]['alternative'][0]['transcript']
    return dict(text="text")
