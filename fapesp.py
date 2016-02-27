#!/usr/bin/env python
# -*- coding: utf-8 -*-

import sys
import time
import datetime
import csv
import re
import click
import csv_utf8

import HTMLParser

from pprint import pprint

import requests

from lxml import html

import logging
logger = logging.getLogger()

# Setting up logger
logger.setLevel(logging.INFO)
ch = logging.StreamHandler(sys.stdout)
ch.setLevel(logging.INFO)
formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
ch.setFormatter(formatter)
logger.addHandler(ch)

class Fapesp():
    def __init__(self):
        # tabela.append([edicao, titulo + ': ' + subtitulo, publicacao, link, tags])
        # tabela2.append([edicao, titulo, subtitulo, publicacao, link, tags])

        self.publicacao = u'Revista Fapesp'

        self.tabela = []
        self.tabela2 = []

    def extract(self):
        url = u'http://revistapesquisa.fapesp.br/revista/edicoes-anteriores/'

        r = requests.get(url)

        if not r.text:
            logger.info(u'erro ao iniciar extração da revista fapesp, saindo...')
            return False

        pagina = r.text
        tree = html.fromstring(pagina)

        revistas = tree.xpath(u'//div[@class="printed_edition_tile"]/a')

        n = 0
        for revista in revistas:
            revista_edicao = revista.xpath(u'./div[@class="info"]/text()')[0].strip()
            revista_titulo = revista.xpath(u'./div[@class="title"]/text()')[0].strip()
            revista_url = revista.get(u'href').strip()

            print revista_edicao + u'\n' + revista_titulo + u'\n' + revista_url

            self.extract_reportagens(revista_url, revista_titulo, revista_edicao)

            print u'\n'
            n += 1

        logger.info(u'total de %d revistas' % n)


    def extract_reportagens(self, url, titulo, edicao):
        h = HTMLParser.HTMLParser()

        k = 0
        while True:
            try:
                r = requests.get(url)

                if not r.text:
                    logger.info(u'erro ao iniciar extração da revista fapesp, saindo...')
                    raise Exception(u'erro ao iniciar extração')

                break
            except Exception as e:
                logger.exception(u'erro ao pegar edição %s' % edicao)
                k += 1
                time.sleep(5)

                if k > 10:
                    logger.info(u'muitos erros ao iniciar extração da revista fapesp, saindo...')
                    return []

        try:
            pagina = r.text
            tree = html.fromstring(pagina)

            reportagens = tree.xpath(u'//a[@class="printed_edition_article_link"]')

            rep = dict()
            for reportagem in reportagens:
                rep = dict()

                rep[u'edicao'] = h.unescape(edicao)
                rep[u'tags'] = h.unescape([x.text_content() for x in reportagem.itersiblings(tag=u'h2', preceding=True)][0]).replace(u'AMP;', '').strip()
                rep[u'titulo'] = h.unescape(reportagem.xpath(u'./h3[@class="printed_edition_article_title"]')[0].text_content()).strip()
                rep[u'subtitulo'] = h.unescape(reportagem.xpath(u'./p[@class="printed_edition_article_excerpt"]')[0].text_content()).strip()
                rep[u'link'] = reportagem.get(u'href').strip()

                self.tabela.append([rep[u'edicao'], rep[u'titulo'], rep[u'subtitulo'], self.publicacao, rep[u'link'], rep[u'tags']])
                self.tabela2.append([rep[u'edicao'], re.sub(ur'\: $', u'', rep[u'titulo'] + ': ' + rep[u'subtitulo']), self.publicacao, rep[u'link'], rep[u'tags']])

        except Exception as e:
            logger.exception(u'erro durante scraping...')

        return True

    def extrai_salva(self):
        self.extract()

        with open('%s-%s.csv' % (self.publicacao, time.strftime(u'%Y-%m-%d')), 'wb') as myfile:
            wr = csv_utf8.UnicodeWriter(myfile, quoting=csv.QUOTE_ALL)
            wr.writerows(self.tabela)

        with open('%s-%s-ajustado.csv' % (self.publicacao, time.strftime(u'%Y-%m-%d')), 'wb') as myfile:
            wr = csv_utf8.UnicodeWriter(myfile, quoting=csv.QUOTE_ALL)
            wr.writerows(self.tabela2)

@click.group()
def cli():
    pass

@click.option('--inicio', help='Pagina de inicio', default=1)
@cli.command()
def extrai_fapesp(inicio):
    fapesp = Fapesp()
    fapesp.extrai_salva()

if __name__ == '__main__':
    cli()