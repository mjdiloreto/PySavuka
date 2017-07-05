"""This file contains the Savuka class, which is used in the cli.py module
as the context object for the program. It contains all data parsed by the
user, and methods to analyze that data."""

from src import parse_funcs
from src import plot_funcs
from src import utils

import numpy as np


def update_buffer(f):
    """Mutates the data in self.data according to buffer index/name and
    axis returned by the decorated function. The first argument after self
    to any decorated function must be the singular buffer being mutated.

    Intended to decouple self.data implementation details from the methods
    of the Savuka class."""

    def wrapper(self, buffer_index, *args, **kwargs):

        # if no kwarg 'axis' provided, defaults to mutating y values.
        axis = kwargs.get('axis')

        # all access to data is done through this function. Each data
        # manipulation methods of Savuka class takes in this 'buf' argument.
        buf = self.get_buffers(buffer_index)[axis_to_index(axis)]

        # calculation
        new_data = f(self, buf, *args, **kwargs)

        # mutate Savuka instance
        self.data[buffer_index][axis_to_index(axis)] = new_data

    def axis_to_index(axis):
        # dependent on self.data implementation details

        # default behavior is to change y
        if axis == 'y' or axis is None:
            return 2
        elif axis == 'x':
            return 1
        elif axis == 'z':
            return 0

    return wrapper


class Savuka:

    def __len__(self):
        return len(self.data)

    def __repr__(self):
        # representation of the data. Called with built-in print function
        r = ""
        for i, buf in enumerate(self.data):
            # TODO, print the attributes as {0}
            r += "\nbuffer {0}: {1}".format(i, buf)
        return r

    def __init__(self):
        # a list of the dictionaries of Dimension objects and values specified
        # by the individual parsing functions in the parse_funcs module
        self.data = []

        # a dictionary of name value pairs for labelling buffers as
        # buffername, buffer_range
        self.attributes = {}

    def read(self, filepath, formstyle):
        """Parses the given file of the given format and adds its data to
        self.data while recording the metadata in self.attributes"""

        # parse the file according to the formstyle specified by the user
        data_dict = parse_funcs.parse(filepath, formstyle)

        # The hash value of the buffer must be unique, so this simple algorithm
        # ensures that no buffer in self will have hash collisions with others.
        data_dict['hash'] = len(self) + 1

        # add the parsed data to the list
        self.data.append(data_dict)

        # show the user the x and y values they parsed in
        print("\nSavuka read in the following data:\n" + str(data_dict))

    def num_buffers(self):
        return len(self)

    def set_name(self, buf, name):
        if isinstance(buf, int) and isinstance(name, str):
            self.attributes[name] = buf
        else:
            print("no names were changed for buffer {0} and name {1}"
                  "".format(buf, name))

    def set_names(self, buf_range, name):
        if isinstance(buf_range, tuple):
            # give all the buffers the same name. add 1 b/c semi-open interval
            for i in range(buf_range[0], buf_range[1] + 1):
                self.set_name(i, name)

    def get_buffer_by_name(self, name):
        try:
            return self.attributes[name]
        except KeyError:
            print("no buffer(s) named {0}".format(name))

    def get_buffer(self, idx):
        """returns the array of x, y, and the z value of the buffer. Each
        buffer has the form [[z],[x],[y]]"""

        try:
            return self.data[idx]
        except IndexError:
            print("buffer {0} not accessible"
                  " with data length {1}".format(idx, len(self)))

    def get_buffers(self, buf_range):
        if isinstance(buf_range, range):
            # return a generator which yields the buffers. Usable as *bufs
            b = (self.get_buffer(x) for x in buf_range)
            return b
        elif isinstance(buf_range, tuple):
            bufs = (self.get_buffer(x) for x in range(buf_range[0],
                                                      buf_range[1] + 1))
            return bufs
        elif isinstance(buf_range, int):
            # we must be guaranteed to return a tuple so we can use * unpacking
            b = (self.get_buffer(buf_range),)
            return b

    def get_xs(self, idx, start=0, end=0):
        """returns the x values within the range of the given buffer."""

        buffer = self.data[idx]
        return buffer.get_xs(start, end)
    ''' allxs = buffer.get('dim1').data
    if end == 0:
        return allxs
    else:
        return allxs[start:end]'''

    def get_ys(self, idx, start=0, end=0):
        """returns the y values within the range of the given buffer. Each
        buffer has the form [[z],[x],[y]]"""
        buffer = self.data[idx]
        allys = buffer.get('dim2').data
        if end == 0:
            return allys
        else:
            return allys[start:end]

    def get_z(self, idx):
        # TODO what about 4+ dimension data?
        """return the zingle z value for the buffer."""
        buffer = self.data[idx]
        return buffer.get('dim3')

    def update_buffers(self, buffer_index, new_data, dim='dim2'):
        self.data[buffer_index][dim] = new_data

    def add_buffers(self, buffer_index1, buffer_index2, axis='y'):
        b1 = self.get_buffer(buffer_index1)
        b2 = self.get_buffer(buffer_index2)

        # interpolates the values of b2 based on the y vals of b1.
        # Todo cubic spline interpolation. Include flag for doing interpolation
        add_to_b2 = np.interp(self.get_xs(b1), self.get_xs(b2), self.get_ys(b2))

        new_y = b2[2] + add_to_b2

        self.update_buffers(buffer_index2, new_y)

    def multiply_buffers(self, buffer_index1, buffer_index2, axis='y'):

        b1 = self.get_buffer(buffer_index1)
        b2 = self.get_buffer(buffer_index2)

        # interpolates the values of b2 based on the y vals of b1.
        print("interpolating ... ")
        add_to_b2 = np.interp(self.get_xs(b1), self.get_xs(b2), self.get_ys(b2))

        new_y = b2[2] * add_to_b2

        self.update_buffers(buffer_index2, new_y)

    def shift_buffer(self, buffer_index, delta, dim='dim2'):
        buf = self.get_buffer(buffer_index).get_ys()

        # numpy adds delta to each elt in an array by default.
        new_buf = buf + delta

        self.update_buffers(buffer_index, new_buf, dim=dim)

    def scale_buffer(self, buffer_index, sigma, dim='dim2'):
        buf = self.get_buffer(buffer_index).get_ys()
        new_buf = buf * sigma

        self.update_buffers(buffer_index, new_buf, dim=dim)

    def pow_buffer(self, buffer_index, exp, dim='dim2'):
        buf = self.get_buffer(buffer_index).get_ys()
        new_buf = buf ** exp

        self.update_buffers(buffer_index, new_buf, dim=dim)

    @plot_funcs.show_after_completion
    def plot_buffers(self, buf_range):
        print(self.get_buffers(buf_range))
        return plot_funcs.plot_buffers(*self.get_buffers(buf_range))

    @plot_funcs.show_after_completion
    def plot_superimposed(self, buf_range):
        return plot_funcs.plot_superimposed(*self.get_buffers(buf_range))

