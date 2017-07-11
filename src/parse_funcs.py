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
from src import buffer
from src.utils import floatify

import re
import numpy as np
from collections import namedtuple


def parse(filepath, formstyle):
    """Dispatches parsing responsibility to the function associated with the
    formstyle specified. Ideally styles and functions should be named after
    the lab instrument that produce them."""

    # evaluate the function of the associated formating style.
    # this can raise a NameError if the formstyle is undefined.
    buf = eval("parse_" + formstyle + "(filepath)")

    assert isinstance(buf, buffer.Buffer), "The parsing function for type {0}" \
        "does not return a instance of a Buffer as defined in module buffer" \
        "it currently returns {1}. You must edit the parse_{0) function in " \
        "pysavuka/src/parse_funcs module to return a Buffer object."

    return buf




def parse_example(files):
    """Parse the format specified by ../docs/xyexample1.txt
    Return the Buffer(a dictionary) of the data and metadata.
    All data should be parsed in the form:
    {
    'dimx': Dimension(numpy.array(...), string)
    }
    metadata can be in any form, as long as the subroutines that require access
    to them address them by the correct name in the Buffer object."""

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

        # show what we put into the Buffer object for visual purposes.
        data_dict = {'dim1': buffer.Dimension(xs, 'x'),
                     'dim2': buffer.Dimension(ys, 'y'),
                     # findall returns a list
                     'dim3': buffer.Dimension(floatify(dim3[0]), dim3_name[0]),
                     'filename': files,
                     'format': 'example'}

        # create a Buffer object. It's just like a regular dictionary, but
        # includes functionality specific to the behavior expected from xy pairs
        # of data
        data_dict = buffer.Buffer(data_dict)

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
