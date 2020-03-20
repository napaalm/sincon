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
__version__ = '2.0'

import re
import json
import requests
import sys
import bs4
import argparse

WEBSITE = "https://www.sinonimi-contrari.it/"

def print_format(obj):
    sin, con = obj['sin'], obj['con']

    print(f"\nSINONIMI di {word}")

    if len(sin) == 0:
        print(f"\nIl dizionario non contiene ancora sinonimi di {word}")
    elif len(sin) != 1 or (len(sin) == 1 and 'altri' not in sin):
        print()

    for key in sin:
        if key != 'altri':
            print(key, ", ".join(sin[key]))
    if 'altri' in sin:
        print("\nAltri sinonimi:", ", ".join(sin['altri']))

    print(f"\nCONTRARI di {word}")

    if len(con) == 0:
        print(f"Il dizionario non contiene ancora contrari di {word}")
    elif len(con) != 1 or (len(con) == 1 and 'altri' not in con):
        print()

    for key in con:
        if key != 'altri':
            print(key, ", ".join(con[key]))
    if 'altri' in con:
        print("\nAltri contrari:", ", ".join(con['altri']))

    print()

def parse(res):
    r = {}
    b = True
    for el in res:
        if el['class'][0] == 'search-results':
            if (el.p.get_text() if el.p else None) == f'Il dizionario non contiene ancora sinonimi di {word}':
                b = False

            for li in el.ol.findChildren('li') if el.ol else []:
                c = li.findChildren('span')
                r.setdefault(c[0].get_text(), []).extend(c[1].get_text().split(', '))

        elif el['class'][0] == 'listOthersTerms':
            r['altri'] = list(map(lambda x: x.get_text(), el.p.findChildren('a')))

    if b and list(r.keys()) == ['altri']:
        r['1.'] = r['altri']
        del r['altri']

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
obj = {'sin': parse(syn), 'con': parse(con), 'status': 'ok'}

if args.json:
    print(json.dumps(obj))
else:
    print_format(obj)
