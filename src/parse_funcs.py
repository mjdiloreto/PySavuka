"""This file contains the functions used to parse data into python lists.
Each lab instrument used with the software should have its own associated
parsing function.

Each function should return a single dictionary, whose keys correspond to
the names of the parsed data, and whose values correspond to the data itself.

For example, any 'parse_*' function should return something like:
{'dim0': Dimension([1.00, 1.10,...,10.00], 'time'),
 'dim1': Dimension([2.13, 3.02, ... 35.67], 'intensity'])
 'dim2': Dimension(1.00, 'urea'),
 'dim4': Dimension(1.00, 'protein'),
 'filename': 'C:\\Users\\...\\data.txt' I have to escape the slashes in comments
 'format': 'example'

There is no limit to the amount of metadata that can be stored in the
dictionary, because specific routines will only require certain fields like
dim0, dim1, etc."""
from src import buffer
from src.utils import floatify, intify

import re
import numpy as np
from collections import namedtuple


# TODO make general case file reader?
# TODO maybe define parameterized reading:>
# delimeter, columns(can be a range), logarithmic sampling, what the columns mean, if the user needs to be prompted for the column interpretation for each column.
def parse(filepath, formstyle):
    """Dispatches parsing responsibility to the function associated with the
    formstyle specified. Ideally styles and functions should be named after
    the lab instrument that produce them."""

    # evaluate the function of the associated formating style.
    # this can raise a NameError if the formstyle is undefined.
    buf = eval("parse_" + formstyle + "(filepath)")

    assert isinstance(buf, buffer.Buffer), (
        "The parsing function for type {0} does not return a instance of a "
        "Buffer as defined in module buffer it currently returns {1}. You must "
        "edit the parse_{0) function in pysavuka/src/parse_funcs module to "
        "return a Buffer object.".format(formstyle)
    )

    return buf

def convert_lines_to_list(file_, delimiter = ','):
    """Open the file, convert it to a list of tuples that represent the items
    on each line of the file delimited by the delimiter.
    e.g.

    1.00, 2.00, 3.00
    4.00, 5.00, 6.00

    gets converted to [(1.00, 2.00, 3.00), (4.00, 5.00, 6.00)]"""

    with open(file_) as f:
        split_lines = [re.split(delimiter, line) for line in f]
        f.close()
    return split_lines


def parse_user_defined(file_, data_start, data_names, extra_dimensions, uses_tabs):
    """Prompts user for relevant information about the file, and returns a
    Buffer object with the parsed data."""
    if uses_tabs:
        split_lines = convert_lines_to_list(file_, delimiter='\t')
    else:
        split_lines = convert_lines_to_list(file_)

    # the actual thing we will return
    data = buffer.Buffer()

    for idx, name in enumerate(data_names):  # how many dimension columns?
        # instantiate the Dimension objects with the correct name and no data
        data['dim' + str(idx)] = buffer.Dimension(None, name)

    for name, line_number in extra_dimensions.items():
        # get the value from the line specified from the user
        # (either first or second value on the line)
        dimension_data = (floatify(split_lines[line_number][0])
                          or floatify(split_lines[line_number[1]]))
        # add the value to our data object
        data['dim{0}'.format(len(data))] = buffer.Dimension(dimension_data, name)

    for line in split_lines[data_start:]:  # from the first line of data onward
        for x in range(len(data_names)):  # for each column
            # add the value to the correct Dimension object
            data['dim{0}'.format(x)].append(floatify(line[x]))

    return data



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
        f.close()

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

        assert len(xs) == len(ys), ("The data couldn't be parsed to match x "
                                    "and y values. This is probably caused by "
                                    "extra lines at the end of the file {0}" 
                                    "".format(files))

        # match something preceded by '=' and 0 or more spaces,
        # containing 1 or more digits, a '.'  then followed by 1 or more digits.
        # This will match '1.00' in the string '$$urea=1.00' and assumes
        # The first line contains the value of the third dimension.
        dim2 = re.findall('(?<==)[0-9]+\.[0-9]+', split_lines[0][0])

        # The name of the dimension preceding dim2. In above example, 'urea'
        dim2_name = re.findall('[a-z]+(?==)', split_lines[0][0])

        # show what we put into the Buffer object for visual purposes.
        # create a Buffer object. It's just like a regular dictionary, but
        # includes functionality specific to the behavior expected from xy pairs
        # of data
        data_dict = buffer.Buffer({'dim0': buffer.Dimension(xs, 'x'),
                     'dim1': buffer.Dimension(ys, 'y'),
                     # findall returns a list
                     'dim2': buffer.Dimension(floatify(dim2[0]), dim2_name[0]),
                     'file': files,
                     'format': 'example'})

        return data_dict


def parse_applied_photophysics(files):

    with open(files) as f:
        split_lines = [re.split(',', line) for line in f]
        f.close()

        xs = np.asarray([floatify(line[0]) for line in split_lines
                         if floatify(line[0]) is not None])

        ys = np.asarray([floatify(line[1]) for line in split_lines[-len(xs):]])

        assert len(xs) == len(ys), ("The data couldn't be parsed to match x "
                                    "and y values. This is probably caused by "
                                    "extra lines at the end of the file {0}" 
                                    "".format(files))

        #TODO what do the x and y represent, and where is the z value? prompt?
        #TODO allow for aliasing of the function name. Don't want to remember this super long name.
        return buffer.Buffer({
            'dim0': buffer.Dimension(xs, "Time-probably"),
            'dim1': buffer.Dimension(ys, "Intensity probably"),
            'dim2': buffer.Dimension(None, "definitely prompt user for this."),
            'file': files,
            'format': "applied photophysics"
        })


def parse_cd(file_):
    """Files will have the following format(space delimited):
        X_UNITS NANOMETERS
        Y_UNITS CD[mdeg]
        Y2_UNITS HT[V]  # can have abitrarily many ys
        UREA 1.00  # and arbitrarily many other dimensions
        300.0000, -0.258226, 316.753
        299.0000, -0.233598, 317.105
        298.0000, -0.223822, 317.478
        ...
        ...

        There should NEVER be any information after the data.
        """
    split_lines = None
    data = {}

    with open(file_) as f:
        split_lines = [re.split('\s', line) for line in f]
        f.close()

    """Because there should never be any information after the data,
    the last line is used as a sentinel to tell the function how many
    data columns there are in the data."""
    num_columns = len(split_lines[-1])
    for column_number in range(num_columns):
        # The key for the data is dim0 dim1 dim2, etc.
        data["dim{0}".format(column_number)] = buffer.Dimension()

    for line in split_lines:
        x_val = floatify(line[0])
        if x_val:  # when data is encountered
            for idx, val in enumerate(line):  # for each column
                # convert the data and put it in the correct list
                data["dim{0}".format(idx)].append(floatify(val))
        else:  # if not data, then some kind of metadata, save it's value.
            data[line[0]] = floatify(line[1]) or line[1]

    # TODO associate X_UNITS, Y_UNITS
    buf = buffer.Buffer(data)

    return buf


