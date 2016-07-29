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
MOVIE_CAT = 'movie'
SOFTWARE_CAT= 'software'
BOOK_CAT = 'books'
UNKNOWN_CAT = 'unknown'

IGNORE_MATCHER = r'^(.*\.(nfo|jpg|txt))$'

MATCHERS = [
    {
        'matcher': r'^(.*\.(flac|mp3|wav))$',
        'category': MUSIC_CAT,
        'name': 'music'
    },
    {
        'matcher': r'^(.*\.(exe|dll|bin|zip|ini|cfg|iso|sys|sig|db|xml|cab|inf|chm|bat|reg|pima|pimx|zdct))$',
        'category': SOFTWARE_CAT,
        'name': 'software'
    },
    {
        'matcher': r'^((.*\.(mp4|mkv|avi|wmv|srt))|(.*((108|72)0p|x26(4|5))+.*))(\.r\d\d?)?$',
        'category': MOVIE_CAT,
        'name': 'movie'
    },
    {
        'matcher': r'^(.*\.(pdf|cbz|cbr|epub|mobi|opf))$',
        'category': BOOK_CAT,
        'name': 'books'
    },
    {
        'category': UNKNOWN_CAT,
    }
]

high_treshold = 0.7


pp = pprint.PrettyPrinter(indent=4)
def run():
    working_dir = '/home/vincent/dump'
    torrents = glob.glob('{0}/*.torrent'.format(working_dir))
    parsed_data = []
    for tor in torrents:

        report = parse_torrent(tor)

        try:
            parsed_data.append({
                'files_matched': report['matched'],
                'files_total': report['total'],
                'assumed_category': report['assumed_category'],
                'torrent_name': report['name'],
                'category_accuracy': float(report['matched'])/float(report['total']),
                'files': report['files']
            })

        except KeyError:
            sys.stdout.write('{0}{1}: {2}'.format(color.BOLD, report['name'], color.END))
            print color.RED + 'Invalid torrent' + color.END

    for tor in parsed_data:
        if tor['category_accuracy'] < high_treshold:
            sys.stdout.write('{0}{1}: {2}'.format(color.BOLD, tor['torrent_name'], color.END))
            print '{0} of {1} files are {2} ({3}% accuracy)'.format(
                tor['files_matched'],
                tor['files_total'],
                tor['assumed_category'],
                str(round(100 * tor['category_accuracy'],2)),
            )

            print '\033[1;37m'
            for file in tor['files']:
                print '\t' + file
            print color.END



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
        # print files
        counter = populate_counter()
        report_files = []
        for file in files:

            fname = '/'.join(file['path'])

            report_files.append(fname)
            if not is_ignored(fname):
                cat = file_cat(fname)
                counter['globl'] += 1

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
            'name': torrent_name,
            'files': report_files
        }

def is_ignored(name):
    return re.match(IGNORE_MATCHER, name, re.M | re.I)
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
