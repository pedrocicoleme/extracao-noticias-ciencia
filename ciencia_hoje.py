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

class Ciencia_hoje():
    def __init__(self):
        # tabela.append([edicao, titulo + ': ' + subtitulo, publicacao, link, tags])
        # tabela2.append([edicao, titulo, subtitulo, publicacao, link, tags])

        self.publicacao = u'Ciencia Hoje'
        self.url_base = u'http://cienciahoje.uol.com.br'

        self.tabela = []
        self.tabela2 = []

    def extract_noticia(self, link):
        r = requests.get(link[1])

        if not r.text:
            logger.info(u'erro ao iniciar extração das noticias, saindo...')
            return False

        pagina = r.text
        tree = html.fromstring(pagina)

        try:
            titulo = tree.xpath(u'//span[@id="parent-fieldname-title"]/text()')[0].strip()
            subtitulo = tree.xpath(u'//span[@id="parent-fieldname-description"]/text()')[0].strip()

            data_publicacao = tree.xpath(u'//*[(self::span or self::p) and contains(text(), "Publicado em")]/text()')[0].strip()
            data_publicacao = regex.sub(ur'Publicado em ', u'', data_publicacao)

            categoria = u', '.join(tree.xpath(u'//div[@id="category"]/span/a/text()'))
        except:
            return True

        print data_publicacao + u'\n' + titulo + u'\n' + subtitulo + u'\n' + link[1] + u'\n' + categoria + u'\n'

        self.tabela.append([data_publicacao, titulo + u': ' + subtitulo, self.publicacao + u' - ' + link[0], link[1], categoria])
        self.tabela2.append([data_publicacao, titulo, subtitulo, self.publicacao + u' - ' + link[0], link[1], categoria])

        return True

    def extract_noticias_pages(self, url_l):
        links = []

        tipo = url_l[0]
        url = url_l[1]

        while url != None:
            r = requests.get(url)

            if not r.text:
                logger.info(u'erro ao iniciar extração das noticias, saindo...')
                return []

            pagina = r.text
            tree = html.fromstring(pagina)

            noticias_c = tree.xpath(u'//h2[@class="tileHeadline"]/a')

            for noticia_c in noticias_c:
                links.append([tipo, noticia_c.get(u'href').strip()])

            try:
                url = tree.xpath(u'//span[@class="next"]/a')[0].get(u'href')
            except:
                url = None

        return links

    def extract_noticias_pagination(self):
        urls = [
            [u'sobreCultura', u'http://cienciahoje.uol.com.br/revista-ch/sobrecultura/sobreCultura/folder_summary_view?b_start:int=0'],
            [u'Resenhas', u'http://cienciahoje.uol.com.br/resenhas/resenhas/folder_summary_view?b_start:int=0'],
            [u'Notícias', u'http://cienciahoje.uol.com.br/noticias/noticias/folder_summary_view?b_start:int=0']]

        urls = urls + self.extract_especiais()

        links = []

        for url in urls:
            links = links + self.extract_noticias_pages(url)

        return links

    def extract_especiais(self):
        url = 'http://cienciahoje.uol.com.br/categorias?listasubject=Especiais&b_start:int=0'

        links = []

        while url != None:
            r = requests.get(url)

            if not r.text:
                logger.info(u'erro ao iniciar extração das noticias, saindo...')
                return []

            pagina = r.text
            tree = html.fromstring(pagina)

            especiais_c = tree.xpath(u'//dt[@class="contenttype-folder" or @class="contenttype-topic"]/a[2]')

            for especial_c in especiais_c:
                links.append([u'Especiais', especial_c.get(u'href')])

            try:
                url = tree.xpath(u'//span[@class="next"]/a')[0].get(u'href')
            except:
                url = None

        return links

    def extract_noticias(self):
        links = self.extract_noticias_pagination()

        for link in links:
            self.extract_noticia(link)

    def extract_edicao(self, url_l): # faltando pegar primeira notícia
        if url_l[2].find(u'2014') != -1 or url_l[2].find(u'2015') != -1:
            return True

        ano = int(regex.search(ur'([0-9]{4})', url_l[2]).group(1))
        # pra testar mais rapidamente
        #if ano > 2008:
        #    return True

        r = requests.get(url_l[1])

        if not r.text:
            logger.info(u'erro ao iniciar extração das noticias, saindo...')
            return False

        pagina = r.text
        tree = html.fromstring(pagina)

        materias_c = tree.xpath(u'//table[@class="invisible"]//td')

        for materia_c in materias_c:
            try:
                if len(materia_c.xpath(u'.//p[@class="callout"]')) > 0 or len(materia_c.xpath(u'.//p')) == 0:
                    continue

                edicao = url_l[2]
                try:
                    titulo = materia_c.xpath(u'./p//strong/text()')[0]
                except:
                    titulo = materia_c.xpath(u'.//strong/text()')[0]

                subtitulo = materia_c.xpath(u'./p')[-1].text_content()

                try:
                    link = materia_c.xpath(u'./p//a')[-1].get(u'href')

                    if link.startswith(u'/'):
                        link = self.url_base + link
                except:
                    link = url_l[1]
                categoria = u''

                print edicao + u'\n' + titulo + u'\n' + subtitulo + u'\n' + link + u'\n' + categoria + u'\n'

                self.tabela.append([edicao, titulo + u': ' + subtitulo, self.publicacao + u' - ' + url_l[0], link, categoria])
                self.tabela2.append([edicao, titulo, subtitulo, self.publicacao + u' - ' + url_l[0], link, categoria])
            except:
                logger.exception(u'erro ao pegar chamada de dentro da edicao')

        # antes da edição 255b
        if len(materias_c) == 0:

            materias_c = tree.xpath(u'//div[@class="migratedContent"]//p[@class="titch2"]/..')

            for materia_c in materias_c:
                edicao = url_l[2]

                titulo = ''.join(materia_c.xpath(u'.//strong/text()')).strip()
                subtitulo = materia_c.text_content().strip()
                subtitulo = regex.sub(ur'[\n\r\s]{1,}', u' ', subtitulo.replace(titulo, u'')).strip()
                titulo = regex.sub(ur'[\n\r\s]{1,}', u' ', titulo).strip()

                try:
                    link = materia_c.xpath(u'.//a')[-1].get(u'href')

                    if link.startswith(u'/'):
                        link = self.url_base + link
                except:
                    link = url_l[1]

                categoria = u''

                print edicao + u'\n' + titulo + u'\n' + subtitulo + u'\n' + link + u'\n' + categoria + u'\n'

                self.tabela.append([edicao, titulo + u': ' + subtitulo, self.publicacao + u' - ' + url_l[0], link, categoria])
                self.tabela2.append([edicao, titulo, subtitulo, self.publicacao + u' - ' + url_l[0], link, categoria])

    def extract_edicoes_pages(self):
        url = 'http://cienciahoje.uol.com.br/revista-ch'

        links = []

        while url != None:
            r = requests.get(url)

            if not r.text:
                logger.info(u'erro ao iniciar extração das noticias, saindo...')
                return []

            pagina = r.text
            tree = html.fromstring(pagina)

            edicoes_c = tree.xpath(u'//p[@class="edicao"]')

            for edicao_c in edicoes_c:
                links.append([u'Revista', edicao_c.xpath(u'./a')[0].get(u'href'), edicao_c.xpath(u'./a/text()')[0] + u' - ' + edicao_c.xpath(u'./span/text()')[0]])

            try:
                url = tree.xpath(u'//span[@class="next"]/a')[0].get(u'href')
            except:
                url = None

        return links

    def extract_edicoes(self):
        links = self.extract_edicoes_pages()

        for link in links:
            self.extract_edicao(link)

    def extrai_salva(self):
        self.extract_noticias()
        self.extract_edicoes()

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
def extrai(inicio):
    ciencia_hoje = Ciencia_hoje()
    ciencia_hoje.extrai_salva()

if __name__ == '__main__':
    cli()
