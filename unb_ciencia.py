#!/usr/bin/env python
# -*- coding: utf-8 -*-

import time
import csv
import regex
import click
import csv_utf8

import requests

from lxml import html

import helpers


logger = helpers.get_logger()


class Unb_ciencia():

    def __init__(self):
        # tabela.append([edicao, titulo + ': ' + subtitulo, publicacao, link, tags])
        # tabela2.append([edicao, titulo, subtitulo, publicacao, link, tags])

        self.publicacao = u'Unb Ciencia'
        self.url_base = u'http://www.unbciencia.unb.br'

        self.tabela = []
        self.tabela2 = []

    def extract(self):
        # http://www.unbciencia.unb.br/index.php?option=com_alphacontent&view=alphacontent&Itemid=2&limitstart=0&limit=0

        url = u'http://www.unbciencia.unb.br/index.php?option=com_alphacontent&view=alphacontent&Itemid=2&limitstart=0&limit=0'

        r = requests.get(url)

        if not r.text:
            logger.info(u'erro ao iniciar extração das noticias, saindo...')
            return False

        pagina = r.text
        tree = html.fromstring(pagina)

        noticias = tree.xpath(u'//div[@class="alphalisting"]')

        n = 0
        for noticia in noticias:
            categoria = noticia.xpath(
                u'.//span[@class="chapeuverdecx"]/text()')[0].strip()
            data_publicacao = noticia.xpath(
                u'.//span[@class="datafina"]/text()')[0].split(u',', 1)[1].strip()

            link_c = noticia.xpath(u'.//span[@class="_alphatitle"]/a')[0]
            titulo = link_c.text.strip()
            link = link_c.get(u'href').strip()

            # regex.sub(ur'^%s' % categoria,    , u'', regex.IGNORECASE)
            subtitulo = regex.sub(ur'[\n\r\s]{1,}', u' ', noticia.xpath(
                u'.//div[@id="content"]/text()')[0]).strip()
            subtitulo = regex.sub(
                ur'^((\p{Lu}){2,}[\s\n\r]*){1,}', u'', subtitulo, regex.UNICODE)

            print data_publicacao + u'\n' + titulo + u'\n' + subtitulo + u'\n' + self.url_base + link + u'\n' + categoria

            self.tabela.append([data_publicacao, titulo + ': ' + subtitulo,
                                self.publicacao, self.url_base + link, categoria])
            self.tabela2.append([data_publicacao, titulo, subtitulo,
                                 self.publicacao, self.url_base + link, categoria])

            print u'\n'
            n += 1

        logger.info(u'total de %d notícias' % n)

    def extrai_salva(self):
        self.extract()

        with open('./data/%s-%s.csv' % (self.publicacao, time.strftime(u'%Y-%m-%d')), 'wb') as myfile:
            wr = csv_utf8.UnicodeWriter(myfile, quoting=csv.QUOTE_ALL)
            wr.writerows(self.tabela)

        with open('./data/%s-%s-ajustado.csv' % (self.publicacao, time.strftime(u'%Y-%m-%d')), 'wb') as myfile:
            wr = csv_utf8.UnicodeWriter(myfile, quoting=csv.QUOTE_ALL)
            wr.writerows(self.tabela2)


@click.group()
def cli():
    pass


@click.option('--inicio', help='Pagina de inicio', default=1)
@cli.command()
def extrai_unb_ciencia(inicio):
    unb_ciencia = Unb_ciencia()
    unb_ciencia.extrai_salva()

if __name__ == '__main__':
    cli()
