import tkinter as tk
from tkinter import filedialog
import re


def get_filenames():
    """Prompt the user in a GUI for one or more file names."""
    root = tk.Tk()
    root.withdraw()
    file_path = filedialog.askopenfilenames()
    return file_path


def get_filename():
    """Prompt the user in a GUI for a single file name."""
    root = tk.Tk()
    root.withdraw()
    file_path = filedialog.askopenfilename()
    return file_path


def eval_string(string):
    """return the proper python type of the object represented by the string,
    if it is in fact a string."""
    a = string
    try:
        a = eval(string)
    except TypeError:
        pass
    return a


def eval_string_list(l):
    """return the proper python types of the objects represented by the list of
    strings, if they are in fact strings."""
    a = [eval_string(x) for x in l]
    return a


def parseline(line, command):
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
    and the index of the corresponding arg, or the name of the kwarg."""

    def decorator(f):

        # wraps the function whose input will be checked.
        def wrapper(self, *args, **kwargs):
            try:
                f(self, *args, **kwargs)
            except Exception as e:
                rerun(self, e, *args, **kwargs)

        # get new params based on exception and rerun f until it doesn't break.
        def rerun(self, e, *args, **kwargs):
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
                kwargs[param] = input("The specified kwarg {0} resulted in the"
                                      " error\n{1}: {2}.\nTry again: "
                                      "".format(arg, e.__class__, e))
            # If param isn't in kwargs it must be an integer
            except KeyError:
                arg = args[param]

                # we need to call the function again with new params
                temp_list = list(args)
                temp_list[param] = input("The specified arg {0} resulted in the"
                                         " error\n{1}: {2}.\nTry again: "
                                         "".format(arg, e.__class__, e))

                # args is always a tuple.
                args = tuple(temp_list)

            wrapper(self, *args, **kwargs)

        return wrapper

    return decorator


def print_dimension_dict(data_dict, *args, **kwargs):
    # Todo generalize this for dataobject, or do __repr__
    print("parsed {0} values for {1}={2} ===> [{3}, {4}, ..., {5}, {6}]"
          "".format(data_dict.get('dim1').name,
                    data_dict.get('dim3').name,
                    data_dict.get('dim3').data,
                    data_dict.get('dim1').data[0],
                    data_dict.get('dim1').data[1],
                    data_dict.get('dim1').data[-2],
                    data_dict.get('dim1').data[-1]))

    print("parsed {0} values for {1}={2} ===> [{3}, {4}, ..., {5}, {6}]"
          "".format(data_dict.get('dim2').name,
                    data_dict.get('dim3').name,
                    data_dict.get('dim3').data,
                    data_dict.get('dim2').data[0],
                    data_dict.get('dim2').data[1],
                    data_dict.get('dim2').data[-2],
                    data_dict.get('dim2').data[-1]))
