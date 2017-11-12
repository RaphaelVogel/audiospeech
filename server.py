import sys
import logging
from logging.handlers import RotatingFileHandler
from bottle import run
import web.routes
import subprocess
import signal

# logger configuration
logger = logging.getLogger("base_logger")
logger.setLevel(logging.INFO)
filehandler = RotatingFileHandler('/home/pi/base/logs/base_log.txt', maxBytes=100000, backupCount=2)
formatter = logging.Formatter('%(asctime)s : %(levelname)s : %(message)s', datefmt='%d-%m-%Y %H:%M:%S')
filehandler.setFormatter(formatter)
logger.addHandler(filehandler)


def signal_handler(signal_type, frame):
    logger.info("Base Webserver stopped")
    sys.exit(0)


if __name__ == '__main__':
    signal.signal(signal.SIGTERM, signal_handler)
    logger.info("Base Webserver started")
    if len(sys.argv) > 1 and sys.argv[1] == 'devmode':
        run(server='cherrypy', host='localhost', port=8080, debug=True, reloader=True)
    else:
        run(server='cherrypy', host='0.0.0.0', port=8080, debug=False, reloader=False)
