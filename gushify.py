#!/usr/bin/env python

import glob
import os.path
import re
from bencoder import bdecode
from switch import switch
import pprint
from collections import OrderedDict
import sys
class color:
   PURPLE = '\033[95m'
   CYAN = '\033[96m'
   DARKCYAN = '\033[36m'
   BLUE = '\033[94m'
   GREEN = '\033[92m'
   YELLOW = '\033[93m'
   RED = '\033[91m'
   BOLD = '\033[1m'
   UNDERLINE = '\033[4m'
   END = '\033[0m'


MUSIC_CAT = 'music'
UNKNOWN_CAT = 'unknown'

MATCHERS = [
    {
        'matcher': r'^(.*\.(flac|mp3|wav))|(cover\.jpg)$',
        'category': MUSIC_CAT,
        'name': 'music'
    },
    {
        'category': UNKNOWN_CAT,
    }
]


pp = pprint.PrettyPrinter(indent=4)
def run():
    working_dir = '/home/vincent/dump'
    torrents = glob.glob('{0}/*.torrent'.format(working_dir))

    for tor in torrents:

        report = parse_torrent(tor)

        sys.stdout.write('{0}{1}: {2}'.format(color.BOLD, report['name'], color.END))
        try:
            print '{0} of {1} files are {2} ({3}% accuracy)'.format(
                report['matched'],
                report['total'],
                report['assumed_category'],
                str(round(100 * float(report['matched'])/float(report['total']),2)),
            )
        except KeyError:
            print color.RED + 'no content found' + color.END



def removekey(d, *arg):
    r = dict(d)
    for key in arg:
        del r[key]
    return r

"""
Parses a torrent and returns a dict containing metadata
:param file: the path to the torrent file
"""
def parse_torrent(file):

    with open(file, "rb") as f:
        torrent = bdecode(f.read())
        torrent_name = torrent['info']['name']

        try:
            files = torrent['info']['files']
        except KeyError:
            # return {
            #     'name': torrent_name
            # }
            files = [{'path': [torrent_name]}]

        counter = populate_counter()

        for file in files:

            counter['globl'] += 1

            fname = file['path'][0]

            cat = file_cat(fname)
            counter[cat] += 1

            for case in switch(cat):
                if case(MUSIC_CAT):
                    break
                if case():
                    break

        without_unk = removekey(counter, UNKNOWN_CAT, 'globl')
        most_matched_cat = max(without_unk, key=without_unk.get)

        return {
            'matched': counter[most_matched_cat],
            'total': counter['globl'],
            'assumed_category': most_matched_cat,
            'name': torrent_name
        }


def populate_counter():
    counter = {
        'globl': 0
    }
    for m in MATCHERS:
        counter[m['category']] = 0
    return counter

def file_cat(name):
    try:
        for m in MATCHERS:
            if re.match(m['matcher'], name, re.M | re.I):
                return m['category']
    except KeyError:
        return UNKNOWN_CAT


run()
