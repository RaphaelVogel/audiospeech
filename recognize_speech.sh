#!/bin/bash

KEY="AIzaSyDkxrlx2acbRLILXVU9_UgnRqUXLcfRoWs"
URL="https://www.google.com/speech-api/v2/recognize?output=json&lang=de-de&key=$KEY"

arecord -D plughw:0,0 -f cd -t wav -d 3 -q -r 8000 | flac - -s -f --best --sample-rate 8000 -o ./audiospeech/file.flac;

wget -q -U "Mozilla/5.0" --post-file ./audiospeech/file.flac --header "Content-Type: audio/x-flac; rate=8000" -O - "$URL" >./audiospeech/stt.txt
