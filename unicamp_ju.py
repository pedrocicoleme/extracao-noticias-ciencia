#!/usr/bin/env python
# -*- coding: utf-8 -*-

import urlparse

import requests
import click
import regex
import lxml.html

import helpers


logger = helpers.get_logger()


def extrai_tudo():
    tabela = []
    tabela2 = []

    new_urls = [
        (u'https://www.unicamp.br/unicamp/ju/678'
         u'/monteiro-lobato-poder-literatura-e-petroleo')]

    for url in new_urls:
        tabela, tabela2 = parse_edicao(url, tabela, tabela2)

    tabela, tabela2 = extrai_2015_2016(tabela, tabela2)

    return tabela, tabela2


def extrai_2015_2016(tabela, tabela2):
    urls = [
        u'http://www.unicamp.br/unicamp/ju/2016',
        u'http://www.unicamp.br/unicamp/ju/2015']

    tabela = []
    tabela2 = []

    for url in urls:
        res = requests.get(url, verify=False)

        root = lxml.html.fromstring(res.content)

        links_edicoes = root.xpath(
            u'//div[@class="view-content clearfix"]/div'
            u'/div[contains(@class, "views-field-title")]'
            u'/span[@class="field-content"]/a')

        for link_edicao in links_edicoes:
            link = urlparse.urljoin(res.url, link_edicao.get(u'href'))

            print link

            parse_edicao(link, tabela, tabela2)

    return tabela, tabela2


def parse_edicao(link, tabela, tabela2):
    res = requests.get(link, verify=False)

    m = regex.search(ur'/(\d+)/', link)

    edicao_num = int(m.group(1))
    edicao = u'Edição {}'.format(m.group(1))

    print edicao

    root = lxml.html.fromstring(res.content)

    links = root.xpath(
        u'//div[@class="left_j_bar" or '
        u'@id="block-views-block-noticia-moldura-block-3-3"]'
        u'//a/@href')

    for link in links:
        if link == u'#':
            continue

        link_a = urlparse.urljoin(res.url, link)

        if unicode(res.url) == unicode(link_a):
            continue

        if unicode(link_a) in [u'http://www8.labunicamp.hom.unicamp.br/unicamp/ju/639']:
            continue

        info_news = parse_noticia(link_a, edicao_num in (674, 672, 646))

        if info_news is None:
            continue

        titulo, subtitulo, link, cat = info_news

        titulo_subtitulo = regex.sub(
            ur': $', u'', titulo + u': ' + subtitulo.strip())

        tabela.append(
            [edicao, titulo, subtitulo, u'Jornal da Unicamp', link, cat])
        tabela2.append(
            [edicao, titulo_subtitulo, u'Jornal da Unicamp',
             link, cat])

    # raw_input()

    return tabela, tabela2


def parse_noticia(link, use_text=False):
    link = link.replace(
        u'http://www8.labunicamp.hom.unicamp.br/unicamp-old/ju/',
        u'http://www.unicamp.br/unicamp/ju/')

    print link

    res = requests.get(link, verify=False)

    if use_text:
        text = res.text
    else:
        text = res.content

    root = lxml.html.fromstring(text)

    try:
        titulo = root.xpath(
            u'//h1[@class="node__title"]')[0].text_content().strip()

        subtitulo = root.xpath(
            u'//div[contains(@class, "field-node--field-subtitulo")]')

        if len(subtitulo):
            subtitulo = subtitulo[0].text_content().strip()
        else:
            subtitulo = u''
    except:
        bloco = root.xpath(u'//div[contains(@class, "jornal_pagina")]')

        if not len(bloco):
            return None

        titulo = bloco[0].xpath(u'./h2/text()')

        if not len(titulo):
            titulo = bloco[0].xpath(u'./h2/img/@alt')

        if not len(titulo):
            titulo = [bloco[0].xpath(u'./h2')[0].text_content()]

        titulo = titulo[0].strip()

        subtitulo = bloco[0].xpath(
            u'./span[@class="sub_title"]')

        if len(subtitulo):
            subtitulo = subtitulo[0].text_content().strip()
        else:
            subtitulo = u''

    if regex.search(
            ur'^(Cartas|Painel da semana|Teses|Painel da|Portal da|Livro da)',
            titulo):
        return None

    print titulo

    subtitulo = regex.sub(ur'\s+', u' ', subtitulo, flags=regex.V1 | regex.I)

    return titulo, subtitulo, link, u''


@click.group()
def cli():
    pass


@cli.command()
def extrai():
    tabela, tabela2 = extrai_tudo()

    helpers.salva_tabelas(u'jornal_da_unicamp', tabela, tabela2)


if __name__ == '__main__':
    cli()
