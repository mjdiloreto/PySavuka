"""This file contains the functions used to parse data into python lists.
Each lab instrument used with the software should have its own associated
parsing function.

Each function should return a single dictionary, whose keys correspond to
the names of the parsed data, and whose values correspond to the data itself.

For example, any 'parse_*' function should return something like:
{'dim1': Dimension([1.00, 1.10,...,10.00], 'time'),
 'dim2': Dimension([2.13, 3.02, ... 35.67], 'intensity'])
 'dim3': Dimension(1.00, 'urea'),
 'dim4': Dimension(1.00, 'protein'),
 'filename': 'C:\\Users\\...\\data.txt' I have to escape the slashes in comments
 'format': 'example'

There is no limit to the amount of metadata that can be stored in the
dictionary, because specific routines will only require certain fields like
dim1, dim2, etc."""

import re
import numpy as np
from collections import namedtuple

# Define a new type of data, which is a container called 'Dimension'
# That will be used to store all parsed data and the name of that data.
# For example, if measuring light intensity over time, the data would be parsed
# into 2 dimensions, one with the name 'intensity' and the y data from the
# experiment, and another called 'time' with the x data.

# This structure is used in each dictionary returned by these parse_funcs
# as the values to the keys named 'dim1','dim2',etc.
# new Dimension instances are made via: Dimension([...],'name')
Dimension = namedtuple('Dimension', ['data', 'name'])


def parse(filepath, formstyle):
    """Dispatches parsing responsibility to the function associated with the
    formstyle specified. Ideally styles and functions should be named after
    the lab instrument that produce them."""

    # evaluate the function of the associated formating style.
    # this can raise a NameError if the formstyle is undefined.
    return eval("parse_" + formstyle + "(filepath)")


def floatify(s):
    """Convert the string to a float, and return None if not possible."""
    try:
        return float(s)
    except ValueError:
        return


def parse_example(files):
    """Parse the format specified by ../docs/xyexample1.txt
    Return the dictionary of parsed data as Dimension instances and metadata."""
    with open(files) as f:
        split_lines = [re.split(',', line) for line in f]

        # This shouldn't ever fail, since the list of lines will always contain
        # something, even if it's just ''
        # This assumes that the first number encountered at the beginning of
        # a line is in fact an x value.
        xs = [floatify(line[0]) for line in split_lines
              if floatify(line[0]) is not None]
        xs = np.asarray(xs)

        # We slice d according to the length of xs because that's where the data
        # begins. This assumes for every x value there is a y. Also don't need
        # to check for None since there shouldn't be any after all the data.
        ys = [floatify(line[1]) for line in split_lines[-len(xs):]]
        ys = np.asarray(ys)

        assert len(xs) == len(ys), "" \
            "The data couldn't be parsed to match x and y values. This is " \
            "probably caused by extra lines at the end of the file {0}" \
            "".format(files)

        # match something preceded by '=' and 0 or more spaces,
        # containing 1 or more digits, a '.'  then followed by 1 or more digits.
        # This will match '1.00' in the string '$$urea=1.00' and assumes
        # The first line contains the value of the third dimension.
        dim3 = re.findall('(?<==)[0-9]+\.[0-9]+', split_lines[0][0])

        # The name of the dimension preceding dim3. In above example, 'urea'
        dim3_name = re.findall('[a-z]+(?==)', split_lines[0][0])

        # data can be accessed by: data_dict.get('key').data
        data_dict = {'dim1': Dimension(xs, 'x'),
                     'dim2': Dimension(ys, 'y'),
                     # findall returns a list
                     'dim3': Dimension(dim3[0], dim3_name[0]),
                     'filename': files,
                     'format': 'example'}

        return data_dict


def parse_example1(files):
    """works for all files composed of lines matching the form:
     .0000000E+00 ,  .0000000E+00
     where the first expression represents the x value, and the second
     the y value.

     assumes the format will be EXACTLY the same each time."""

    # TODO make this faster.
    with open(files) as f:
        read = [line for line in f]
        xs = [float(line[3:11]) * (10 ** int(line[14:15]))
              for line in read[3:]]
        ys = [float(line[19:27]) * (10 ** int(line[30:31]))
              for line in read[3:]]
    '''
    names = {dim1: 'urea', dim2: 'protein'}

    d = {dim1: x, din2: y, dim3: urea}

    return d, names

    return {urea: z, x: xs, y: ys, err, ir}'''

    return xs, ys
