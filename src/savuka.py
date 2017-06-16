"""This file contains the Savuka class, which is used in the cli.py module
as the context object for the program. It contains all data parsed by the
user, and methods to analyze that data."""

import parse_funcs
import plot_funcs

import numpy as np


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
        return self.data.shape == (0,)

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

    def dimensionality(self):
        return self.data.shape

    def num_buffers(self):
        return self.dimensionality()[0]

    def get_buffers(self, idx):
        """returns the array of x, y, and the z value of the buffer. Each
        buffer has the form [[z],[x],[y]]"""

        # -2 index of data size should always correspond to x dimension
        current_x = self.data.shape[-2]
        if isinstance(idx, int):
            #TODO change assertions to try: except.
            assert 0 <= idx <= current_x, "buffer {0} not accessible" \
                    " with data shape {1}".format(idx, self.data.shape)
            return self.data[idx]
        elif isinstance(idx, tuple):
            assert 0 <= idx[0] <= current_x and 0 <= idx[1] <= current_x, "" \
            "buffer {0} not accessible " \
            "with data shape {1}".format(idx, self.data.shape)
            bufs = [self.data[x] for x in range(idx[0], idx[1] + 1)]
            return bufs

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

    def plot_all_buffers(self):
        return plot_funcs.plot_all(self)

    def plot_buffers(self, buf_range):
        return plot_funcs.plot_buffers(self, buf_range)

    def plot_superimposed(self, buf_list):
        return plot_funcs.plot_superimposed(self, buf_list)

