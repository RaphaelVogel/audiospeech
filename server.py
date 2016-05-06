#!/usr/bin/python3
import sys
import logging
from logging.handlers import RotatingFileHandler
from bottle import run
import web.routes
import time
from threading import Timer
import subprocess


# logger configuration
logger = logging.getLogger("base_logger")
logger.setLevel(logging.WARN)
filehandler = RotatingFileHandler('/home/pi/base/log.txt', maxBytes=100000, backupCount=2)
formatter = logging.Formatter('%(asctime)s : %(levelname)s : %(message)s', datefmt='%d-%m-%Y %H:%M:%S')
filehandler.setFormatter(formatter)
logger.addHandler(filehandler)


if __name__ == '__main__':
    if len(sys.argv) > 1 and sys.argv[1] == 'devmode':
        run(server='cherrypy', host='localhost', port=8080, debug=True, reloader=True)
    else:
        run(server='cherrypy', host='0.0.0.0', port=8080, debug=False, reloader=False)
