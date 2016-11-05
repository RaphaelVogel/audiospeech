import requests
import logging, configparser

cfg = configparser.ConfigParser()
cfg.read('/home/pi/base/tools/config.txt')

logger = logging.getLogger("base_logger")


def send_message(message_type, message):
    try:
        if len(message) > 1024:
            return

        payload = {
            "token": cfg['pushover'][message_type],
            "user": cfg['pushover']['user'],
            "message": message
        }
        r = requests.post("https://api.pushover.net/1/messages.json", data=payload, timeout=5)
        if not r.status_code == requests.codes.ok:
            return

        return {'status': 'OK'}

    except Exception as e:
        logger.error('Cloud not send Pushover message: %s' % str(e))
        return
