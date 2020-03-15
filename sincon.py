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
__version__ = '1.1'

import re
import requests
import sys
import bs4

WEBSITE = "https://www.sinonimi-contrari.it/"

def print_format(res):
    for el in res:
        if el['class'][0] == 'search-results':
            print(re.sub(r'\.$', '', # toglie i punti alla fine, fastidiosi quando si copia una parola
                         re.sub(r'(lett\.|sm\.|[A-Z]\w+\.|\d+\.)', r'\n\1 ', el.get_text()), # divide in righe le varie definizioni
                         flags=re.M))
            print()
        elif el['class'][0] == 'listOthersTerms':
            print(re.sub(r'\.$', '',
                         re.sub(r':', r': ', el.get_text()),
                         flags=re.M))
            print()

def split_syncon(tags):
    for i in range(len(tags)):
        if tags[i].name == 'hr':
            syn = tags[:i]
            con = tags[i+1:]
            break
    if 'syn' not in locals():
        print("La parola cercata non esiste nel dizionario", file=sys.stderr)
        exit(1)

    return (syn[1:], con[1:])

if len(sys.argv) != 2:
    print(f"Utilizzo: {sys.argv[0]} PAROLA")
    exit(1)

word = sys.argv[1]

r = requests.get(WEBSITE+word)
tags = bs4.BeautifulSoup(r.text, 'html.parser').find('div', {'class': 'termWrap'}).find_all(recursive=False)

syn, con = split_syncon(tags)

print(f"\nSINONIMI di {word}")
print_format(syn)

print(f"CONTRARI di {word}")
print_format(con)
