#!/usr/bin/env python

import glob
import os.path
import re
from bencoder import bdecode
from switch import switch
import pprint
from collections import OrderedDict
import sys
from gutils import prompt_opts, prompt_yes_no, walk

import threading
from time import sleep

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
BOOK_CAT = 'book'
GAME_CAT = 'game'
MISC_CAT = 'misc'
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
        'name': 'software',
    },
    {
        'matcher': r'^((.*\.(mp4|mkv|avi|wmv|srt))|(.*((108|72)0p|x26(4|5))+.*))(\.r\d\d?)?$',
        'category': MOVIE_CAT,
        'name': 'movie'
    },
    {
        'matcher': r'^(.*\.(pdf|cbz|cbr|epub|mobi|opf))$',
        'category': BOOK_CAT,
        'name': 'book'
    },
    {
        'matcher': r'^(.*(pistolet|reloaded|skidrow).*)$',
        'category': GAME_CAT,
        'name': 'game'
    },
    {
        'matcher': r'^(.*\.(misc))$', # impossible matcher
        'category': MISC_CAT,
        'name': 'misc'
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
    data_parsed = []
    for tor in torrents:

        report = parse_torrent(tor)

        try:
            data_parsed.append({
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

    print ""
    print str(len(data_parsed)) + " torrents found. Next we are going to match them with content"


    match_data(data_parsed)


    # data_validated = validate_data(data_parsed)

def match_data(data):
    files = walk('/media/vincent/Stockage/Telechargements')[0:-1]
    print "This make take several minutes for large data sets.\n\n"
    file_match = {}
    widows = 0
    for torrent in data:

        sys.stdout.write('.')
        sys.stdout.flush()

        name = torrent['torrent_name']
        file_match[name] = {}

        for file_torrent in torrent['files']:
            file_match[name][file_torrent] = []
            for file_dir in files:
                if file_dir.endswith(file_torrent) and not path_contains_hidden_dir(file_dir):
                    file_match[name][file_torrent].append(file_dir)
        
    # print file_match

    print '\n'+color.GREEN+' File matching finished.' + color.END
    print '\nThere are {0} widows (torrents without data)'.format
    print '\n'

    for name, matched in file_match.iteritems():
        print color.BLUE + name + ': ' + color.END
        for file_torrent, files_dir in matched.iteritems():
            print '  ' + color.BOLD + file_torrent + color.END
            for file_dir in files_dir:
                print '    ' + file_dir

def validate_data(parsed_data):
    data_validated = []
    for tor in parsed_data:
        if tor['category_accuracy'] < high_treshold:
            sys.stdout.write('\n{0}{1}: {2}'.format(color.BOLD, tor['torrent_name'], color.END))
            print '{0} of {1} files are {2} ({3}% accuracy)'.format(
                tor['files_matched'],
                tor['files_total'],
                tor['assumed_category'],
                str(round(100 * tor['category_accuracy'],2)),
            )

            cat = prompt_torrent(tor)
            try:
                print '\n    Selected category: ' + color.GREEN + cat + color.END
            except TypeError:
                print '\n    Item skipped... This is usually not a good idea.'
                print '    You should definitely use misc category.'
                if prompt_yes_no('    Use misc category?', 'yes'):
                    cat = 'misc'
        else:
            cat = tor['assumed_category']

        data_validated.append({
            'category': cat,
            'name': tor['torrent_name'],
            'files': tor['files']
        })
    return data_validated



def prompt_torrent(torrent):
    print '\n    The accuracy treshold is not high enough to auto bind category'

    print '    Please categorize torrent yourself, you can enter first two chars\n'
    opts =  ['skip', 'list', 'cancel']
    for m in MATCHERS:
        try:
            opts.append(m['name'])
        except KeyError:
            pass
    result = prompt_opts('    ', opts, torrent['assumed_category'])

    if result == 'skip':
        return None
    elif result == 'list':
        print '\033[1;37m'

        files = torrent['files']

        # if len(files) > 9:
        #     files = files[0:7]
        #     files.append('...')

        for file in files:
            print '\t' + file

        print color.END

        return prompt_torrent(torrent)
    elif result == 'cancel':
        if prompt_yes_no("\nAre you sure you want to quit program now?", "no"):
            print '\nBye bye...'
            exit(1)
        else:
            return prompt_torrent(torrent)
    else:
        return result



def path_contains_hidden_dir(path):
    return re.match(r'^.*(\/\.).*$', path, re.I)

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
        if counter[most_matched_cat] == 0:
            most_matched_cat = 'misc'
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
