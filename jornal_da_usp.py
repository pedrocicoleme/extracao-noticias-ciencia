#!/usr/bin/env python
# -*- coding: utf-8 -*-

import time
import csv

import HTMLParser
import csv_utf8
import requests
import feedparser
import click

import helpers


logger = helpers.get_logger()


def extract_rss(tabela, tabela2):
    url = u'http://jornal.usp.br/editorias/ciencias/feed/?paged='

    h = HTMLParser.HTMLParser()

    k = 0
    while k >= 0:
        k += 1

        try:
            res = requests.get(url + unicode(k), timeout=20)

            if res.status_code == requests.codes.not_found:
                logger.info(u'jornal_da_usp - acabaram as paginas')

                k = -1

                break

            if res.status_code != requests.codes.ok:
                logger.info(
                    u'jornal_da_usp - erro ao pegar a pagina %s - %s',
                    k, res.status_code)
                k -= 1

                time.sleep(10)

                continue
        except Exception as e:
            logger.info(u'jornal_da_usp - erro ao pegar a pagina %s', k)

            logger.exception(e)

            k -= 1

            time.sleep(10)

            continue

        feed = feedparser.parse(res.text)

        if len(feed.entries) == 0:
            logger.info(u'jornal_da_usp - acabaram as paginas')

            k = -1

            break

        for entry in feed.entries:
            cats = [x['term'] for x in entry.tags]

            if cats[0] == u'Ciências Humanas' or u'Colunistas' in cats:
                continue

            tabela.append([
                time.strftime(u'%Y-%m-%d', entry.published_parsed),
                h.unescape(entry.title) + ': ' +
                h.unescape(entry.description),
                u'Jornal da USP',
                h.unescape(entry.link),
                h.unescape(u', '.join(cats))])

            tabela2.append([
                time.strftime(u'%Y-%m-%d', entry.published_parsed),
                h.unescape(cats[0]),
                h.unescape(entry.title),
                h.unescape(entry.description),
                h.unescape(u''.join(cats[1:])),
                h.unescape(entry.link)])

        logger.info(u'jornal_da_usp - pagina %d', k)

def extrai_salva():
    tabela = []
    tabela2 = []

    extract_rss(tabela, tabela2)

    nome = u'jornal_da_usp'

    with open('./data/%s-%s.csv' % (
            nome, time.strftime(u'%Y-%m-%d')), 'wb') as myfile:
        wr = csv_utf8.UnicodeWriter(myfile, quoting=csv.QUOTE_ALL)

        wr.writerows(tabela2)

    with open('./data/%s-%s-ajustado.csv' % (
            nome, time.strftime(u'%Y-%m-%d')), 'wb') as myfile:
        wr = csv_utf8.UnicodeWriter(myfile, quoting=csv.QUOTE_ALL)

        wr.writerows(tabela)


@click.group()
def cli():
    pass


@click.option('--inicio', help='Pagina de inicio', default=1)
@cli.command()
def extrai(inicio):
    extrai_salva()


if __name__ == '__main__':
    cli()
