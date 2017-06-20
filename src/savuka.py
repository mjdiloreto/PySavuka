"""This file contains the Savuka class, which is used in the cli.py module
as the context object for the program. It contains all data parsed by the
user, and methods to analyze that data."""

import parse_funcs
import plot_funcs

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

    def __init__(self):
        # a dict of parameters associated with the data, used for analysis:
        # e.g. model, paths of data files, etc.
        self.data = np.array([])

        # a dictionary of name value pairs for labelling buffers as
        # buffername, buffer_range
        self.attributes = {}

    def read(self, filepath, formstyle):
        """Parses the given file of the given format and adds its data to
        self.data while recording the metadata in self.attributes"""

        # TODO record metadata in self.attributes
        x, y = parse_funcs.parse(filepath, formstyle)

        # make z the same dimensionality as x and y
        # TODO actually record the z value, depending on formstyle.
        # Have [x,y,z] returned by parsefuncs
        z = np.zeros(np.asarray(x).shape)

        dataset = np.asarray([z, x, y])

        if self.is_empty():
            self.data = np.asarray([dataset])

        else:
            # dataset is contained in another list so that its dimensions match
            # self.data.
            self.data = np.concatenate((self.data, np.asarray([dataset])),
                                       axis=0)

        print("\nparsed x values for z={4} ===> [{0}, {1}, ..., {2}, {3}]".format(
            self.data[-1, -2, 0],
            self.data[-1, -2, 1],
            self.data[-1, -2, -2],
            self.data[-1, -2, -1],
            self.data[-1, -3, 0]))
        print("parsed y values for z={4} ===> [{0}, {1}, ..., {2}, {3}]".format(
            self.data[-1, -1, 0],
            self.data[-1, -1, 1],
            self.data[-1, -1, -2],
            self.data[-1, -1, -1],
            self.data[-1, -3, 0]))

    def is_empty(self):
        return self.dimensionality() == (0,)

    def dimensionality(self):
        return self.data.shape

    def num_buffers(self):
        return self.dimensionality()[0]

    def set_name(self, buf_range, name):
        assert isinstance(buf_range, tuple) or isinstance(buf_range, int), "" \
            "Name can only be assigned to " \
            "valid buffer range: {0}".format(buf_range)
        assert isinstance(name, str), "Name must be a string: {0}".format(name)
        self.attributes[name] = buf_range

    def get_buffer_by_name(self, name):
        try:
            return self.attributes[name]
        except KeyError:
            print("no buffer(s) named {0}".format(name))

    def get_buffers(self, idx):
        """returns the array of x, y, and the z value of the buffer. Each
        buffer has the form [[z],[x],[y]]"""

        if isinstance(idx, int):
            try:
                return self.data[idx]
            except IndexError:
                print("buffer {0} not accessible"
                      " with data shape {1}".format(idx, self.data.shape))
        elif isinstance(idx, tuple):
            try:
                bufs = [self.data[x] for x in range(idx[0], idx[1] + 1)]
                return bufs
            except IndexError:
                print("buffer {0} not accessible"
                      " with data shape {1}".format(idx, self.data.shape))

    def get_xs(self, buffer, start=0, end=0):
        # TODO add dimension checks
        """returns the x values within the range of the given buffer. Each
        buffer has the form [[z],[x],[y]]"""
        allxs = buffer[1]
        if end == 0:
            return allxs
        else:
            return allxs[start:end]

    def get_ys(self, buffer, start=0, end=0):
        """returns the y values within the range of the given buffer. Each
        buffer has the form [[z],[x],[y]]"""
        allys = buffer[2]
        if end == 0:
            return allys
        else:
            return allys[start:end]

    def get_z(self, buffer):
        """return the zingle z value for the buffer."""
        return buffer[0, 0]

    def update_buffers(self, buffer_index, new_buffer, axis='y'):

        def axis_to_index(axis):
            # dependent on self.data implementation details

            # default behavior is to change y
            if axis == 'y' or axis is None:
                return 2
            elif axis == 'x':
                return 1
            elif axis == 'z':
                return 0

        self.data[buffer_index][axis_to_index(axis)] = new_buffer

    def add_buffers(self, buffer_index1, buffer_index2, axis='y'):

        b1 = self.get_buffers(buffer_index1)
        b2 = self.get_buffers(buffer_index2)

        # interpolates the values of b2 based on the y vals of b1.
        add_to_b2 = np.interp(self.get_xs(b1), self.get_xs(b2), self.get_ys(b2))

        new_y = b2[2] + add_to_b2

        self.update_buffers(buffer_index2, new_y)

    def multiply_buffers(self, buffer_index1, buffer_index2, axis='y'):

        b1 = self.get_buffers(buffer_index1)
        b2 = self.get_buffers(buffer_index2)

        # interpolates the values of b2 based on the y vals of b1.
        add_to_b2 = np.interp(self.get_xs(b1), self.get_xs(b2), self.get_ys(b2))

        new_y = b2[2] * add_to_b2

        self.update_buffers(buffer_index2, new_y)

    def shift_buffer(self, buffer_index, delta, axis='y'):
        buf = self.get_ys(self.get_buffers(buffer_index))

        # numpy adds delta to each elt in an array by default.
        new_buf = buf + delta

        self.update_buffers(buffer_index, new_buf, 'y')

    def scale_buffer(self, buffer_index, sigma, axis='y'):
        buf = self.get_ys(self.get_buffers(buffer_index))
        new_buf = buf * sigma

        self.update_buffers(buffer_index, new_buf, 'y')

    def pow_buffer(self, buffer_index, exp, axis='y'):
        buf = self.get_ys(self.get_buffers(buffer_index))
        new_buf = buf ** exp

        self.update_buffers(buffer_index, new_buf, 'y')

    def plot_all_buffers(self):
        return plot_funcs.plot_all(self)

    def plot_buffers(self, buf_range):
        return plot_funcs.plot_buffers(self, buf_range)

    def plot_superimposed(self, buf_list):
        return plot_funcs.plot_superimposed(self, buf_list)

