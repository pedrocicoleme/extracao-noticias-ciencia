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

from lxml import etree as ET
def pp(e):
    print ET.tostring(e, pretty_print=True)
    print

class Ciencia_e_cultura():
    def __init__(self):
        # tabela.append([edicao, titulo + ': ' + subtitulo, publicacao, link, tags])
        # tabela2.append([edicao, titulo, subtitulo, publicacao, link, tags])

        self.publicacao = u'Ciencia e Cultura - SBPC'
        self.url_base = u'http://cienciaecultura.bvs.br'

        self.tabela = []
        self.tabela2 = []

    def extract_edicoes(self):
        url = u'http://cienciaecultura.bvs.br/scielo.php?script=sci_issues&pid=0009-6725&lng=pt&nrm=iso'

        links = []

        r = requests.get(url)

        if not r.text:
            logger.info(u'erro ao iniciar extração das edições, saindo...')
            return []

        pagina = r.text
        tree = html.fromstring(pagina)

        edicoes_c = tree.xpath(u'//div[@class="content"]//td/b/font/a')

        n = 0
        for edicao_c in edicoes_c:
            links.append(edicao_c.get(u'href'))

        pprint(links)

        return links

    def extract(self):
        urls = self.extract_edicoes()

        n = 0
        for url in urls:
            r = requests.get(url)

            if not r.text:
                logger.info(u'erro ao iniciar extração das noticias, saindo...')
                return False

            pagina = r.text
            tree = html.fromstring(pagina)

            edicao = tree.xpath(u'//p/font[contains(text(), "Cienc. Cult.")]')[0].text_content()

            blocos = tree.xpath(u'//div[@class="content"]/table/tbody/tr/td/table/tbody/tr[position()>1]/td')

            categoria = u''
            
            for bloco in blocos:
                if bloco.get(u'class') != None:
                    if bloco.get(u'class').find(u'section') != -1:
                        categoria = bloco.text_content().strip()

                    continue
                elif bloco.text_content() != u'&nbsp;':
                    try:
                        titulo = bloco.xpath(u'./font[2]')[0].text_content().strip()

                        link = bloco.xpath(u'./div/a')[0].get(u'href').strip()
                    except:
                        #logger.exception(u'erro ao pegar noticia')
                        continue
                else:
                    continue

                print edicao + u'\n' + titulo + u'\n' + link + u'\n' + categoria + u'\n'

                self.tabela.append([edicao, titulo, self.publicacao, link, categoria])
                self.tabela2.append([edicao, titulo, u'', self.publicacao, link, categoria])

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
def extrai_ciencia_e_cultura(inicio):
    ciencia_e_cultura = Ciencia_e_cultura()
    ciencia_e_cultura.extrai_salva()

if __name__ == '__main__':
    cli()