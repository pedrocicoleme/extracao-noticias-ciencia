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

class Divulga_ciencia_ufsc():
    def __init__(self):
        # tabela.append([edicao, titulo + ': ' + subtitulo, publicacao, link, tags])
        # tabela2.append([edicao, titulo, subtitulo, publicacao, link, tags])

        self.publicacao = u'Divulga Ciencia - UFSC'
        self.url_base = u'http://noticias.ufsc.br/tags/divulga-ciencia/'

        self.tabela = []
        self.tabela2 = []

    def extract_edicoes(self):
        url = u'http://noticias.ufsc.br/tags/divulga-ciencia/'

        edicoes = []

        r = requests.get(url)

        if not r.text:
            logger.info(u'erro ao iniciar extração das noticias, saindo...')
            return edicoes

        pagina = r.text
        tree = html.fromstring(pagina)

        edicoes_c = tree.xpath(u'//div[@class="entry-head"]//a')

        for edicao in edicoes_c:
            edicoes.append(edicao.get(u'href').strip())

        return edicoes

    def extract(self):
        edicoes = self.extract_edicoes()

        n = 0
        k = 0
        for edicao in edicoes:
            print edicao

            r = requests.get(edicao)

            if not r.text:
                logger.info(u'erro ao iniciar extração das noticias, saindo...')
                return False

            pagina = r.text
            tree = html.fromstring(pagina)

            data_publicacao = tree.xpath(u'//div[@class="entry-head-info"]/text()')[0]
            m = regex.search(ur'([0-9]{2}/[0-9]{2}/[0-9]{4})', data_publicacao)

            if m != None:
                data_publicacao = m.group(1)

            noticias = tree.xpath(u'//div[@class="entry"]/p//span[@style="font-size: medium;color: #000080" or @style="font-size: medium; color: #000080;" or @style="font-size: medium; color: #0b5521;"]/strong')

            for noticia in noticias:
                categoria = u''

                try:
                    titulo = noticia.xpath(u'./text()')[0].strip()
                    subtitulo_c = noticia.xpath(u'./ancestor::p/following-sibling::p/span')[0]
                except Exception as e:
                    try:
                        titulo = noticia.xpath(u'./span/strong/text()')[0].strip()
                        subtitulo_c = noticia.xpath(u'./ancestor::p/following-sibling::p/span')[0]
                    except Exception as e2:
                        # logger.exception('erro ao procurar pelo titulo')
                        continue

                if len(titulo) < 1:
                    continue

                subtitulo = subtitulo_c.text_content().strip()
                try:
                    link = subtitulo_c.xpath(u'./a')[-1].get(u'href').strip()
                    subtitulo = regex.sub(ur'%s[\s.]*$' % subtitulo_c.xpath(u'./a')[-1].text_content(), u'', subtitulo).strip()
                except:
                    link = edicao

                print data_publicacao + u'\n' + titulo + u'\n' + subtitulo + u'\n' + self.url_base + link + u'\n' + categoria

                self.tabela.append([data_publicacao, titulo + ': ' + subtitulo, self.publicacao, link, categoria])
                self.tabela2.append([data_publicacao, titulo, subtitulo, self.publicacao, link, categoria])

                print u'\n'
                n += 1

            k += 1

        logger.info(u'total de %d notícias em %d edições' % (n, k))

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
def extrai_divulga_ciencia_ufsc(inicio):
    divulga_ciencia_ufsc = Divulga_ciencia_ufsc()
    divulga_ciencia_ufsc.extrai_salva()

if __name__ == '__main__':
    cli()