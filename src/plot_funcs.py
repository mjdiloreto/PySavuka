from . import utils
import matplotlib.pyplot as plt


def show_after_completion(f):
    """Decorator for functions/Savuka methods which should display plots
    once they have been staged. None of the functions in this module
    (plot_funcs.py) should call 'plt.show()'"""

    def wrapper(self, *args, **kwargs):
        f(self, *args, **kwargs)
        plt.show()

    return wrapper


def plot_all(sav):
    for x in range(sav.num_buffers()):
        plot_single_buffer(sav, x)


def plot_buffers(sav, buf_range, *args):
    b = utils.eval_string(buf_range)
    try:
        if isinstance(b, int):
            plot_single_buffer(sav, b)
        elif isinstance(b, tuple) and len(b) == 2:
            for x in range(b[0], b[0] + len(b)):
                plot_single_buffer(sav, x)
        else:
            print("You must enter either an integer or length 2 tuple as "
                  "an argument to plot. You entered: {0}".format(buf_range))

        # supports variable arity (variable arguments) kind of hackish.
        for arg in args:
            plot_buffers(sav, arg)
    except Exception as e:
        print("You may only specify an integer or tuple for the buffer."
              " You entered: {0} \n{1}".format(buf_range, e.__class__.__name__))


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


def plot_single_buffer(sav, buffer):
    try:
        print("\nplotting buffer(s): {0}".format(buffer))
        buf = sav.get_buffers(buffer)
        plt.figure(buffer)
        plt.plot(sav.get_xs(buf), sav.get_ys(buf))
    except IndexError:
        print("There is no buffer at"
              " the given index: {0}".format(buffer))
