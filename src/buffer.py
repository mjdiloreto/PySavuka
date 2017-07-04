from collections import namedtuple

dim = namedtuple('dim', ['data', 'name'])


class Buffer(dict):

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
            self['dim1'] = dim([], 'default')
            self['dim2'] = dim([], 'default')

    def get_xs(self):
        return self['dim1'].data

    def get_x_name(self):
        return self['dim1'].name

    def get_ys(self):
        return self['dim2'].data

    def get_y_name(self):
        return self['dim2'].name
