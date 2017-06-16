"""This file contains the functions used to parse data into python lists.
Each lab instrument used with the software should have its own associated
parsing funtion."""


def parse(filepath, formstyle):
    """Dispatches parsing responsibility to the function associated with the
    formstyle specified. Ideally styles and functions should be named after
    the lab instrument that produce them."""

    # evaluate the function of the associated formating style.
    # this can raise a NameError if the formstyle is undefined.
    return eval("parse_" + formstyle + "(filepath)")


def parse_example(files):
    """works for all files composed of lines matching the form:
     .0000000E+00 ,  .0000000E+00
     where the first expression represents the x value, and the second
     the y value.

     assumes the format will be EXACTLY the same each time."""

    # TODO make this faster.
    with open(files) as f:
        read = [line for line in f]
        xs = [float(line[3:11]) * (10 ** int(line[14:15]))
              for line in read[3:]]
        ys = [float(line[19:27]) * (10 ** int(line[30:31]))
              for line in read[3:]]

    return xs, ys



