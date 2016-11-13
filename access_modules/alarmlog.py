import logging
import subprocess

logger = logging.getLogger("base_logger")


def get_log():
    try:
        out = subprocess.check_output("tail -n 20 /home/pi/base/logs/alarm_log.txt", shell=True)
        # convert from bytestring to UTF-8 string
        out = str(out, encoding='UTF-8')
        return {'alarm_logs': out}

    except Exception as e:
        logger.error('Could not read alarm log: %s' % str(e))
        return