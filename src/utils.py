import re
import json
import sys
import traceback

from collections import Iterable
from PyQt5.QtWidgets import QApplication, QWidget, QFileDialog


def ask_for_files():
    """Pull up a gui to prompt user for files. Works cross-platform"""
    app = QApplication(sys.argv)

    files, _ = QFileDialog.getOpenFileNames(QWidget(), "Select data files",
                                            "", "All Files (*)")

    # app should probably be closed here.
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
    except (ValueError, SyntaxError, TypeError):
        return

def range_to_tuple(s):
    """Convert a string in the form (int, int, int-int, int) to a tuple
    containing all values in the tuple AND in the range int-int."""
    # This check is vital. If it is not here, plain integers are converted to tuples,
    # so it would be impossible to pass savuka an integer.
    if not s.startswith("("):
        raise TypeError("Ranges must start with parens")

    # make a list of the values in the tuple, getting rid of leading and
    # trailing parenthesis.
    all_vals = [x for x in re.split(",|\(|\)", s) if x != '']
    # convert int-int to a tuple of ints in the range, leave single ints alone
    final = []
    for val in all_vals:
        x = rangeify(val)
        if x is not None:
            final.extend(x)
        else:
            final.append(intify(val))

    if not final: # User gave no arguments. final is ()
        raise TypeError("No arguments given to range_to_tuple")

    return tuple(final)

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
    if it is in fact a string. Also convert things in 'range' syntax to tuples"""
    try:  # it might be a 'range'. Have to check this first.
        return range_to_tuple(string)
    except (TypeError, NameError, SyntaxError):
        try:
            return eval(string)
        except (TypeError, NameError, SyntaxError):  # if it really is a string after all
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
    """For the given line, separate arguments into either args or kwargs,
    depending on whether they are preceded by '-option'.
    E.g.
    parse_option('0 1 -option yes -option2 no')
    -> args = (0, 1)
       kwargs = {option: yes, option2: no}

    All entries are converted to their proper python types as well.
    i.e. 0 is int(0) not '0'.

    Also! convert things in the 'range' syntax, i.e. (int,int,int-int,int)
    to a tuple containing all numbers in the range.
    See utils.range_to_tuple
    """

    # anything before the first option will simply be an argument.
    add_to_args = True  # have we not encountered an -option yet?
    args = []
    kwargs = {}
    # split the line by spaces
    for x in re.split("\s", line):
        # check for options to the command (anything preceded by '-'
        if re.match('-+[a-z]', x):
            # initialize it in the dictionary as an empty list
            add_to_args = False
            opt = x.strip('-')
            kwargs[opt] = []
        # Have we still not seen an option?
        elif add_to_args:
            evaluated = eval_string(x)
            if evaluated:  # don't add '' (no arguments given)
                args.append(evaluated)
        # match params to their given options
        else:
            kwargs[opt].append(eval_string(x))

    return args, kwargs


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


def except_all(f):
    """wrapper for cmd.Cmd methods that keeps the program running,
     in spite of errors"""

    def wrapper(*args, **kwargs):
        try:
            return f(*args, **kwargs)
        except:  # except any error that might occur
            # print the error, keeping program open
            traceback.print_exc(file=sys.stdout)

    return wrapper

