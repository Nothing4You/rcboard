import logging
import logging.handlers
import sys
import time


logger = logging.getLogger("rcmproxy.log")


def logging_config():
    root_logger = logging.getLogger()

    stdout_handler = logging.StreamHandler(sys.stdout)
    stdout_fmt = logging.Formatter("%(asctime)s %(levelname)-8s %(name)s %(message)s", datefmt="%Y-%m-%dT%H:%M:%SZ")
    stdout_fmt.converter = time.gmtime
    stdout_handler.setFormatter(stdout_fmt)
    stdout_handler.setLevel(logging.INFO)

    file_handler = logging.handlers.TimedRotatingFileHandler("log/rcmproxy.log", when="m", interval=30)
    file_handler.setLevel(logging.DEBUG)
    file_handler.setFormatter(stdout_fmt)

    root_logger.addHandler(stdout_handler)
    root_logger.addHandler(file_handler)
    root_logger.setLevel(logging.DEBUG)

    module_logger = logging.getLogger("rcmproxy")
    module_logger.setLevel(logging.DEBUG)

    logger.info("Logging configured")
