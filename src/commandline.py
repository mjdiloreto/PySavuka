"""This module contains the main program loop and all code for commands passed
to the program."""

from src import savuka
from src import plot_funcs
from src import utils
from src import models
from src import svd
from src import params
from src import fit

import cmd
import re
import os
import sys
from sys import stderr, stdout
from time import sleep

# TODO organize methods alphabetically
# don't change the location of any files in this package.
library_root = os.path.abspath(os.path.join(__file__, "../.."))

formats_path = os.path.join(library_root, r'docs/supported_formats.txt')

json_path = os.path.join(library_root, r'docs\formats.json')

FORMATS = open(formats_path).read()


class CommandLine(cmd.Cmd):
    intro = """
    
    Welcome to PySavuka 
    
    type 'help' for help
    
    """

    def __init__(self):
        super(CommandLine, self).__init__()
        self.savuka = savuka.Savuka()
        self.prompt = '(pysavuka)'
        self.params = None

    def postcmd(self, stop, line):
        # wait 1/10 second after each command. This fixes some weird
        # printing bugs when color is involved.
        sleep(0.1)

    def do_quit(self, line):  # TODO add save feature.
        """Exit savuka:
        Usage:
            quit
        """
        sys.exit()

    @utils.except_all
    def onecmd(self, line):
        return cmd.Cmd.onecmd(self, line)

    def do_help(self, arg):
        """Print help text in red. Kind of a hack since stderr is always red."""
        self.stdout = stderr
        cmd.Cmd.do_help(self, arg)
        self.stdout = stdout

    def default(self, line):
        print("This command is unsupported: {0}".format(line))

    def do_read(self, line):
        """user will be prompted to select file(s) and asked about the
           format of those files, as specified by supported_formats.txt
           in the docs folder of this project.

        Usage: read
            Options:
                None
           """

        def read_help(filepaths, formstyle):
            for x in filepaths:
                try:
                    # store the file's information in the savuka object.
                    self.savuka.read(x, formstyle)
                except NameError:
                    newformstyle = input(
                        "\nThe specified format [{0}] is unsupported,"
                        " enter a new one: ".format(formstyle))
                    return read_help(filepaths, newformstyle)

        filepaths = utils.ask_for_files()
        if filepaths is not "":
            formstyle = input("\nFormat of the file(s): ")
            return read_help(filepaths, formstyle)

    def do_plot(self, line):
        """usage: plot |
            plot <python style list with no spaces, eg [1,2,3]>

            OPTIONS:
            -s      superimpose the plots

            plots the buffers specified by the given ranges (either integers
            or python tuples)."""
        args, kwargs = utils.parse_options(line)
        if line is '':
            # default behavior is to plot everything in separate windows.
            self.savuka.plot_buffers(range(len(self.savuka)))
        elif '-s' in args:
            self.savuka.plot_superimposed(utils.string_to_index_list(args[0]))
        else:
            self.savuka.plot_buffers(args[0])

        plot_funcs.show()

    def do_svd(self, line):
        """usage: svd [file path] [# of spectra]
        Singular value decomposition."""

        return svd.svd()

    def do_formats(self, line):
        """List all currently defined formats for files."""
        # get the dictionary of formats from formats.json
        defined_formats = utils.load_formats_from_json(json_path)

        formats = []

        # iterate through the format names
        for formstyle in defined_formats.keys():
            name = "\n{0}:\n".format(formstyle)
            # things like 'data_start, extra_dimensions, etc.)
            desc = ["\t{0}\t{1}\n".format(k, v) for k, v
                    in defined_formats[formstyle].items()]
            desc = "".join(desc)  # make them all one string

            formats.append(name + desc)

        print("".join(formats))

    def do_load(self, line):
        """Load the file of the given format into the program.

        Usage:
            load [file path] [format type]

        Options:
            file path:
                The exact path of the file to be read in.
            format type:
                The format of the file. Specified in formats.json
                or by using the formats command."""

        def load_help(filepath, formstyle):
            self.savuka.read(filepath, formstyle)

        if line is "":
            filepath = input("\nFile path to be read: ")
            formstyle = input("\nWhat is the format of the file?: ")
            return load_help(filepath, formstyle)
        else:
            parsed = cmd.Cmd.parseline(self, line)
            return load_help(parsed[0], parsed[1])

    def do_print(self, line):
        """Display the data contents of the files read into the program.
        Usage:
            print

        Options:
            None"""
        if line is "":
            print(self.savuka)
            # Todo make line params specify buffer indices and names to print

    def do_shift(self, line):
        """Add the given amount to all y values of the given buffer.

        Usage:
            pow <buffer number> <amount>

        Options:
            buffer number: int
                Which buffer should be raised to the exponent?
            amount: int or float
                Add this amount to all y values.
        """
        args = utils.parseline(line)
        self.savuka.shift_buffer(utils.intify(args[0]), utils.floatify(args[1]))

    def do_scale(self, line):
        # TODO add option to scale fit by typing fit after command
        """Multiply all y values in a buffer by the given scalar.

        Usage:
            pow <buffer number> <scalar>

        Options:
            buffer number: int
                Which buffer should be raised to the exponent?
            scalar: int or float or in the form a/b
                Scale all y values by this amount."""
        args = utils.parseline(line)
        self.savuka.scale_buffer(utils.intify(args[0]), utils.floatify(args[1]))

    def do_pow(self, line):
        """Raise all y values in a buffer to the given power.

        Usage:
            pow <buffer number> <exponent>

        Options:
            buffer number: int
                Which buffer should be raised to the exponent?
            exponent: int or float
                exponent to raise all y values to.
        """

        args = utils.parseline(line)
        self.savuka.pow_buffer(utils.intify(args[0]), utils.floatify(args[1]))

    def do_formatload(self, line):
        """Specify a file format and load in file(s) accordingly. Provides the
        ability to save the format for future use using the read or load commands.

        Usage:
            formatload

        Options:
            None
        """
        files = utils.ask_for_files()
        cols = utils.intify(input("How many columns total?: "))
        data_start = utils.intify(input("What line does data "
                            "start on (starting from 0)?: "))
        data_names = []
        for x in range(cols):
            data_names.append(input("What is the name of column "
                                    "{0}?: ".format(x)))

        num_extra_dimensions = utils.intify(input("How many other dimensions "
                                              "are there?: "))
        extra_dimensions = {}
        for x in range(num_extra_dimensions):
            v = utils.intify(input("What line contains the data from extra "
                    "dimension {0}? (starting from 0): ".format(x)))
            k = input("What is the name of that dimension?: ")
            extra_dimensions[k] = v

        delimiter = input("What does the file use to separate values? "
                          "[t for tab, s for space, or , for comma]: ")
        # convert the answer into an escaped character
        if delimiter == 't':
            delimiter = '\t'
        elif delimiter == 's':
            delimiter = '\s'
        # comma can stay the same

        save_state = input("Would you like to save this as a permanent file"
                           "format? [y/n]: ")

        confirmations = {"y", "Y", "yes", "Yes", "YES"}
        if save_state in confirmations:  # Save the data in formats.json
            name = input("What would you like to name the format?: ")
            utils.save_formats_to_json(json_path, name,
                {
                    "data_start": data_start,
                    "data_names": data_names,  # reveals number of columns
                    "extra_dimensions": extra_dimensions,
                    "delimiter": delimiter
                })

        for file_ in files:
            self.savuka.format_load(file_, data_start, data_names,
                                   extra_dimensions, delimiter)

    def do_models(self, line):
        """list all the descriptions of all available models for fitting.
        Usage:
            models

        Options:
            None
        """
        print("".join(models.get_helps(line)))

    def do_fit(self, line):
        """Fit the data from the given buffer index to the given model.
        Usage:
            fit <buffer index> <model name> -keyword <keyword value>...

        Arguments:
            buffer index: int OR tuple(no spaces, e.g. (0,1,2))
                What buffers should be fit to the model
            model name: string
                The name of the model as specified in models.py

        Keyword arguments:
            method: str, optional
                Name of the fitting method to use. Valid values are:
                - `'leastsq'`: Levenberg-Marquardt (default)
                - `'least_squares'`: Least-Squares minimization, using Trust Region Reflective method by default
                - `'differential_evolution'`: differential evolution
                - `'brute'`: brute force method
                - '`nelder`': Nelder-Mead
                - `'lbfgsb'`: L-BFGS-B
                - `'powell'`: Powell
                - `'cg'`: Conjugate-Gradient
                - `'newton'`: Newton-CG
                - `'cobyla'`: Cobyla
                - `'tnc'`: Truncate Newton
                - `'trust-ncg'`: Trust Newton-CGn
                - `'dogleg'`: Dogleg
                - `'slsqp'`: Sequential Linear Squares Programming
            debug: bool, optional
                When set to True, will output parameter values at each iteration
                   of the fitting routine. Default is False.
            scale_covar : bool, optional
                Whether to automatically scale the covariance matrix (`leastsq` only).
            nan_policy : str, optional
                Specifies action if `userfcn` (or a Jacobian) returns NaN
                values. One of:
                    - 'raise' : a `ValueError` is raised
                    - 'propagate' : the values returned from `userfcn` are un-altered
                    - 'omit' : non-finite values are filtered
            full_output : bool, optional
                non-zero to return all optional outputs.
            col_deriv : bool, optional
                non-zero to specify that the Jacobian function computes derivatives
                down the columns (faster, because there is no transpose operation).
            ftol : float, optional
                Relative error desired in the sum of squares.
            xtol : float, optional
                Relative error desired in the approximate solution.
            gtol : float, optional
                Orthogonality desired between the function vector and the columns of
                the Jacobian.
            maxfev : int, optional
                The maximum number of calls to the function. If `Dfun` is provided
                then the default `maxfev` is 100*(N+1) where N is the number of elements
                in x0, otherwise the default `maxfev` is 200*(N+1).
            epsfcn : float, optional
                A variable used in determining a suitable step length for the forward-
                difference approximation of the Jacobian.
                Normally the actual step length will be sqrt(epsfcn)*x
                If epsfcn is less than the machine precision, it is assumed that the
                relative errors are of the order of the machine precision.
            factor : float, optional
                A parameter determining the initial step bound
                (``factor * || diag * x||``). Should be in interval ``(0.1, 100)``.
            diag : sequence, optional
                N positive entries that serve as a scale factors for the variables.
                """
        args, kwargs = utils.parse_options(line)
        print(args)
        if len(args) != 2:
            print(self.do_help("fit"))

        # make parameters for a single buffer
        if isinstance(args[0], int):
            num_bufs = 1
        # make parameters for multiple buffers.
        elif isinstance(args[0], tuple):
            num_bufs = len(args[0])

        self.do_parameters("{0} {1}".format(num_bufs, args[1]))
        kwargs['parameters'] = self.params
        self.savuka.fit(*args, **kwargs)

    def do_clear(self, line):
        """Clear the screen. Equivalent to cls on Windows and clear on Unix."""
        os.system('cls' if os.name == 'nt' else 'clear')

    def do_parameters(self, line):
        """Set the parameters for fitting.
        Usage:
            pd <number of buffers> <model>

        Arguments:
            number of buffers:
                How many buffers should have parameters specified for the fit?
            model:
                name of the model function that will be fit, as specified by the
                models command
                """
        args, kwargs = utils.parse_options(line)
        if len(args) != 2:  # user didn't provide necessary options
            print(self.do_help("parameters"))

        num_bufs = args[0]
        model = args[1]
        model = models.get_models(model)  # convert string to function
        self.params = params.main(num_bufs, model)

    def do_fit_result(self, line):
        """If we have run a fit, print its results"""
        self.savuka.report_result()

    def do_fit_plot(self, line):
        """If we have run a fit, plot it"""
        # TODO hook up with better plotting options from self.do_plot
        self.savuka.plot_result()

    def do_chi_error(self, line):
        """Generate a plot of chi-quare for fits perturbing the value of
        parameter and not allowing it to vary during fitting. A curve of
        chi-square should be produced, with the true best-fit value of param
        as the minimum.
        Usage:
            chi_error <param name> -keyword <keyword value>...

        Arguments:
            param name: str
                Name of the parameter to be varied, according to the model
                as defined by the models command. The only variable in the
                models that cannot be used is x.

        Keyword arguments:
            nsamples: int
                how many values of param to take X^2 at. Odd number will
                include true param value
            plus_minus: float
                percentage value representing how far from the true value of
                param the value should vary in the X^2 analysis.
            debug: bool
                Whether each fit should print its results. Default False.

            """
        args, kwargs = utils.parse_options(line)
        if len(args) != 1:
            print(self.do_help("chi_error"))

        self.savuka.plot_x2(args[0], **kwargs)


def main():
    CommandLine().cmdloop()


if __name__ == '__main__':
    main()
