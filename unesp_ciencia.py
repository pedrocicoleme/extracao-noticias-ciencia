#!/usr/bin/env python
# -*- coding: utf-8 -*-

import time

import HTMLParser
import requests
import feedparser
import click
import lxml.html

import helpers


logger = helpers.get_logger()


def extrai_unesp_ciencia():
    tabela = []
    tabela2 = []

    url = (u'http://www.unespciencia.com.br/category/'
           u'edicoes-anteriores/feed/?paged=')

    k = 0
    while k >= 0:
        k += 1

        try:
            res = requests.get(url + unicode(k), timeout=20)

            if res.status_code == requests.codes.not_found:
                logger.info(u'unesp_ciencia - acabaram as paginas')

                k = -1

                break

            if res.status_code != requests.codes.ok:
                logger.info(
                    u'unesp_ciencia - erro ao pegar a pagina %s - %s',
                    k, res.status_code)

                k -= 1

                time.sleep(10)

                continue
        except Exception:
            logger.exception(u'unesp_ciencia - erro ao pegar a pagina %s', k)

            k -= 1

            time.sleep(10)

            continue

        feed = feedparser.parse(res.text)

        if len(feed.entries) == 0:
            logger.info(u'unesp_ciencia - acabaram as paginas')

            k = -1

            break

        edicao_num = None

        for entry in feed.entries:
            edicao_num = int(entry.title.strip().split(u' ', 1)[-1])

            if edicao_num <= 60:
                break

            print edicao_num

            html = entry.content[0][u'value']

            tabela, tabela2 = get_news_from_edition(
                html, entry.title.strip(), tabela, tabela2)

            # raw_input()

        if edicao_num < 60:
            break

        logger.info(u'unesp_ciencia - pagina %d', k)

    return tabela, tabela2

def get_news_from_edition(html, edicao, tabela, tabela2):
    root = lxml.html.fromstring(html)

    h = HTMLParser.HTMLParser()

    ps = root.xpath(u'//p')

    cat = None
    for p in ps:
        cat_c = p.xpath(u'./strong/text()')

        if len(cat_c):
            cat = cat_c[0].strip()

        artigos = p.xpath(u'./a')

        if not len(artigos):
            artigos = p.xpath(u'./br')

        for artigo in artigos:
            titulo = artigo.text or artigo.tail

            if isinstance(titulo, basestring):
                titulo = titulo.split(u' – ', 1)[0].strip()
            else:
                continue

            if not len(titulo) or \
               titulo == u'revistaunespciencia@reitoria.unesp.br':
                continue

            link = artigo.get(u'href', '')

            print cat
            print titulo
            print link
            print u'--------------------------'

            tabela.append([
                edicao,
                h.unescape(titulo),  # sem subtitulo no site
                u'Unesp Ciência',
                h.unescape(link),
                h.unescape(cat)])

            tabela2.append([
                edicao,
                h.unescape(cat),
                h.unescape(titulo),
                u'',
                h.unescape(cat),
                h.unescape(link)])

    return tabela, tabela2


@click.group()
def cli():
    pass


@cli.command()
def extrai():
    tabela, tabela2 = extrai_unesp_ciencia()

    helpers.salva_tabelas(u'unesp_ciencia', tabela, tabela2)


if __name__ == '__main__':
    cli()
