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
from src import utils

import re
import os
import numpy as np
from collections import namedtuple

library_root = os.path.abspath(os.path.join(__file__, "../.."))

json_path = os.path.join(library_root, r'docs\formats.json')


# TODO logarithmic sampling of data.
def parse(filepath, formstyle):
    """Dispatches parsing responsibility to the function associated with the
    formstyle specified. Ideally styles and functions should be named after
    the lab instrument that produce them."""

    defined_formats = utils.load_formats_from_json(json_path)
    if formstyle in defined_formats:
        # dict of user-specified descriptions of the format.
        parameters = defined_formats[formstyle]

        # parse the file using user-specified parameters
        buf = parse_user_defined(filepath,
                                 parameters['data_start'],
                                 parameters['data_names'],
                                 parameters['extra_dimensions'],
                                 parameters['delimiter']
                                 )
    else:
        # evaluate the function of the associated formating style.
        # this can raise a NameError if the formstyle is undefined.
        buf = eval("parse_" + formstyle + "(filepath)")

    try:
        assert isinstance(buf, buffer.Buffer)
    except AssertionError:
        assert isinstance(buf, tuple), (
            "The parsing function for type {0} does not return a instance of a "
            "Buffer as defined in module buffer it currently returns {1}. "
            "You must edit the parse_{0) function in pysavuka/src/parse_funcs "
            "module to return a Buffer object.".format(formstyle)
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
        split_lines = [re.split(delimiter, line.strip('\n')) for line in f
                       if re.split(delimiter, line.strip('\n')) != ['']]
        f.close()
    return split_lines


def parse_user_defined(file_, data_start, data_names, extra_dimensions, delimiter):
    """Prompts user for relevant information about the file, and returns a
    Buffer object with the parsed data."""
    split_lines = convert_lines_to_list(file_, delimiter)

    # the actual thing we will return
    data = {}

    for idx, name in enumerate(data_names):  # how many dimension columns?
        # instantiate the Dimension objects with the correct name and no data
        data['dim' + str(idx)] = buffer.Dimension(None, name)

    for name, line_number in extra_dimensions.items():
        # get the value from the line specified from the user
        # (either first or second value on the line)
        dim_value = utils.find_number_on_line("".join(split_lines[line_number]))
        # add the value to our data object
        data['dim{0}'.format(len(data))] = buffer.Dimension(dim_value, name)

    for line in split_lines[data_start:]:  # from the first line of data onward
        for x in range(len(data_names)):  # for each column
            # add the value to the correct Dimension object
            data['dim{0}'.format(x)].append(utils.floatify(line[x]))

    return buffer.Buffer(data)


def lines_to_list(lines, column, start=0, stop=0):
    """Convert all the values in the given column from the lines into a
    single list."""
    if start == 0 and stop == 0:
        return [utils.floatify(line[column]) for line in lines]
    elif stop == 0:
        return [utils.floatify(line[column]) for line in lines[start:]]
    else:
        assert start < stop, ("start({0}) must be less than stop({1})"
                              "".format(start, stop))
        return [utils.floatify(line[column]) for line in lines[start:stop]]


def parse_v_vectors(file_):
    split_lines = convert_lines_to_list(file_, ',')

    # xs are the first column
    xs = lines_to_list(split_lines, 0)
    all_ys = []

    # skip the first column, because it is x
    for col in range(1, len(split_lines[0])):
        y_vals = lines_to_list(split_lines, col)
        all_ys.append(y_vals)

    list_of_buffers = []
    for i in range(len(all_ys)):
        buf = {'dim0': buffer.Dimension(xs, 'x'),
               'dim1': buffer.Dimension(all_ys[i], 'decomposed'),  # TODO name
               'file': file_,
               'format': 'v_vector'}
        buf = buffer.Buffer(buf)
        list_of_buffers.append(buf)

    return tuple(list_of_buffers)


def parse_v(file_):
    """Exactly the same as parse_v_vectors, but the first line is a header
    for some reason and not actual data."""
    split_lines = convert_lines_to_list(file_, ',')

    # xs are the first column, get rid of first value
    xs = lines_to_list(split_lines, 0, start=1)
    all_ys = []

    # skip the first column, because it is x
    for col in range(1, len(split_lines[1])):
        # get rid of first value in the column, it is a header
        y_vals = lines_to_list(split_lines, col, start=1)
        all_ys.append(y_vals)

    list_of_buffers = []
    for i in range(len(all_ys)):
        buf = {'dim0': buffer.Dimension(xs, 'x'),
               'dim1': buffer.Dimension(all_ys[i], 'decomposed'),  # TODO name
               'file': file_,
               'format': 'v_vector'}
        buf = buffer.Buffer(buf)
        list_of_buffers.append(buf)

    return tuple(list_of_buffers)


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
        xs = [utils.floatify(line[0]) for line in split_lines
              if utils.floatify(line[0]) is not None]

        # We slice d according to the length of xs because that's where the data
        # begins. This assumes for every x value there is a y. Also don't need
        # to check for None since there shouldn't be any after all the data.
        ys = [utils.floatify(line[1]) for line in split_lines[-len(xs):]]

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
                     'dim2': buffer.Dimension(utils.floatify(dim2[0]), dim2_name[0]),
                     'file': files,
                     'format': 'example'})

        return data_dict


def parse_applied_photophysics(files):

    with open(files) as f:
        split_lines = [re.split(',', line) for line in f]
        f.close()

        xs = [utils.floatify(line[0]) for line in split_lines
                         if utils.floatify(line[0]) is not None]

        ys = [utils.floatify(line[1]) for line in split_lines[-len(xs):]]

        assert len(xs) == len(ys), ("The data couldn't be parsed to match x "
                                    "and y values. This is probably caused by "
                                    "extra lines at the end of the file {0}" 
                                    "".format(files))

        return buffer.Buffer({
            'dim0': buffer.Dimension(xs, "Time-probably"),
            'dim1': buffer.Dimension(ys, "Intensity probably"),
            'dim2': buffer.Dimension(None, "definitely prompt user for this."),
            'file': files,
            'format': "applied photophysics"
        })


def parse_cd(file_):
    """DEPRECATED. Use the cd format as defined by the JSON file."""
    old_text = """Files will have the following format(space delimited):
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
        x_val = utils.floatify(line[0])
        if x_val:  # when data is encountered
            for idx, val in enumerate(line):  # for each column
                # convert the data and put it in the correct list
                data["dim{0}".format(idx)].append(utils.floatify(val))
        else:  # if not data, then some kind of metadata, save it's value.
            data[line[0]] = utils.floatify(line[1]) or line[1]

    buf = buffer.Buffer(data)

    return buf


