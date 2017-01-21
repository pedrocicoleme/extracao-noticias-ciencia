# -*- coding: utf-8 -*-

import sys

import logging


def get_logger():
    logging.getLogger("requests").setLevel(logging.WARNING)
    logging.getLogger("urllib3").setLevel(logging.WARNING)

    formatter = logging.Formatter(
        '%(asctime)s[%(name)s][%(levelname)s]: %(message)s')

    ch = logging.StreamHandler(sys.stdout)
    ch.setFormatter(formatter)
    ch.setLevel(logging.INFO)

    logger = logging.getLogger()

    logger.setLevel(logging.INFO)
    logger.addHandler(ch)

    return logger
