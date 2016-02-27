#!/usr/bin/env python
# -*- coding: utf-8 -*-

import sys
import time
import datetime
import csv
import re
import click
import csv_utf8

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

base_url = u'http://www.unesp.br'

def r_get(url):
    k = 0
    while True:
        try:
            r = requests.get(url)

            if not r.text:
                raise Exception(u'erro ao iniciar extração')

            return r
        except Exception as e:
            logger.exception(u'erro ao acessar "%s"' % url)
            k += 1
            time.sleep(5)

            if k > 10:
                logger.info(u'muitos erros ao acessa pagina "%s", saindo...' % url)
                return None

class Unesp_ciencia():
    def __init__(self):
        # tabela.append([edicao, titulo + ': ' + subtitulo, publicacao, link, tags])
        # tabela2.append([edicao, titulo, subtitulo, publicacao, link, tags])

        self.publicacao = u'Revista Unesp Ciência'

        self.tabela = []
        self.tabela2 = []

    def extract(self):
        url = u'http://www.unesp.br/revista/edicoes/'

        r = requests.get(url)

        if r is None:
            logger.info(u'erro ao iniciar extração da revista unesp ciência, saindo...')
            return False

        pagina = r.text
        tree = html.fromstring(pagina)

        anos = tree.xpath(u'//td[@class="noticiaTEXTO"]//a[contains(@href, "/revista/edicoes")]')

        for ano in anos:
            print u'**************************************'
            print u'%s' % ano.text_content().strip()
            print u'**************************************'
            self.extract_revistas(ano.get(u'href'))

    def extract_revistas(self, url):
        r = requests.get(base_url + url)

        if r is None:
            logger.info(u'erro ao iniciar extração da revista unesp ciência, saindo...')
            return False

        pagina = r.text
        tree = html.fromstring(pagina)

        revistas = tree.xpath(u'//td[@class="noticiaTEXTO"]//td/a')

        for revista in reversed(revistas):
            revista_edicao = revista.xpath(u'./span/text()')[0].strip()
            #revista_titulo = revista.xpath(u'./div[@class="title"]/text()')[0].strip()
            revista_url = revista.get(u'href').strip()

            print revista_edicao + u'\n' + revista_url + u'\n=================================='

            self.extract_reportagens(revista_edicao, revista_url)

            print u'\n'

    def extract_reportagens(self, edicao, url):
        # [edicao, titulo, subtitulo, publicacao, link, tags]
        reps = []

        r = r_get(base_url + url)

        super_url = u'http://www.unesp.br'

        if not r.text:
            logger.info(u'erro ao iniciar extração da revista fapesp, saindo...')
            raise Exception(u'erro ao iniciar extração')

        try:
            pagina = r.text
            tree = html.fromstring(pagina)

            # primeiras reportagens
            reportagens = tree.xpath(u'//td[@class="noticiaTEXTO"]//td[@class="noticiaTEXTO"]')[0]

            n = 0
            for reportagem in reportagens.xpath(u'.//a'):
                n += 1
                try:
                    # categoria
                    try:
                        categoria = [x.text_content().strip() for x in reportagem.itersiblings(preceding=True) if (x.tag == u'strong' or x.tag == u'b')][0]
                    except:
                        try:
                            x = reportagem.getparent()
                            if x.tag == u'b':
                                categoria = u''.join(x.xpath(u'./text()')).strip()

                            if len(categoria) == 0:
                                categoria = [y.text_content().strip() for y in x.itersiblings(preceding=True) if (x.tag == u'strong' or x.tag == u'b')][0]
                        except:
                            categoria = u''

                    # titulo
                    titulo = reportagem.xpath(u'.//span[@class="titulosessao"]')[0].text_content().strip()

                    # link
                    link = reportagem.get(u'href')

                    # subtitulo
                    subtitulo = u''.join(reportagem.xpath(u'./text()')).strip()

                    if len(subtitulo) == 0:
                        for x in reportagens.xpath(u'(.//a)[' + unicode(n) + u']/following-sibling::text()'):
                            if len(x.strip()) > 0:
                                subtitulo = x.strip()
                                break

                    if len(subtitulo) == 0:
                        for x in reportagens.xpath(u'(.//a)[' + unicode(n) + u']/../following-sibling::text()'):
                            if len(x.strip()) > 0:
                                subtitulo = x.strip()
                                break

                except Exception as e:
                    # logger.exception(u'erro na edição %s' % url)
                    continue

                # print u'\n'.join([categoria.strip(), titulo, super_url + link, re.sub(ur'[ ]{2,}', u' ', subtitulo.replace(u'\n', u''))]) + u'\n'

                self.tabela.append([edicao, titulo, re.sub(ur'[ ]{2,}', u' ', subtitulo.replace(u'\n', u'')), self.publicacao, super_url + link, categoria.strip()])
                self.tabela2.append([edicao, re.sub(ur'\: $', u'', titulo + u': ' + re.sub(ur'[ ]{2,}', u' ', subtitulo.replace(u'\n', u''))), self.publicacao, super_url + link, categoria.strip()])

            # últimas reportagens
            reportagens = tree.xpath(u'//td[@class="noticiaTEXTO"]/p[not(contains(@class, "linhaINDICE"))]/a')

            for reportagem in reportagens:
                txts = []
                tags = u''

                try:
                    titulo = reportagem.xpath(u'./span[@class="titulosessao"]')[0].text_content().strip()

                    try:
                        titulo += u' ' + reportagem.xpath(u'./strong')[0].text_content().strip()
                    except Exception as e:
                        pass

                    subtitulo = u''.join(reportagem.xpath(u'./text()')).strip()
                    link = reportagem.get(u'href').strip()

                    # print u'\n'.join([titulo, super_url + link, subtitulo]) + u'\n'

                    txts = titulo.split(u':')

                    if len(txts) > 1:
                        if len(txts[1].strip()) > 0:
                            tags = txts[0].strip()
                            txts[0] = txts[1].strip()

                    self.tabela.append([edicao, txts[0].strip(), subtitulo, self.publicacao, super_url + link, tags])
                    self.tabela2.append([edicao, re.sub(ur'\: $', u'', txts[0].strip() + u': ' + subtitulo), self.publicacao, super_url + link, tags])
                except Exception as e:
                    pass

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
def extrai_unesp_ciencia(inicio):
    unesp_ciencia = Unesp_ciencia()
    unesp_ciencia.extrai_salva()

if __name__ == '__main__':
    cli()