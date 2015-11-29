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
    response = subprocess.check_output('arecord -D plughw:0,0 -f cd -t wav -d 4 -q -r 16000 | flac - -s -f --best --sample-rate 16000 -o file.flac; && '
        'wget -q -U "Mozilla/5.0" --post-file file.flac --header "Content-Type: audio/x-flac; rate=16000" -O - '
        '"https://www.google.com/speech-api/v2/recognize?output=json&lang=de-de&key=AIzaSyDkxrlx2acbRLILXVU9_UgnRqUXLcfRoWs" && '
        'rm file.flac  > /dev/null 2>&1', shell=True)
    print("Answer: ", response)
