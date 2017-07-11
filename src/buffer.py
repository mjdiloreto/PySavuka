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
        s = ""

        for key, value in self.items():
            if isinstance(value, Dimension):
                # x and y should be arrays
                if isinstance(value.data, np.ndarray):
                    try:
                        s += "{0}: [{1}, {2}, . . . , {3}, {4}],\n"\
                             "".format(value.name, value.data[0], value.data[1],
                                       value.data[-2], value.data[-1])
                    except IndexError:
                        s += "{0}: {1},\n".format(value.name, value.data)
                # z1, z2, zn should be single values, if present.
                else:
                    s += "{0}: {1},\n".format(value.name, value.data)
            else:
                s += "{0}: {1}, ".format(key, value)

        # strip the final space and comma. Aesthetics only.
        return "{" + s[:-2] + "}"

    def __init__(self, *args, **kwargs):
        super(Buffer)

        # pass other dimensions as arguments to copy them
        for arg in args:
            self.update(arg)

            # add new keys by passing them as kwargs.
        for k, v in kwargs.items():
            self[k] = v

        # minimum requirement is that there are x and y values
        if 'dim1' not in self:
            self['dim1'] = Dimension(np.asarray([]), 'default')
        if 'dim2' not in self:
            self['dim2'] = Dimension(np.asarray([]), 'default')

        # many calculations assume data are numpy arrays
        assert isinstance(self['dim1'].data, np.ndarray) \
            and isinstance(self['dim2'].data, np.ndarray), \
            "first two dimensions in a Buffer must be numpy arrays."

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

    def add_to_x(self, data, interpolate=False):
        current_x = self['dim1'].data
        if isinstance(data, np.ndarray):
            if current_x.shape == data.shape:
                self['dim1'].data += data
            elif interpolate:
                print("using cubic spline interpolation on data")
                # TODO cubic spline interpolation
        elif isinstance(data, int):
            self['dim1'].data += data

    def add_to_y(self, data, interpolate=False):
        current_y = self['dim2'].data
        if isinstance(data, np.ndarray):
            if current_y.shape == data.shape:
                self['dim2'].data += data
            elif interpolate:
                print("using cubic spline interpolation on data")
                # TODO cubic spline interpolation
        elif isinstance(data, int):
            self['dim2'].data += data


if __name__ == '__main__':
    b = Buffer()
    print(b.__repr__())
    b['a'] = 'b'
    b1 = Buffer(b)
    print(b1.__repr__())