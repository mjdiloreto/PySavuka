from collections import namedtuple
import numpy as np

# Define a new type of data, which is a container called 'Dimension'
# That will be used to store all parsed data and the name of that data.
# For example, if measuring light intensity over time, the data would be parsed
# into 2 dimensions, one with the name 'intensity' and the y data from the
# experiment, and another called 'time' with the x data.

# This structure is used in each dictionary returned by these parse_funcs
# as the values to the keys named 'dim1','dim2',etc.
# new Dimension instances are made via: Dimension([...],'name')
Dimension = namedtuple('Dimension', ['data', 'name'])


class Buffer(dict):

    def __str__(self):
        """String representation of Buffer. Show first two and last two
        values of each dataset, or, if not a dataset, show the key, value
        pairs as in a regular dictionary."""
        s = "{"

        for key, value in self.items():
            if isinstance(value, Dimension):
                if isinstance(value.data, np.ndarray):
                    s += "{0}: [{1}, {2}, . . . , {3}, {4}],\n"\
                         "".format(value.name, value.data[0], value.data[1],
                                   value.data[-2], value.data[-1])
                else:
                    s += "{0}: {1},\n".format(value.name, value.data)
            else:
                s += "{0}: {1}, ".format(key, value)

        # strip the final space and comma. Aesthetics only.
        return s[:-2] + "}"

    def __init__(self, *args, **kwargs):
        super(Buffer)

        # pass other dimensions as arguments to copy them
        for arg in args:
            self.update(arg)

            # add new keys by passing them as kwargs.
        for k, v in kwargs.items():
            self[k] = v

        # minimum requirement is that there are x and y values
        if not 'dim1' and 'dim2' in self:
            self['dim1'] = Dimension([], 'default')
            self['dim2'] = Dimension([], 'default')

    def get_xs(self, start=0, end=0):
        """returns the x values within the range of the given buffer."""
        allxs = self['dim1'].data
        if start == 0 and end == 0:
            return allxs
        else:
            assert start > end, "Tried to slice buffer from " \
                                "{0} to {1}".format(start, end)
            return allxs[start:end]

    def get_x_name(self):
        """returns the user associated name for the x dimension of their
        data. This is defined in the parse_funcs function that creates
        the Buffer object."""
        return self['dim1'].name

    def get_ys(self, start=0, end=0):
        allys = self['dim2'].data
        if start == 0 and end == 0:
            return allys
        else:
            assert start > end, "Tried to slice buffer from " \
                                "{0} to {1}".format(start, end)
            return allys[start:end]

    def get_y_name(self):
        return self['dim2'].name
