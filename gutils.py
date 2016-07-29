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
            keys.append(key.title())
        else:
            keys.append(key)
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
# #
# while True:
#     print 'returned: ' + prompt_opts('Fuck you?', [
#         'yes',
#         'maybe',
#         'no',
#         'pls'])
