import os
import logging
import logging.handlers
import sys
import time


logger = logging.getLogger("rcmproxy.log")


def logging_config():
    root_logger = logging.getLogger()

    if os.environ.get("RCBOARD_LOG_STDOUT", "true").lower() == "true":
        stdout_handler = logging.StreamHandler(sys.stdout)
        stdout_fmt = logging.Formatter(
            "%(asctime)s.%(msecs)03dZ %(levelname)-8s %(name)s %(message)s",
            datefmt="%Y-%m-%dT%H:%M:%S",
        )
        stdout_fmt.converter = time.gmtime
        stdout_handler.setFormatter(stdout_fmt)
        stdout_handler.setLevel(os.environ.get("RCBOARD_LOG_STDOUT_LEVEL", "INFO"))

        root_logger.addHandler(stdout_handler)

    if os.environ.get("RCBOARD_LOG_FILE", "true").lower() == "true":
        file_handler = logging.handlers.TimedRotatingFileHandler(
            "log/rcmproxy.log", when="m", interval=30
        )
        file_handler.setFormatter(stdout_fmt)
        file_handler.setLevel(os.environ.get("RCBOARD_LOG_FILE_LEVEL", "DEBUG"))

        root_logger.addHandler(file_handler)

    root_logger.setLevel(logging.DEBUG)

    module_logger = logging.getLogger("rcmproxy")
    module_logger.setLevel(logging.DEBUG)

    logger.info("Logging configured")
