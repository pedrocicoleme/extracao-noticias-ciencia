#!/usr/bin/env python
# -*- coding: utf-8 -*-

import sys
import time
import datetime
import csv
import regex
import click
import csv_utf8

import requests
import feedparser

import HTMLParser

import logging

logger = logging.getLogger()


# Setting up logger
logger.setLevel(logging.INFO)
logging.getLogger("requests").setLevel(logging.WARNING)
logging.getLogger("urllib3").setLevel(logging.WARNING)
ch = logging.StreamHandler(sys.stdout)
ch.setLevel(logging.INFO)
formatter = logging.Formatter(
    '%(asctime)s %(name)s [%(levelname)s] %(message)s')
ch.setFormatter(formatter)
logger.addHandler(ch)


def extract_rss(tabela, tabela2, nome, url, k=1):
    last_date = time.strftime(u'%Y-%m-%d')

    h = HTMLParser.HTMLParser()

    k = k - 1
    while k >= 0:
        k += 1

        try:
            r = requests.get(url + unicode(k), timeout=10)

            if r.status_code == requests.codes.not_found:
                logger.info(u'%s - acabaram as paginas', nome)

                k = -1

                break

            if r.status_code != requests.codes.ok:
                logger.info(
                    u'%s - erro ao pegar a pagina %s - %s',
                    nome, k, r.status_code)
                k -= 1

                time.sleep(10)

                continue
        except Exception as e:
            logger.info(u'%s - erro ao pegar a pagina %s', nome, k)

            logger.exception(e)

            k -= 1

            time.sleep(10)

            continue

        feed = feedparser.parse(r.text)

        if len(feed.entries) == 0:
            logger.info(u'%s - acabaram as paginas', nome)

            k = -1

            break

        for entry in feed.entries:
            date = time.strftime(u'%Y-%m-%d', entry.published_parsed)

            if datetime.datetime.strptime(
                date, '%Y-%m-%d') > datetime.datetime.strptime(
                    last_date, '%Y-%m-%d'):
                logger.info(u'%s - acabaram as paginas', nome)

                k = -1

                break

            last_date = date

            keywords = u''
            cat = u''
            try:
                if len(entry.tags) > 1:
                    keywords = u', '.join(
                        [x['term'] for x in entry.tags[1:]])

                cat = entry.tags[0]['term']
            except:
                pass

            if regex.search(
                (ur'(Institucional|Ex\-alunos|Artes|Vestibular|Especial'
                 ur'|Perfil|Gente da USP|Lazer e Entretenimento|Alunos|'
                 ur'Entrevista)'), cat, flags=regex.V1 | regex.I) is None:
                tabela.append([
                    time.strftime(u'%Y-%m-%d', entry.published_parsed),
                    h.unescape(entry.title) + ': ' +
                    h.unescape(entry.description),
                    u'Agencia USP' if nome == u'agenusp' else u'USP Online',
                    h.unescape(entry.link),
                    u', '.join([h.unescape(cat),
                                h.unescape(keywords)])])

                tabela2.append([
                    time.strftime(u'%Y-%m-%d', entry.published_parsed),
                    h.unescape(cat),
                    h.unescape(entry.title),
                    h.unescape(entry.description),
                    h.unescape(keywords),
                    h.unescape(entry.link)])

                # print u'%s - %s - %s - %s - %s' % (date,
                # entry.tags[0]['term'], entry.title, keywords, entry.link)

        logger.info(u'%s - pagina %d', nome, k)


def extrai_salva(nome, url, inicio):
    tabela = []
    tabela2 = []

    extract_rss(tabela, tabela2, nome, url, k=inicio)

    with open('%s-%s.csv' % (
            nome, time.strftime(u'%Y-%m-%d')), 'wb') as myfile:
        wr = csv_utf8.UnicodeWriter(myfile, quoting=csv.QUOTE_ALL)

        wr.writerows(tabela2)

    with open('%s-%s-ajustado.csv' % (
            nome, time.strftime(u'%Y-%m-%d')), 'wb') as myfile:
        wr = csv_utf8.UnicodeWriter(myfile, quoting=csv.QUOTE_ALL)

        wr.writerows(tabela)


@click.group()
def cli():
    pass


@click.option('--inicio', help='Pagina de inicio', default=1)
@cli.command()
def extrai_agenusp(inicio):
    extrai_salva(
        u'agenusp',
        u'http://www.usp.br/agen/?feed=rss2&cat=22,23,24,28,29,30,31&paged=',
        inicio)


@click.option('--inicio', help='Pagina de inicio', default=1)
@cli.command()
def extrai_usponline(inicio):
    extrai_salva(
        u'usponline',
        (u'http://www5.usp.br/feed/?category=ciencias,cultura,'
         u'educacao,meio-ambiente,pesquisa-noticias,saude-2,'
         u'sociedade,tecnologia-2&paged='),
        inicio)


@click.option('--inicio', help='Pagina de inicio', default=1)
@cli.command()
def extrai_tudo(inicio):
    extrai_agenusp(inicio)
    extrai_usponline(inicio)

if __name__ == '__main__':
    cli()
