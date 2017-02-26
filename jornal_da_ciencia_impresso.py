#!/usr/bin/env python
# -*- coding: utf-8 -*-

import os
import time
import csv
import subprocess
import pickle

import requests
import regex
import click
import copy
import pyperclip
import lxml.html
from pynput import keyboard

import csv_utf8
import helpers


logger = helpers.get_logger()


class Jornal_da_ciencia_impresso():

    def __init__(self):
        # tabela.append([edicao, titulo + ': ' + subtitulo,
        #     publicacao, link, tags])
        # tabela2.append([edicao, titulo, subtitulo, publicacao, link, tags])

        self.publicacao = u'Jornal da Ciencia Impresso'

        self.url = u'http://jcnoticias.jornaldaciencia.org.br/'

        self.tabela = []
        self.tabela2 = []

    def extract_edicoes(self):
        url = self.url + u'category/pdf/page/'

        k = 1

        while True:
            res = requests.get(url + unicode(k))

            root = lxml.html.fromstring(res.content)

            edicoes = root.xpath(u'//div[@class="pdf-edicao"]')
            
            for edicao in edicoes:
                link_c = edicao.xpath(u'.//div[@class="pdf-titulo"]/a')[0]

                print link_c.text
                print link_c.get(u'href')

                res = self.extract_from_edicao(link_c.text, link_c.get(u'href'))

                for res1 in res:
                    self.tabela.append([
                        res1['edicao'],
                        res1['titulo'].strip(),
                        res1.get(u'subtitulo', u'').strip(),
                        u'Jornal da Ciência Impresso',
                        res1[u'link'],
                        res1.get(u'tags', u'')])

                    title_and_sub = regex.sub(
                            ur'\s+', u' ',
                            res1['titulo'].strip() + u': ' + res1.get(u'subtitulo', u'').strip(),
                            flags=regex.V1 | regex.I)

                    title_and_sub = regex.sub(
                        ur'(: $|- )',
                        u'',
                        title_and_sub,
                        flags=regex.V1 | regex.I)
                    
                    self.tabela2.append([
                        res1['edicao'],
                        title_and_sub,
                        u'Jornal da Ciência Impresso',
                        res1[u'link'],
                        regex.sub(
                            ur'\s+', u' ',
                            res1.get(u'tags', u''),
                            flags=regex.V1 | regex.I)])

            if len(edicoes):
                k += 1
            else:
                break

    def extract_from_edicao(self, titulo, link):
        filename = os.path.join(
            u'./data/jornal_da_ciencia_impressos', link.split('/')[-1])

        if not os.path.exists(filename):
            with open(filename, 'wb') as filex:
                filex.write(requests.get(link).content)

        if os.path.exists(filename + '.p'):
            res2 = pickle.load(open(filename + '.p', 'rb'))

            for res1 in res2:
                res1[u'link'] = link

            return res2

            # raw_input()

            return

        p = subprocess.Popen(
            [u'evince', filename],
            stdout=open(os.devnull, 'w'), stderr=open(os.devnull, 'w'))

        global edicao
        global link_e
        global res
        global semi_res

        link_e = link
        edicao = titulo
        res = []
        semi_res = None

        def on_release(key):
            global edicao
            global link_e
            global res
            global semi_res

            try:
                key = key.char
            except:
                pass

            if key == u'q':
                if semi_res is not None:
                    res.append(copy.copy(semi_res))

                semi_res = {
                    u'edicao': edicao,
                    u'titulo': pyperclip.paste(),
                    u'link': link_e}

            if key == u'w':
                semi_res['subtitulo'] = pyperclip.paste()

            if key == u'e':
                semi_res['tags'] = pyperclip.paste()

            if key == keyboard.Key.esc:
                # Stop listener
                return False

        # Collect events until released
        with keyboard.Listener(on_release=on_release) as listener:
            listener.join()

        p.terminate()

        with open(filename + '.p', 'wb') as fpickle:
            pickle.dump(res, fpickle)

        return res

    def extrai_salva(self):
        self.extract_edicoes()

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
def extrai(inicio):
    jornal_da_ciencia = Jornal_da_ciencia_impresso()
    jornal_da_ciencia.extrai_salva()


if __name__ == '__main__':
    cli()
