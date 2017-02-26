# -*- coding: utf-8 -*-

import sys
import time
import logging
import csv

import requests.packages.urllib3

import csv_utf8


def get_logger():
    logging.getLogger("requests").setLevel(logging.ERROR)
    logging.getLogger("urllib3").setLevel(logging.ERROR)

    requests.packages.urllib3.disable_warnings()

    formatter = logging.Formatter(
        '%(asctime)s[%(name)s][%(levelname)s]: %(message)s')

    ch = logging.StreamHandler(sys.stdout)
    ch.setFormatter(formatter)
    ch.setLevel(logging.INFO)

    logger = logging.getLogger()

    logger.setLevel(logging.INFO)
    logger.addHandler(ch)

    return logger


def salva_tabelas(nome, tabela, tabela2):
    with open('./data/%s-%s.csv' % (
            nome, time.strftime(u'%Y-%m-%d')), 'wb') as myfile:
        wr = csv_utf8.UnicodeWriter(myfile, quoting=csv.QUOTE_ALL)

        wr.writerows(tabela)

    with open('./data/%s-%s-ajustado.csv' % (
            nome, time.strftime(u'%Y-%m-%d')), 'wb') as myfile:
        wr = csv_utf8.UnicodeWriter(myfile, quoting=csv.QUOTE_ALL)

        wr.writerows(tabela2)
