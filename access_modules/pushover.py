import requests
import logging, configparser

cfg = configparser.ConfigParser()
cfg.read('/home/pi/base/tools/config.txt')

logger = logging.getLogger("base_logger")


# message_type = alarm | standard
# message = unquoted message string
def send_message(message_type, message):
    try:
        if len(message) > 1024:
            return

        payload = {
            "token": cfg['pushover'][message_type],
            "user": cfg['pushover']['user'],
            "message": message
        }
        # requests.post() will quote message automatically
        r = requests.post("https://api.pushover.net/1/messages.json", data=payload, timeout=5)
        if not r.status_code == requests.codes.ok:
            return

        return {'status': 'OK'}

    except Exception as e:
        logger.error('Cloud not send Pushover message: %s' % str(e))
        return
