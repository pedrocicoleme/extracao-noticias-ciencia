#!/usr/bin/env python
# -*- coding: utf-8 -*-

import os
import time
import csv
import re
import click
import csv_utf8

import requests

from lxml import html

import helpers


logger = helpers.get_logger()


s = requests.Session()


def r_get(url):
    k = 0
    while True:
        try:
            r = s.get(url)

            if not r.text:
                raise Exception(u'erro ao iniciar extração')

            return r
        except Exception as e:
            logger.exception(u'erro ao acessar "%s"' % url)
            k += 1
            time.sleep(5)

            if k > 10:
                logger.info(
                    u'muitos erros ao acessa pagina "%s", saindo...' % url)
                return None


def limpa(text):
    return re.sub(ur'[ ]{2,}', u' ', re.sub(ur'[\t\r\n]', u'', text)).strip()


class Minas_faz_ciencia():

    def __init__(self):
        # tabela.append([edicao, titulo + ': ' + subtitulo, publicacao, link, tags])
        # tabela2.append([edicao, titulo, subtitulo, publicacao, link, tags])

        self.publicacao = u'Revista Minas Faz Ciência'

        self.tabela = []
        self.tabela2 = []

        self.links = {
            u'MFC_60': u'http://issuu.com/fapemig/docs/mfc_60?e=3684464/10653328',
            u'MFC_59': u'http://issuu.com/fapemig/docs/mfc_59__',
            u'MFC_58': u'http://issuu.com/fapemig/docs/mfc_58_alta',
            u'MFC_57': u'http://www.fapemig.br/wp-content/uploads/2014/06/MFC-57_final1.pdf',
            u'MFC_56': u'http://issuu.com/fapemig/docs/mfc_56_final',
            u'MFC_55': u'http://issuu.com/fapemig/docs/mfc_55?e=3684464/6154272',
            u'MFC_54': u'http://issuu.com/fapemig/docs/mfc_54?e=3684464/4683726',
            u'MFC_53': u'http://issuu.com/FAPEMIG_Redes_Sociais/docs/mfc__53?e=6114905/4249539',
            u'MFC_52': u'http://issuu.com/fapemig/docs/minas_faz_ci_ncia_52#download',
            u'MFC_51': u'http://issuu.com/fapemig/docs/minas_faz_ci_ncia__51',
            u'MFC_50': u'http://www.fapemig.br/wp-content/uploads/2012/08/MinasfazCiencia50.pdf',
            u'MFC_49': u'http://www.fapemig.br/wp-content/uploads/2012/07/MFC-49-Final.pdf',
            u'MFC_48': u'http://issuu.com/fapemig/docs/mfc_48?mode=window',
            u'MFC_47': u'http://www.fapemig.br/wp-content/uploads/2012/02/MFC-47.pdf',
            u'MFC_46': u'http://www.fapemig.br/wp-content/uploads/2011/11/MFC-46.pdf',
            u'MFC_45': u'http://www.fapemig.br/wp-content/uploads/2011/11/MFC-45.pdf',
            u'MFC_44': u'http://www.fapemig.br/wp-content/uploads/2011/11/MFC-44.pdf',
            u'MFC_43': u'http://www.fapemig.br/wp-content/uploads/2011/11/MFC-43.pdf',
            u'MFC_42': u'http://www.fapemig.br/wp-content/uploads/2011/11/MFC-421.pdf',
            u'MFC_41': u'http://www.fapemig.br/wp-content/uploads/2011/11/MFC-41.pdf',
            u'MFC_40': u'http://www.fapemig.br/wp-content/uploads/2011/11/MFC-40.pdf',
            u'MFC_39': u'http://www.fapemig.br/wp-content/uploads/2011/11/MFC-39.pdf',
            u'MFC_38': u'http://www.fapemig.br/wp-content/uploads/2011/11/MFC-38.pdf',
            u'MFC_37': u'http://www.fapemig.br/wp-content/uploads/2011/11/MFC-37.pdf',
            u'MFC_36': u'http://www.fapemig.br/wp-content/uploads/2011/11/MFC-36.pdf',
            u'MFC_35': u'http://www.fapemig.br/wp-content/uploads/2011/11/MFC-35.pdf',
            u'MFC_Inovacao': u'http://issuu.com/fapemig_redes_sociais/docs/mfc_inova____o_final',
            u'MFC_Especial': u'http://www.fapemig.br/wp-content/uploads/2011/11/MFC-Especial.pdf',
            u'MFC_Especial_Redes_de_Pesquisa': u'http://issuu.com/fapemig/docs/minas_faz_ci__ncia_especial_redes_d'
        }

    def extract(self):
        self.extract_list_editions_new()

        # self.extract_list_editions_old()

    def extract_list_editions_new(self):
        path = 'minas_pdfs/'

        #os.system('for file in ./minas_pdfs/*.pdf; do pdftotext -raw "$file" "$file.txt"; done')

        for file in os.listdir(path):
            if file.endswith(".pdf.txt"):
                # print(file)

                # time.sleep(2)

                with open(path + file) as fo:
                    file_lines = fo.readlines()

                paginas = ''.join(file_lines).split('\x0c')[:10]

                tem = False
                for pagina in paginas:
                    if re.search(r'\xc3\x8d[\n]?N[\n]?D[\n]?I[\n]?C[\n]?E', pagina, re.IGNORECASE) != None:
                        pagina = re.sub(
                            r'\xc3\x8d[\n]?N[\n]?D[\n]?I[\n]?C[\n]?E\n', '', pagina, re.IGNORECASE)
                        tem = True
                        break

                if tem is False:
                    with open(path + re.sub(r'\.pdf', '', file)) as fo:
                        pagina = ''.join(fo.readlines())

                print file + '\n'
                # print pagina
                self.extract_news_edition_new(file.split('.')[0], pagina)

                print u'********************************************************************************\n'

                #raw_input("Press Enter to continue...")

    def extract_news_edition_new(self, edition, page):
        link = self.links[edition.decode('utf-8')]

        noticias = re.split(r'\n[0-9]{1,}[\n ]', page)

        for noticia in noticias:
            linhas = noticia.split('\n')

            linhas = [x for x in linhas if re.search(
                r'^[0-9]{1,}$', x.strip()) == None]

            if len(linhas) > 1:
                l = 1
                tags = linhas[0]

                while re.search(r'(^ENGENHARIA| d[aeo]| para| em)[ ]?$', tags, re.IGNORECASE) != None and l < len(linhas):
                    tags += ' ' + linhas[l]
                    l += 1

                if l < len(linhas):
                    while re.search(r'^(d[aeo]|para|em|Gerais)[ ]?', linhas[l]) != None and l < len(linhas):
                        tags += ' ' + linhas[l]
                        l += 1

                        if l == len(linhas):
                            break

                tags = re.sub(r'6 ESP', 'ESP', tags, re.IGNORECASE)

                titulo = ' '.join(linhas[l:])

                if re.search(r'LEMBRA DESSA\?', tags):
                    g = tags.split('?', 1)

                    tags = g[0] + '?'
                    titulo = (g[1] + ' ' + titulo).strip()

                print tags
                print titulo
                print u'\n'

                subtitulo = u''
                edition = edition.decode('utf-8').replace('_', ' ')
                titulo = titulo.decode('utf-8').strip()
                tags = tags.decode('utf-8')

                self.tabela.append(
                    [edition, titulo, subtitulo, self.publicacao, link, tags])
                self.tabela2.append(
                    [edition, titulo, self.publicacao, link, tags])

    def extract_list_editions_old(self):
        url = u'http://revista.fapemig.br/outrasedicoes.php'

        super_url = u'http://revista.fapemig.br/'

        r = r_get(url)

        if r is None:
            logger.info(
                u'erro ao iniciar extração do minas faz ciencia, saindo...')
            return False

        tree = html.fromstring(r.content)

        for revista in tree.xpath(u'//div[@id="divText"]/table[1]//table[1]//a'):
            link = super_url + revista.get(u'href')

            infos = revista.xpath(
                u'./ancestor::td[1]/ancestor::td[1]/following-sibling::td[1]')[0]

            edicao = limpa(infos.xpath(u'./b')[0].text_content())

            em = infos.xpath(u'.//*[self::em or self::font]')

            if len(em) > 0:
                edicao += u' - ' + limpa(em[0].text_content())

            self.extract_edition_old(edicao, link)

    def extract_edition_old(self, edition, url):
        url_reportagens = u'http://revista.fapemig.br/reportagens.php'

        super_url = u'http://revista.fapemig.br/'

        r = r_get(url)
        r = r_get(url_reportagens)

        if r is None:
            logger.info(
                u'erro ao iniciar extração do minas faz ciencia, saindo...')
            return False

        tree = html.fromstring(r.content)

        print u'\n' + edition
        for reportagem in tree.xpath(u'//div[@id="divText"]//a'):
            titulo = limpa(reportagem.text_content())
            link = super_url + reportagem.get(u'href')
            subtitulo = self.extract_news_old(
                super_url + reportagem.get(u'href'))
            # print u'\n'

            self.tabela.append([edition, titulo, subtitulo,
                                self.publicacao, link, u''])
            self.tabela2.append(
                [edition, titulo + ': ' + subtitulo, self.publicacao, link, u''])

    def extract_news_old(self, url):
        r = r_get(url)

        if r is None:
            logger.info(
                u'erro ao iniciar extração do minas faz ciencia, saindo...')
            return False

        tree = html.fromstring(r.content)

        subtitulo = u''
        for p in tree.xpath(u'//div[@id="divText"]//*[self::p or self::font or self::em]'):
            subtitulo = p.text_content().strip()

            if len(subtitulo) > 100:
                tem = False

                for subt in p.iterdescendants():
                    if len(subt.text_content().strip()) > 0:
                        tem = True
                        subtitulo = subt.text_content().strip()
                        break

                if tem is False:
                    subtitulo = subtitulo.split('.')[0].strip()

            if len(subtitulo) > 0:
                break

        if len(subtitulo) == 0:
            try:
                j = tree.xpath(
                    u'//div[@id="divText"]//em')[0].text_content().strip()

                if re.search(ur'^\(', j) == None:
                    subtitulo = j
            except:
                pass

        return limpa(subtitulo)

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
def extrai_minas_faz_ciencia(inicio):
    minas_faz_ciencia = Minas_faz_ciencia()
    minas_faz_ciencia.extrai_salva()

if __name__ == '__main__':
    cli()
