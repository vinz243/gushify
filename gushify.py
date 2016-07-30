#!/usr/bin/env python

import glob
import os.path
import re
from bencoder import bdecode
from switch import switch
import pprint
from collections import OrderedDict
import sys
import gutils

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

rows, columns = os.popen('stty size', 'r').read().split()

pp = pprint.PrettyPrinter(indent=4)
welcome_message = """
Thanks for using gushify! This script will help you clean your torrents.
Remember that none of selected actions (moving or deleting files...) will be
performed immediately but instead those changes will happen at the end.
"""
def run():
    print welcome_message
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
    storage_path = '/media/vincent/Stockage/Telechargements'
    files = gutils.walk(storage_path)[0:-1]
    print "This make take several minutes for large data sets.\n\n"
    file_match = {}
    widows = []
    unsure = 0
    for torrent in data:

        sys.stdout.write('.')
        sys.stdout.flush()

        name = torrent['torrent_name']
        file_match[name] = {}

        has_child = False
        need_validation = False

        for file_torrent in torrent['files']:
            has_one = False
            file_match[name][file_torrent] = []
            for file_dir in files:
                if file_dir.endswith(file_torrent) and not path_contains_hidden_dir(file_dir):
                    has_child = True
                    file_match[name][file_torrent].append(file_dir)

                    if has_one:
                        need_validation = True
                    has_one = True

        if not has_child:
            widows.append(name)
        if need_validation:
            unsure += 1
    # print file_match

    print '\n\n'+color.GREEN+'File matching finished.' + color.END
    print '\nThere are {0} widows out of {1} torrents (torrents without data)'.format(str(len(widows)), str(len(file_match.keys())))
    print 'And we have {0} unsure torrents (torrent with multiple file prentenders)'.format(str(unsure))

    if gutils.prompt_yes_no('Would you like to see widows? ', 'yes'):
        print ''
        counter = 0
        for widow in widows:
            counter += 2
            if counter > (int(rows) - 4):
                raw_input('')
            else:
                print ''
            print '  Torrent {0} is a widow.'.format(color.BOLD + widow + color.END)

    print '\nWhat do you wanna do with them? '
    print 'Nothing means program will forget them'
    print 'Delete means delete torrent file'
    print 'Match means asking this question for each widowed torrent'
    sleep(2)
    response = prompt_widow_action(file_match)

    counter_done = 0
    counter_errors = 1
    counter_torrents = len(file_match.keys())
    for widow in widows:
        # for file_torrent, file_dir in file_match[widow].iteritems():
        try:
            file_match.pop(widow)
            counter_done += 1
        except KeyError:
            counter_errors += 1
            print color.YELLOW + '\n  Non fatal error: Could not find key ' + widow + color.END + '\n'
    sys.stdout.write(color.GREEN +
        'Dropped {0} torrents out of {1}. {2} non-fatal errors raised!'.format(
            str(counter_done),
            str(counter_torrents),
            str(counter_errors)
        ) + color.END)
    sys.stdout.flush()


    print '\nOK widows done. Now let\'s move to unsure torrents'
    print 'Unsure torrents are files with several pretenders (file with same names)'

    for name, files in file_match.iteritems():
        do_print = True
        files_safe = []
        for file_torrent, files_dir in files.iteritems(): # first time to get only safe values
            if len(files_dir) == 1:
                files_safe.append(files_dir[0])

        for file_torrent, files_dir in files.iteritems():
            if len(files_dir) > 1:
                if do_print:
                    do_print = False
                    print color.BOLD + '\n  {0} has at least one file conflict:\n'.format(name) + color.END
                print '    Conflict for ./' + file_torrent + ':\n'
                best = find_most_likely_file(files_safe, files_dir, storage_path)
                index = 0
                best_index = -1
                files_dir.append('None')
                for file in files_dir:
                    if file == best:
                        print '      *{0}: {1}'.format(index, file)
                        best_index = index
                    else:
                        print '       {0}: {1}'.format(index, file)
                    index += 1

                choice = -1
                print ''
                while choice not in range(index):
                    sys.stdout.write('          Please enter your match: ')
                    sys.stdout.flush()
                    try:
                        input = raw_input().lower()
                        if input == '' or not input:
                            choice = best_index
                        else:
                            choice = int(input)
                    except ValueError:
                        choice = -1
                print ''



def find_most_likely_file(safe_files, pretenders, prefix=''):
    best_score = 0
    best_pretender = None
    for pret in pretenders:
        for file in safe_files:
            common = gutils.common_start(file, pret)
            score = len(common)
            if score > best_score:
                best_pretender = pret
                best_score = score
    return best_pretender


def prompt_widow_action(file_match):
    result = gutils.prompt_opts("", ['nothing', 'delete', 'match', 'cancel'], 'nothing')

    if result == 'nothing':
        print 'OK, forgetting widows...'
        print ''
        return 'nothing'
    elif result == 'cancel':
        if gutils.prompt_yes_no("\nAre you sure you want to quit program now?", "no"):
            print '\nBye bye...'
            exit(1)
        else:
            return prompt_widow_action(file_match)
    else:
        print 'Not implemented yet :(\n'
        return prompt_widow_action(file_match)

    # for name, matched in file_match.iteritems():
    #     print color.BLUE + name + ': ' + color.END
    #     for file_torrent, files_dir in matched.iteritems():
    #         print '  ' + color.BOLD + file_torrent + color.END
    #         for file_dir in files_dir:
    #             print '    ' + file_dir

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
                if gutils.prompt_yes_no('    Use misc category?', 'yes'):
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
    result = gutils.prompt_opts('    ', opts, torrent['assumed_category'])

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
        if gutils.prompt_yes_no("\nAre you sure you want to quit program now?", "no"):
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
