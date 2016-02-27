#!/usr/bin/env python
# -*- coding: utf-8 -*-

import sys
import time
import datetime
import csv
import regex
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

class Canal_ciencia_ibict():
    def __init__(self):
        # tabela.append([edicao, titulo + ': ' + subtitulo, publicacao, link, tags])
        # tabela2.append([edicao, titulo, subtitulo, publicacao, link, tags])

        self.publicacao = u'Canal Ciencia - IBICT'
        self.url_base = u'http://www.canalciencia.ibict.br'

        self.tabela = []
        self.tabela2 = []

    def extract_from_pagination(self):
        url = u'http://www.canalciencia.ibict.br/pesquisa/pesquisascompletas.html?pager.offset='

        links = []

        k = 0
        while True:
            r = requests.get(url + unicode(k))

            if not r.text:
                logger.info(u'erro ao iniciar extração das noticias, saindo...')
                return False

            pagina = r.text
            tree = html.fromstring(pagina)

            links_c = tree.xpath(u'//div[@class="lista-links-mapa"]//a')

            if len(links_c) == 0:
                break

            for link_c in links_c:
                titulo = link_c.text.strip()
                link = self.url_base + link_c.get(u'href').strip()
                links.append([titulo, link])

            k += 15

        return links

    def extract(self):
        links = self.extract_from_pagination()

        # links = [[u'Caminhada de seis minutos ajuda a avaliar o risco de cirurgias cardíacas', u'http://www.canalciencia.ibict.br//pesquisa/0268-Caminhada-6-minutos-ajuda-avaliar-risco-cirurgia-cardiaca.html']]

        n = 0
        for link_l in links:
            r = requests.get(link_l[1])

            if not r.text:
                logger.info(u'erro ao iniciar extração das noticias, saindo...')
                return False

            pagina = r.text
            tree = html.fromstring(pagina)

            try:
                data_publicacao = tree.xpath(u'//*[(self::i or self::em) and contains(text(), "ublicado em")]/text()')[0]
                data_publicacao = regex.sub(ur'(Publicado em|Texto de divulgação científica publicado em) ', u'', data_publicacao)
            except:
                data_publicacao = u'sem data'

            try:
                subtitulo = tree.xpath(u'//h4[contains(text(), "Original da Pesquisa")]/following-sibling::p/text()')[0]
            except:
                subtitulo = u''

            titulo = link_l[0]
            link = link_l[1]
            categoria = u''

            print data_publicacao + u'\n' + titulo + u'\n' + subtitulo + u'\n' + link + u'\n'

            self.tabela.append([data_publicacao, titulo + ': ' + subtitulo, self.publicacao, link, categoria])
            self.tabela2.append([data_publicacao, titulo, subtitulo, self.publicacao, link, categoria])

            n += 1

        logger.info(u'total de %d notícias' % n)

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
def extrai_canal_ciencia_ibict(inicio):
    canal_ciencia_ibict = Canal_ciencia_ibict()
    canal_ciencia_ibict.extrai_salva()

if __name__ == '__main__':
    cli()