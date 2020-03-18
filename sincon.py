#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
     _
 ___(_)_ __   ___ ___  _ __
/ __| | '_ \ / __/ _ \| '_ \
\__ \ | | | | (_| (_) | | | |
|___/_|_| |_|\___\___/|_| |_|

Semplice wrapper script che permette di ottenere sinonimi e contrari di una parola da www.sinonimi-contrari.it

Copyright (C) 2020, Antonio Napolitano
Questo software è rilasciato sotto licenza GPLv3

"""

__author__ = 'Antonio Napolitano'
__license__ = 'GPLv3'
__version__ = '1.3'

import re
import json
import requests
import sys
import bs4
import argparse

WEBSITE = "https://www.sinonimi-contrari.it/"

def print_format(res):
    for el in res:
        if el['class'][0] == 'search-results':
            print(re.sub(r'\.$', '', # toglie i punti alla fine, fastidiosi quando si copia una parola
                         re.sub(r'(p\. u\.|intr\.|lett\.|sm\.|[A-Z]\w+\.|\d+\.)', r'\n\1 ', el.get_text()), # divide in righe le varie definizioni
                         flags=re.M))
            print()
        elif el['class'][0] == 'listOthersTerms':
            print(re.sub(r'\.$', '',
                         re.sub(r':', r': ', el.get_text()),
                         flags=re.M))
            print()

def to_json(res): # TODO: stolido, cargo
    r = {}
    for el in res:
        if el['class'][0] == 'search-results':
            for li in el.ol.findChildren('li') if el.ol else []:
                c = li.findChildren('span')
                r.setdefault(c[0].get_text(), []).extend(c[1].get_text().split(', '))

        elif el['class'][0] == 'listOthersTerms':
            r['altri'] = list(map(lambda x: x.get_text(), el.p.findChildren('a')))

    return r

def split_syncon(tags):
    for i in range(len(tags)):
        if tags[i].name == 'hr':
            syn = tags[:i]
            con = tags[i+1:]
            break
    if 'syn' not in locals():
        if args.json:
            print({'status': 'not found'})
        else:
            print("La parola cercata non esiste nel dizionario", file=sys.stderr)
        exit(1)

    return (syn[1:], con[1:])

parser = argparse.ArgumentParser(description='Semplice wrapper script che permette di ottenere sinonimi e contrari di una parola da www.sinonimi-contrari.it')
parser.add_argument('word', type=str, nargs=1, help='parola da cercare')
parser.add_argument('-j', '--json', action='store_true', help='print output in json')
args = parser.parse_args()

word = args.word[0]

r = requests.get(WEBSITE+word)
tags = bs4.BeautifulSoup(r.text, 'html.parser').find('div', {'class': 'termWrap'}).find_all(recursive=False)

syn, con = split_syncon(tags)

if args.json:
    obj = {'sin': to_json(syn), 'con': to_json(con), 'status': 'ok'}
    # obj['con'].remove('Il dizionario non contiene ancora contrari di test')
    print(json.dumps(obj))
else:
    print(f"\nSINONIMI di {word}")
    print_format(syn)
    
    print(f"CONTRARI di {word}")
    print_format(con)
