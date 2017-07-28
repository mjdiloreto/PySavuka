import re
import json
import sys

from collections import Iterable
from PyQt5.QtWidgets import QApplication, QWidget, QFileDialog


def ask_for_files():
    # TODO Should I close these applications?
    app = QApplication(sys.argv)

    files, _ = QFileDialog.getOpenFileNames(QWidget(), "Select data files",
                                            "", "All Files (*)")
    return files


def find_number_on_line(line):
    """return the first occurrence of a decimal number in a string.
    Works for scientific notation as well.
    e.g. 'This is the line and the value is 1.00E-9'
    will be converted to the floating-point number 1.00E-9"""
    matches = re.findall(line, r'[0-9]+\.[0-9]+((e|E)(\+|\-)[0-9]+)?')
    return floatify(matches[0])


def load_formats_from_json(file_):
    with open(file_, 'r') as f:
        data = json.load(f)
        f.close()
    return data


def save_formats_to_json(file_, name, obj):
    with open(file_, 'r') as f:
        # load in what already exists
        data = json.load(f)
        f.close()

    # assign the new object its name, overwrite if necessary
    data[name] = obj

    with open(file_, 'w') as f:
        # save it back to the same file
        json.dump(data, f, ensure_ascii=False)
        f.close()


def floatify(s):
    """Convert the string to a float, and return None if not possible."""
    try:
        return float(s)
    except ValueError:
        try:
            # for numbers like '1/3', they first have to be evaluated
            return float(eval(s))
        except (ValueError, SyntaxError, TypeError):
            return


def intify(s):
    """Convert the string to an int, and return None if not possible."""
    try:
        return int(s)
    except ValueError:
        return


def rangeify(s):
    """Convert <int1-int2> into [int1, int1.1, int1.2, int1.3, ..., int2], and
    return None if not possible"""
    try:
        bounds = re.split("-", s)
        return tuple(range(intify(bounds[0]), intify(bounds[1])+1))
    except IndexError:
        return


def parse_buffers(line):
    """Creates a list of buffers entered by the use, either in the form
    <0 1 3 4>, or <0-1 3-4>. Both will return [0,1,3,4]"""
    a = []
    # TODO come back and make this clever damn it.
    for x in re.split("\s", line):
        if intify(x):
            a.append(intify(x))
        elif rangeify(x):
            for y in rangeify(x):
                a.append(intify(y))

    return a


def string_to_numbers(s):
    """Convert the string of space separated numbers into a list of numbers"""
    return [intify(x) or floatify(x) for x in re.split("\s", s)]


def string_to_index_list(s):
    """parse list syntax from "[1,2.4,3-6]" into [1, 3, 4, 5, 6]
    Good for getting indices of buffers from user. Notice no floats."""
    b = []

    for x in re.split(",|\[|\]", s):
        if rangeify(x) is not None:
            b.extend(rangeify(x))
        elif intify(x) is not None:
            b.append(intify(x))

    return b


def eval_string(string):
    """return the proper python type of the object represented by the string,
    if it is in fact a string."""
    try:
        a = eval(string)
        return a
    except (TypeError, NameError):  # it really is a string after all
        return string


def eval_string_list(l):
    """return the proper python types of the objects represented by the list of
    strings, if they are in fact strings."""
    a = [eval_string(x) for x in l]
    return a


def parseline(line):
    """return a generator of all the arguments"""
    return tuple(arg for arg in re.split("\s", line))


def parse_options(line):
    """for the given line, associate parameters to the corresponding
    options, defaulting to 'arg'. Also, evaluate things like numbers to
    their correct types.
    e.g.    parseline('a b -i c') should return
            {'arg' : [a, b], 'i' : [c]}
        so commands of form
            'do_something arg1 arg2 -option x y -option2 z'
        will be parsed as:
            {args: [arg1, arg2],
             option: [x, y],
             option2: [z]}

    takes in line param from cmd.Cmd"""

    # anything before the first option will simply be an argument.
    opt = 'args'
    matched = {'args': []}
    # split the line by spaces
    for x in re.split("\s", line):
        # check for options to the command (anything preceded by '-'
        if re.match('-+[a-z]', x):
            # initiallze it in the dictionary as an empty list
            opt = x.strip('-')
            matched[opt] = []

        # match params to their given options
        else:
            matched[opt].append(eval_string(x))

    return matched


def print_helps(mod):
    """Prints all the help texts (__doc__ aka triple-quoted strings under
    each function) from module"""
    helps = []

    # everything in the module, classes, functions, variables, etc.
    for name in mod.__dict__.values():
        if callable(name):  # it is a function
            helps.append(name.__doc__)

    return helps


# Which parameter is responsible for which exception?
def check_input(exceptions_and_params={}):
    """Decorator that tries to run each decorated function with the given
    parameters, and if it fails, determines which parameter failed, and reruns
    the function with a new input.

    Any method decorated with this function can pass a dictionary of exceptions
    and the index of the corresponding arg (0 for the first argument, 1 for
    the second, etc.), or the name of the kwarg."""

    def decorator(f):

        # TODO don't force user to input new param. let them quit
        # wraps the function whose input will be checked.
        def wrapper(*args, **kwargs):
            try:
                f(*args, **kwargs)
            except Exception as e:
                rerun(e, *args, **kwargs)

        # get new params based on exception and rerun f until it doesn't break.
        def rerun(e, *args, **kwargs):
            try:
                # Which parameter resulted in the exception?
                param = exceptions_and_params[e.__class__]
            except KeyError:
                print("One of the parameters used with the command resulted in"
                      " the error:\n\n{0} {1} \n\n"
                      "try new parameters.".format(e.__class__, e))
                return
            try:
                # first call should break if second will. Before asking for data
                arg = kwargs[param]
                kwargs[param] = input("The specified kwarg <{0}> resulted in "
                                      "the error\n{1}: {2}.\nTry again: "
                                      "".format(arg, e.__class__, e))
            # If param isn't in kwargs it must be an integer
            except KeyError:
                print(args)
                arg = args[param]

                # we need to call the function again with new params
                temp_list = list(args)
                temp_list[param] = input("The specified arg <{0}> resulted in "
                                         "the error\n{1}: {2}.\nTry again: "
                                         "".format(arg, e.__class__, e))

                # args is always a tuple.
                args = tuple(temp_list)

            wrapper(*args, **kwargs)

        return wrapper

    return decorator

