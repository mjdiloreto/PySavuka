import tkinter as tk
import itertools
from tkinter import filedialog
import re

from collections import Iterable


def get_filenames():
    """Prompt the user in a GUI for one or more file names."""
    file_path = filedialog.askopenfilenames()
    return file_path


def floatify(s):
    """Convert the string to a float, and return None if not possible."""
    try:
        return float(s)
    except ValueError:
        try:
            # for numbers like '1/3'
            return float(eval(s))
        except (ValueError, SyntaxError):
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
    """parse list syntax from "[1,2.4,3-6]" into [1, 2.4, 3, 4, 5, 6]
    Good for getting indices of buffers from user."""
    b = []

    for x in re.split(",|\[|\]", s):
        y = rangeify(x) or intify(x)
        if isinstance(y, Iterable):
            for z in y:
                b.append(z)
        else:
            if y is not None:
                b.append(y)
    return b


def get_filename():
    """Prompt the user in a GUI for a single file name."""
    root = tk.Tk()
    root.withdraw()
    file_path = filedialog.askopenfilename()
    return file_path


def eval_string(string):
    """return the proper python type of the object represented by the string,
    if it is in fact a string."""
    try:
        a = eval(string)
        return a
    except TypeError:
        return string


def eval_string_list(l):
    """return the proper python types of the objects represented by the list of
    strings, if they are in fact strings."""
    a = [eval_string(x) for x in l]
    return a


def parseline(line):
    """return a generator of all the arguments"""
    return tuple(arg for arg in re.split("\s", line))


def parseline2(line, command):
    """for the given line, associate parameters to the corresponding
    options, defaulting the name of the command.
    e.g. parseline('a b -i c', 'command') should return
        {'command' : [a, b], 'i' ; [c]}

    takes in line param from cmd.Cmd"""

    opt = command
    matched = {}
    # split the line by spaces not preceded by commas
    # to account for any parameters that are tuples
    for idx, x in enumerate(re.split("(?<!,)\s", line)):
        # check for options to the command (anything preceded by '-'
        if re.match('-+[a-z]', x):
            opt = x.strip('-')

        # match params to their given options
        else:
            if opt not in matched:
                matched[opt] = [x]
            else:
                matched[opt].append(x)
    return matched


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

