#!/usr/bin/env python
# -*- coding: utf-8 -*-

import datetime
import time
import csv
import re
import click
import csv_utf8

import requests

from lxml import html


import helpers


logger = helpers.get_logger()


def r_get(url):
    k = 0
    while True:
        try:
            r = requests.get(url)

            if not r.text:
                raise Exception(u'erro ao iniciar extração')

            return r
        except Exception:
            logger.exception(u'erro ao acessar "%s"' % url)

            k += 1

            time.sleep(5)

            if k > 10:
                logger.info(
                    u'muitos erros ao acessa pagina "%s", saindo...', url)

                return None


def limpa(text):
    return re.sub(ur'[ ]{2,}', u' ', re.sub(ur'[\t\r\n]', u'', text)).strip()


class Unicamp_ju():

    def __init__(self):
        # tabela.append([edicao, titulo, subtitulo, publicacao, link, tags])
        # tabela2.append([edicao, titulo + ': ' + subtitulo, publicacao, link, tags])

        self.publicacao = u'Jornal da Unicamp'

        self.tabela = []
        self.tabela2 = []

    def extract(self):
        self.extract_list_editions_after_2011()

        self.extract_list_editions_until_2011()

    def extract_list_editions_after_2011(self):
        url = u'http://www.unicamp.br/unicamp/ju/anteriores/'
        url_aux = u'?page='

        super_url = u'http://www.unicamp.br'

        for ano in range(datetime.datetime.now().year, 2011, -1):
            print u'**************************************'
            print u'%s' % ano
            print u'**************************************'

            for p in xrange(2, -1, -1):
                r = r_get(url + unicode(ano) + url_aux + unicode(p))

                if r is None:
                    logger.info(
                        u'erro ao iniciar extração do jornal da unicamp, saindo...')
                    return False

                tree = html.fromstring(r.content)

                for edicao in tree.xpath(u'//div[contains(@class, "view-content")]/h3'):
                    print edicao.text_content()

                    for div in edicao.itersiblings():
                        link = super_url + div.xpath('.//a[1]')[0].get(u'href')
                        break

                    self.extract_version3(
                        edicao.text_content() + u' - ' + unicode(ano), link)

    def extract_list_editions_until_2011(self):
        links = []

        url = u'http://www.unicamp.br/unicamp/ju/anos-anteriores'

        r = r_get(url)

        if r is None:
            logger.info(
                u'erro ao iniciar extração do jornal da unicamp, saindo...')
            return False

        try:
            pagina = r.text
            tree = html.fromstring(pagina)

            anos = tree.xpath(u'//div[@class="ano_wrap"]')

            for ano_div in anos:
                ano = ano_div.xpath(
                    u'.//span[@class="ano_title"]')[0].text_content().strip()

                for tr in ano_div.xpath(u'.//tr'):
                    try:
                        tds = tr.xpath(u'.//td')
                    except Exception:
                        logger.exception(u'erro ao pegar trs')

                    if len(tds) >= 2:
                        try:
                            link = tds[1].xpath(u'.//a')[0]
                            links.append([
                                ano,
                                re.sub(
                                    ur'[ ]{2,}', u' ',
                                    link.text_content().replace(
                                        u'\n', u'').replace(u'\t', u'')),
                                link.get(u'href')])
                        except:
                            continue

                    if len(tds) == 1:
                        try:
                            link = tds[0].xpath(u'.//a')[0]
                            links.append([
                                ano,
                                re.sub(
                                    ur'[ ]{2,}', u' ',
                                    link.text_content().replace(
                                        u'\n', u'').replace(u'\t', u'')),
                                link.get(u'href')])
                        except:
                            continue
        except Exception:
            logger.exception(u'erro ao pegar ano')

        ano = u''
        edicao = u''
        for link in links:
            if ano != link[0]:
                ano = link[0]
                print u'**************************************'
                print u'%s' % ano
                print u'**************************************'

            if edicao != link[1]:
                edicao = link[1]
                print u'\n%s' % edicao
                print u'**************************************'

            self.extract_select_version(edicao + u' - ' + ano, link[2])

    def extract_select_version(self, edition, url):
        r = r_get(url)

        if r is None:
            logger.info(
                u'erro ao iniciar extração do jornal da unicamp, saindo...')

            return False

        tree = html.fromstring(r.content)

        if len(tree.xpath(u'//img[@src="images/ch-nesta.jpg"]')) > 0:
            return self.extract_version2(edition, url, tree)

        return self.extract_version1(edition, url, tree)

    def extract_version1(self, edition, url, tree):
        super_url = url.rsplit(u'/', 1)[0] + u'/'

        try:
            links = tree.xpath(
                u'//*[contains(text(), "Leia nesta edi")]/ancestor::tr[1]/following-sibling::tr')

            for link in links[1:]:
                try:
                    el_link = link.xpath(u'.//a')[0].get(u'href')
                    el_titulo = link.xpath(u'.//a')[0].text_content().strip()

                    if el_link.find('http://') == -1:
                        el_link = super_url + el_link

                    if len(el_titulo):
                        self.extract_version1_news(edition, el_titulo, el_link)
                except:
                    pass
        except Exception as e:
            logger.exception(u'erro na versao 1')

    def extract_version1_news(self, edition, titulo, url):
        r = r_get(url)

        if re.search(
                ur'^(Cartas|Painel da semana|Teses |Painel da|Portal da|Livro da)',
                titulo):
            return

        if r is None:
            logger.info(u'erro ao iniciar extração da noticia, saindo...')
            return False

        tree = html.fromstring(r.content)

        subtitulo = u''
        try:
            div = tree.xpath(
                u'//img[contains(@src, "edit_jornal.jpg")]/ancestor::td[1]')[0]

            subtitulo = re.sub(ur'[\t\n]', u'', u''.join(
                div.xpath('.//i/text()')))
        except Exception as e:
            logger.exception(u'erro dentro da reportagem')

        self.tabela.append(
            [edition, titulo, subtitulo, self.publicacao, url, u''])
        self.tabela2.append(
            [edition, titulo + u' - ' + subtitulo, self.publicacao, url, u''])

    def extract_version2(self, edition, url, tree):
        super_url = url.rsplit(u'/', 1)[0] + u'/'

        try:
            links = tree.xpath(u'//a[@class="text-link"]')

            for link in links:
                el_titulo = limpa(link.text_content())

                el_link = link.get(u'href')

                if el_link.find('http://') == -1:
                    el_link = super_url + el_link

                self.extract_version2_news(edition, el_titulo, el_link)
        except Exception as e:
            logger.exception(u'erro na versao 2')

    def extract_version2_news(self, edition, titulo, url):
        if len(titulo) == 0 or \
           re.search(ur'Capa da Edi|Teses', titulo) is not None:
            return

        r = r_get(url)

        if r is None:
            logger.info(
                u'erro ao iniciar extração do jornal da unicamp, saindo...')

            return False

        tree = html.fromstring(r.content)

        subtitulo = u''
        try:
            subtitulo = limpa(tree.xpath(
                u'//td[@class="titulos"][1]//em')[0].text_content())
        except Exception as e:
            # print url
            # logger.exception(u'erro na versao 2 da unicamp, dentro da noticia')
            pass

        self.tabela.append(
            [edition, titulo, subtitulo, self.publicacao, url, u''])
        self.tabela2.append(
            [edition, titulo + u' - ' + subtitulo, self.publicacao, url, u''])

    def extract_version3(self, edition, url):
        r = r_get(url)

        if r is None:
            logger.info(
                u'erro ao iniciar extração do jornal da unicamp, saindo...')

            return False

        tree = html.fromstring(r.content)

        for reportagem in tree.xpath(
                u'//div[@class="left_j_bar"]//div[@class="field-item even"]/a')[1:]:
            self.extract_version3_news(edition, limpa(
                reportagem.text_content()), reportagem.get(u'href'))

    def extract_version3_news(self, edition, titulo, url):
        try:
            r = r_get(url)

            if r is None:
                logger.info(
                    u'erro ao iniciar extração do jornal da unicamp, saindo...')
                return False

            tree = html.fromstring(r.content)

            subtitulo = tree.xpath(
                u'//span[@class="sub_title"]')[0].text_content()

            self.tabela.append(
                [edition, titulo, subtitulo, self.publicacao, url, u''])

            self.tabela2.append([
                edition, titulo + u' - ' + subtitulo, self.publicacao,
                url, u''])

            # print u'\n'.join([url, titulo, subtitulo])
        except Exception as e:
            logger.exception(u'erro ao extrair noticia da versao 3')

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
def extrai_unicamp_ju(inicio):
    unicamp_ju = Unicamp_ju()
    unicamp_ju.extrai_salva()

if __name__ == '__main__':
    cli()
