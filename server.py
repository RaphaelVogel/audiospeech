#!/usr/bin/env python
# coding: utf8
import sys
import logging
from logging.handlers import RotatingFileHandler
from bottle import run
import web.routes
import time
from threading import Timer
import subprocess


# logger configuration
logger = logging.getLogger("audiospeech_logger")
logger.setLevel(logging.WARN)
filehandler = RotatingFileHandler('./audiospeech/log.txt', maxBytes=100000, backupCount=2)
formatter = logging.Formatter('%(asctime)s : %(levelname)s : %(message)s', datefmt='%d-%m-%Y %H:%M:%S')
filehandler.setFormatter(formatter)
logger.addHandler(filehandler)


def reset_mpd():
    subprocess.call(["sudo", "service", "mpd", "restart"])
    Timer(10800.0, reset_mpd).start()  # 3h


if __name__ == '__main__':
    reset_mpd()
    if len(sys.argv) > 1 and sys.argv[1] == 'devmode':
        run(server='cherrypy', host='localhost', port=8080, debug=True, reloader=True)
    else:
        run(server='cherrypy', host='0.0.0.0', port=8080, debug=False, reloader=False)
