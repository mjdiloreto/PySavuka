"""Each of the functions in this module takes, as an argument, at least
one instance of a Buffer as defined in the module buffer."""

from src import utils

import matplotlib.pyplot as plt


def show_after_completion(f):
    """Decorator for functions/Savuka methods which should display plots
    once they have been staged. None of the functions in this module
    (plot_funcs.py) should call 'plt.show()'

    Do not try to concurrently plot data and continue execution of program.
    Because matplotlib is not threadsafe, there will be a huge workaround
    involving the multiprocessing module. This means you must close all plots
    before doing anything with the Savuka program."""

    def wrapper(self, *args, **kwargs):

        f(self, *args, **kwargs)
        plt.show()

    return wrapper


def plot_xy(*args, **kwargs):

    new_args = (eval(arg) for arg in args)
    new_kwargs = {k: eval(v) for k, v in kwargs.items()}

    _plot_xy(*new_args, **new_kwargs)


def _plot_xy(xdata, ydata, **kwargs):
    if kwargs:
        plt.plot(xdata, kwargs['y'])
    else:
        plt.plot(xdata, ydata)
    plt.show()


def plot_buffer(buf):
    """Plots the x and y data of the buffer in the subplot of given idx.
    Subplots should be unique to each buffer being plotted. Collisions in
    idx will result in overwriting of previously queued data."""
    try:
        print("\nplotting buffer(s): {0}".format(buf))
        plt.figure(buf['hash'])
        plt.plot(buf.get_xs(), buf.get_ys())
    except IndexError:
        print("There is no buffer at"
              " the given index: {0}".format(buf))


def plot_buffers(*args):
    # plot all the Buffer objects
    for arg in args:
        plot_buffer(arg)


def plot_superimposed(sav, buf_list):
    # Figure number unique to this function. Only one superimposed plot at once.
    plt.figure(999)

    # add the buffers associated with the arguments to the list.
    bufs = []
    for x in utils.eval_string_list(buf_list):
        if isinstance(x, tuple):
            print("\nplotting buffers in range: "
                  "({0}, {1})".format(x[0], x[1] + 1))
            for y in range(x[0], x[1]+1):
                try:
                    bufs.append(sav.get_buffers(y))
                except IndexError:
                    print("There is no buffer at"
                          " the given index: {0}".format(y))
        elif isinstance(x, int):
            print("\nplotting buffer: {0}".format(x))
            try:
                bufs.append(sav.get_buffers(x))
            except IndexError:
                print("There is no buffer at"
                      " the given index: {0}".format(x))

    xs = [sav.get_xs(x) for x in bufs]
    ys = [sav.get_ys(x) for x in bufs]
    vals = [val for x in zip(xs, ys) for val in x]
    plt.plot(*vals)



