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


class Jornal_da_ciencia():

    def __init__(self):
        # tabela.append([edicao, titulo + ': ' + subtitulo, publicacao, link, tags])
        # tabela2.append([edicao, titulo, subtitulo, publicacao, link, tags])

        self.publicacao = u'Jornal da Ciencia'
        # self.url_base = u'http://www.unbciencia.unb.br'

        self.tabela = []
        self.tabela2 = []

    def extract_edicoes(self):
        url = u'http://jcnoticias.jornaldaciencia.org.br/category/edicoes/'

        edicoes = []

        r = requests.get(url)

        if not r.text:
            logger.info(u'erro ao iniciar extração das noticias, saindo...')

            return edicoes

        pagina = r.text
        tree = html.fromstring(pagina)

        edicoes_c = tree.xpath(u'//select[@id="cat"]//option')

        for edicao_c in edicoes_c:
            edicao = edicao_c.text.split(u',', 1)[0].strip()

            if edicao.find(u'Escolha uma') == -1:
                edicoes.append(edicao)

        return edicoes

    def extract(self):
        url = u'http://jcnoticias.jornaldaciencia.org.br/category/edicoes/'

        edicoes = self.extract_edicoes()

        #edicoes = [u'2130']

        n = 0
        m = 0
        for edicao in edicoes:
            print u'***********************************\n' + edicao + u'\n***********************************\n'
            r = requests.get(url + edicao)

            if not r.text:
                logger.info(
                    u'erro ao iniciar extração das noticias, saindo...')
                return False

            pagina = r.text
            tree = html.fromstring(pagina)

            edicao = tree.xpath(
                u'//div[@class="resumo-principal"]/strong/text()')[0].strip()

            print edicao

            noticias = tree.xpath(
                u'//div[@class="home-materia-edicao" or @class="materia-principal"]')

            for noticia in noticias:
                categoria = u''

                try:
                    link_c = noticia.xpath(
                        u'.//div[@class="home-titulo-materia" or @class="titulo-principal"]//a')[0]
                    titulo = regex.sub(
                        '^[0-9]{1,}\.\s', u'', link_c.text).strip()
                    link = link_c.get(u'href').strip()

                    try:
                        subtitulo = noticia.xpath(
                            u'.//div[@class="home-texto-materia" or @class="resumo-principal"]//p/text()')[0].strip()
                    except:
                        subtitulo = u''

                    # print edicao + u'\n' + titulo + u'\n' + subtitulo + u'\n'
                    # + link + u'\n'

                    self.tabela.append(
                        [edicao, titulo + u': ' + subtitulo, self.publicacao, link, categoria])
                    self.tabela2.append(
                        [edicao, titulo, subtitulo, self.publicacao, link, categoria])

                    n += 1
                except:
                    pass

            m += 1

        logger.info(u'total de %d notícias em %d edições' % (n, m))

    def extrai_salva(self):
        self.extract()

        with open('./data/%s-%s.csv' % (
                self.publicacao, time.strftime(u'%Y-%m-%d')), 'wb') as myfile:
            wr = csv_utf8.UnicodeWriter(myfile, quoting=csv.QUOTE_ALL)

            wr.writerows(self.tabela)

        with open('./data/%s-%s-ajustado.csv' % (
                self.publicacao, time.strftime(u'%Y-%m-%d')), 'wb') as myfile:
            wr = csv_utf8.UnicodeWriter(myfile, quoting=csv.QUOTE_ALL)

            wr.writerows(self.tabela2)


@click.group()
def cli():
    pass


@click.option('--inicio', help='Pagina de inicio', default=1)
@cli.command()
def extrai_jornal_da_ciencia(inicio):
    jornal_da_ciencia = Jornal_da_ciencia()
    jornal_da_ciencia.extrai_salva()

if __name__ == '__main__':
    cli()
