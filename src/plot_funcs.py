"""Each of the functions in this module takes, as an argument, at least
one instance of a Buffer as defined in the module buffer."""

from src import utils

import matplotlib.pyplot as plt

# GLOBALS
#########

# Pyplot uses numbers for the figures. It is recommended to use 3-digit figure
# numbers, and many people start with 121, for some reason.
FIG_NUMBER = 121

def get_fig_number():
    """Return the current value of FIG_NUMBER and increment it by one,
    to guarantee unique plots."""
    global FIG_NUMBER

    num = FIG_NUMBER
    FIG_NUMBER += 1

    return num


def show():
    """Wrap matplotlib. Useful for more advanced plotting which
    hasn't been implemented"""
    plt.show()


def plot_xy(x, y, x_label='x', y_label='y'):
    """Plot x values against y values, whatever they may be.
    Parameters
    ----------
        x: np.ndarray
            x values to be plot
        y: np.ndarray
            y values to be plot
        x_label: string
            label for x axis
        y_label: string
            label for y axis
            """
    fig = plt.figure(get_fig_number())
    plt.plot(x, y)

    return fig



def plot_buffer(buf):
    """Plots the x and y data of the buffer in the subplot of given idx.
    Subplots should be unique to each buffer being plotted. Collisions in
    idx will result in overwriting of previously queued data."""
    try:
        print("\nplotting buffer(s): {0}".format(buf))
        plt.figure(get_fig_number())
        plt.plot(buf.get_xs(), buf.get_ys(), 'o')
    except IndexError:
        print("There is no buffer at"
              " the given index: {0}".format(buf))


def plot_buffers(*args):
    # plot all the Buffer objects
    for arg in args:
        plot_buffer(arg)


def plot_superimposed(*args):
    """plots any number of Buffer objects on the same graph."""
    xs = [buf.get_xs() for buf in args]
    ys = [buf.get_ys() for buf in args]
    vals = [val for x in zip(xs, ys) for val in x]
    plt.plot(*vals)


def plot_superimposed1(sav, buf_list):
    # Figure number unique to this function. Only one superimposed plot at once.
    plt.figure(get_fig_number())

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


def plot_with_residuals(x, y, fitted_y, resids):
    """Plot the original y values, the y values of the model given fit
    parameters, and the residuals against x."""
    fig = plt.figure(get_fig_number())
    frame1 = fig.add_axes((.1,.3,.8,.6))
    plt.plot(x, y, 'o', x, fitted_y, '-')

    frame2 = fig.add_axes((.1, .1, .8, .2))

    plt.plot(x, resids, '-')
    frame2.set_ylabel('$Residual$', fontsize=14)

    # This is for any sort of plot manipulation after it is made. Future
    return fig




