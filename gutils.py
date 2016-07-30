import sys

def prompt_yes_no(question, default="yes"):
    """Ask a yes/no question via raw_input() and return their answer.

    "question" is a string that is presented to the user.
    "default" is the presumed answer if the user just hits <Enter>.
        It must be "yes" (the default), "no" or None (meaning
        an answer is required of the user).

    The "answer" return value is True for "yes" or False for "no".
    """
    valid = {"yes": True, "y": True, "ye": True,
             "no": False, "n": False}
    if default is None:
        prompt = " [y/n] "
    elif default == "yes":
        prompt = " [Y/n] "
    elif default == "no":
        prompt = " [y/N] "
    else:
        raise ValueError("invalid default answer: '%s'" % default)

    while True:
        sys.stdout.write(question + prompt)
        choice = raw_input().lower()
        if default is not None and choice == '':
            return valid[default]
        elif choice in valid:
            return valid[choice]
        else:
            sys.stdout.write("Please respond with 'yes' or 'no' "
                             "(or 'y' or 'n').\n")
def prompt_opts(question, options, default=None):
    """Ask a multiple choice question

    "question" is a string that is presented to the user.
    "options is a dict with for each keyassociates a value
    "default" is the presumed answer if the user just hits <Enter>.
        It must be "yes" (the default), "no" or None (meaning
        an answer is required of the user).

    """
    keys = []
    for key in options:
        if key == default:
            keys.append('\033[1m' + key + '\033[0m')
        else:
            keys.append(str(key))
    prompt = " [{0}] ".format('/'.join(keys))

    while True:
        sys.stdout.write(question + prompt)
        choice = raw_input().lower()
        if default is not None and choice == '':
            return default
        elif choice in options:
            return choice
        else:
            if len(choice) > 1:
                for key in options:
                    if key.startswith(choice):
                        return key
            sys.stdout.write("Please respond with provided options\n\t")

import os

def walk(dir):
    files = []
    for dirname, dirnames, filenames in os.walk(dir):
        # print path to all subdirectories first.
        for subdirname in dirnames:
            files.append(os.path.join(dirname, subdirname))

        # print path to all filenames.
        for filename in filenames:
            files.append(os.path.join(dirname, filename))

        # Advanced usage:
        # editing the 'dirnames' list will stop os.walk() from recursing into there.
        if '.git' in dirnames:
            # don't go into any .git directories.
            dirnames.remove('.git')
    return files



def long_substr(data):
    substr = ''
    if len(data) > 1 and len(data[0]) > 0:
        for i in range(len(data[0])):
            for j in range(len(data[0])-i+1):
                if j > len(substr) and is_substr(data[0][i:i+j], data):
                    substr = data[0][i:i+j]
    return substr

def is_substr(find, data):
    if len(data) < 1 and len(find) < 1:
        return False
    for i in range(len(data)):
        if find not in data[i]:
            return False
    return True

import sys
def common_start(sa, sb):
    """ returns the longest common substring from the beginning of sa and sb """
    def _iter():
        for a, b in zip(sa, sb):
            if a == b:
                yield a
            else:
                return

    return ''.join(_iter())


# spinner()
# #
# while True:
#     print 'returned: ' + gutils.prompt_opts('Fuck you?', [
#         'yes',
#         'maybe',
#         'no',
#         'pls'])
