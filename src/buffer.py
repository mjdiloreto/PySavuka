from collections import namedtuple
import numpy as np

# Define a new type of data, which is a container called 'Dimension'
# That will be used to store all parsed data and the name of that data.
# For example, if measuring light intensity over time, the data would be parsed
# into 2 dimensions, one with the name 'intensity' and the y data from the
# experiment, and another called 'time' with the x data.

# This structure is used in each dictionary returned by these parse_funcs
# as the values to the keys named 'dim0','dim1',etc.
# new Dimension instances are made via: Dimension([...],'name')
# Dimension = namedtuple('Dimension', ['data', 'name'])


class Dimension(object):
    def __repr__(self):
        return "(" + self.name + ", " + str(self.data) + ")\n"

    def __init__(self, data=None, name=None):
        self.data = data if data is not None else np.asarray([])
        self.name = name if name is not None else ''

    def set_data(self, new_data):
        self.data = np.asarray(new_data)

    def set_name(self, new_name):
        self.name = str(new_name)

    def sample(self, start, stop, step):
        """sample data from start to stop by the step"""
        self.data = self.data[start:stop:step]

    def append(self, val):
        # TODO maybe have Dimension inherit from list and have an as_nparray method
        # val must be in list because that's how numpy appends.
        self.data = np.append(self.data, [val])


class Buffer(dict):

    def __str__(self):
        """String representation of Buffer. Show first two and last two
        values of each dataset, or, if not a dataset, show the key, value
        pairs as in a regular dictionary."""
        s = []

        for key, value in self.items():
            if isinstance(value, Dimension):
                # x and y should be arrays
                if isinstance(value.data, np.ndarray):
                    try:
                        s.append("{0}: [{1}, {2}, . . . , {3}, {4}],\n"
                                 "".format(value.name,
                                           value.data[0],
                                           value.data[1],
                                           value.data[-2],
                                           value.data[-1])
                                 )
                    except IndexError:
                        s.append("{0}: {1},\n".format(value.name, value.data))
                # z1, z2, zn should be single values, if present.
                else:
                    s.append("{0}: {1},\n".format(value.name, value.data))
            else:
                s.append("{0}: {1}, ".format(key, value))

        # make the list a string,
        # strip the final space and comma. Aesthetics only.
        string = "".join(s)[:-2]

        return "{" + string + "}"

    def __init__(self, *args, **kwargs):
        super(Buffer)

        # pass other dimensions as arguments to copy them
        for arg in args:
            self.update(arg)

            # add new keys by passing them as kwargs.
        for k, v in kwargs.items():
            self[k] = v

        # minimum requirement is that there are x and y values
        if 'dim0' not in self:
            self['dim0'] = Dimension(np.asarray([]), 'default')
        if 'dim1' not in self:
            self['dim1'] = Dimension(np.asarray([]), 'default')

        # calculations must assume data is in Dimension form.
        assert isinstance(self['dim0'], Dimension) \
            and isinstance(self['dim1'], Dimension), \
            "first two dimensions in a Buffer must be numpy arrays."

    def get_xs(self, start=0, end=0):
        """returns the x values within the range of the given buffer."""
        allxs = self['dim0'].data
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
        return self['dim0'].name

    def get_ys(self, start=0, end=0):
        allys = self['dim1'].data
        if start == 0 and end == 0:
            return allys
        else:
            assert start > end, "Tried to slice buffer from " \
                                "{0} to {1}".format(start, end)
            return allys[start:end]

    def get_y_name(self):
        return self['dim1'].name

    def add_to_x(self, data, interpolate=False):
        current_x = self['dim0'].data
        if isinstance(data, np.ndarray):
            if current_x.shape == data.shape:
                self['dim0'].data += data
            elif interpolate:
                print("using cubic spline interpolation on data")
                # TODO cubic spline interpolation
        elif isinstance(data, int):
            self['dim0'].data += data

    def add_to_y(self, data, interpolate=False):
        current_y = self['dim1'].data
        if isinstance(data, np.ndarray):
            if current_y.shape == data.shape:
                self['dim1'].data += data
            elif interpolate:
                print("using cubic spline interpolation on data")
                # TODO cubic spline interpolation
        elif isinstance(data, int):
            self['dim1'].data += data

    def update_y(self, new_data):
        self['dim1'].set_data(new_data)

    def update_x(self, new_data):
        self['dim0'].set_data(new_data)


if __name__ == '__main__':
    d = Dimension()
    print(d)
    d1 = Dimension(np.asarray([1,2,3]), 'doggy')
    print(d1)