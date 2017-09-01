"""This module contains the main program loop and all code for commands passed
to the program."""

from src import savuka
from src import plot_funcs
from src import utils
from src import models
from src import svd
from src import params
from src.parse_funcs import library_root, json_path
from src import fit

import cmd
import re
import os
import sys
from sys import stderr, stdout
from time import sleep
import matplotlib.pyplot as plt


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

    ####################
    # OVERRIDE METHODS #
    ####################

    def postcmd(self, stop, line):
        # wait 1/10 second after each command. This fixes some weird
        # printing bugs when color is involved.
        sleep(0.1)

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

    def do_quit(self, line):  # TODO add save feature.
        """Exit savuka:
        Usage:
            quit
        """
        sys.exit()

    ################
    # DATA PARSING #
    ################

    def do_read(self, line):
        """user will be prompted to select file(s) and asked about the
           format of those files, as specified by formats.json
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

    def do_add_format(self, line):
        """Specify a file format and load in file(s) accordingly. Provides the
        ability to save the format for future use using the read or load commands.

        Usage:
            add_format

        Parameters
        ----------
            None
        """
        messages = {"cols": "How many columns total?: ",
                    "data_start": "What line does data start on "
                                  "(starting from 0)?: ",
                    "column_name": "What is the name of column {0}?: ",
                    "n_extra": "How many other dimensions are there?: ",
                    "v": "What line contains the data from extra "
                         "dimension {0}? (starting from 0): "}
        cols = self.ensure_input_type(None, (int,), utils.intify,
                                      messages['cols'])

        data_start = self.ensure_input_type(None, (int,), utils.intify,
                                            messages['data_start'])

        data_names = []
        for x in range(cols):
            # Don't need to type-match strings
            column_name = self.ensure_input_type(None, (int,), utils.intify,
                                                 messages['column_name'].format(
                                                     x))

            data_names.append(column_name)

        n_extra = self.ensure_input_type(None, (int,), utils.intify,
                                         messages['n_extra'])

        extra_dimensions = {}
        for x in range(n_extra):
            v = self.ensure_input_type(None, (int,), utils.intify,
                                       messages['v'].format(x))
            k = input("What is the name of that dimension?: ")
            extra_dimensions[k] = v

        delimiter = input("What does the file use to separate values? "
                          "[t for tab, s for space, or , for comma]: ")
        # convert the answer into an escaped character
        if delimiter == 't':
            delimiter = '\t'
        elif delimiter == 's':
            delimiter = '\s'
        elif delimiter == ',':
            delimiter = ','
        # otherwise leave it unchanged. Delimiter can be anything.

        save_state = input("Would you like to save this as a permanent file"
                           "format? [y/n]: ")

        # Save the data in formats.json
        name = input("What would you like to name the format?: ")

        # Check the types of user input

        utils.save_formats_to_json(json_path, name,
                                   {
                                       "data_start": data_start,
                                       "data_names": data_names,
                                   # reveals number of columns
                                       "extra_dimensions": extra_dimensions,
                                       "delimiter": delimiter
                                   })

    def do_delete_format(self, line):
        """Delete the specified format from formats.json.
        Usage:
            delete_format <name_of_format>

        Parameters
        ----------
            name of format: str
                The format to be deleted from formats.json (in PySavuka/docs).
        """
        args, kwargs = utils.parse_options(line)

        if not self.length_match(args, 1):
            name = input("What is the name of the format to be deleted?: ")
        else:
            name = args[0]

        utils.save_formats_to_json(json_path, name, None)
        """Delete the given format from formats.json.
        Usage:
            delete_format <name of format>

        Parameters
        ----------
            name of format: str
                How the format should be called via the read command.
        """
        args, kwargs = utils.parse_options(line)

        if not self.length_match(args, 1):
            name = input("What is the name of the format to be deleted?: ")
        else:
            name = args[0]

        utils.save_formats_to_json(name, None)

    ########################
    # DISPLAY DATA TO USER #
    ########################

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

    def do_print(self, line):
        """Display the buffers that have been read into the program
        Usage:
            print <start> <stop> <step>

        Options:
            start: int, optional
                The first buffer to be displayed. Buffer 0 by default.
            stop: int, optional
                The last buffer to be displayed. The last buffer by default.
            step: int, optional
                Step size of printing. How many buffers should be skipped. 1 by
                default, i.e. no buffers are skipped."""
        args, kwargs = utils.parse_options(line)
        if args:
            if not self.length_match(args, 3, "print"):
                return
            if not self.type_match((args[0], (int,), "start"),
                                   (args[1], (int,), "stop"),
                                   (args[2], (int,), "step"),):
                return
            self.savuka.print_buffers(args[0], args[1], args[2])
        else:
            # Just display everything
            print(self.savuka)


    ###############
    # MUTATE DATA #
    ###############

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

    def do_svd(self, line):
        """usage: svd [file path] [# of spectra]
        Singular value decomposition."""

        return svd.svd()

    ###########
    # FITTING #
    ###########

    def do_models(self, line):
        """list all the descriptions of all available models for fitting.
        Usage:
            models

        Options:
            None
        """
        print("".join(models.get_helps(line)))

    def do_fit(self, line):
        """Fit the data from the given buffer index to the given model. If some
        buffers are not linked in any way to others, then they should not be
        will mess up the fit. In the case of many fits being run independently,
        use the fit_many command.

        Usage:
            fit <buffer index> <model name> -keyword <keyword value>...

        Arguments:
            buffer index: int OR tuple(no spaces, e.g. (0,1,2))
                What buffers should be fit to the model
            model name: string
                The name of the model as specified in models.py

        Keyword arguments:
            type: str, optional
                What type of fitting should be done? Valid values are:
                - `'global'` (default): run the fit with all buffers
                - `'independent'`: run a fit with one set of parameters on
                                   each buffer.
            method: str, optional
                Name of the fitting method to use. Valid values are:
                - `'leastsq'`: Levenberg-Marquardt (default)
                - `'least_squares'`: Least-Squares minimization, using Trust
                                     Region Reflective method by default
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
        if not self.length_match(args, 2, "fit"):
            return

        if not self.type_match((args[0], (int, tuple), "buffer index"),
                               (args[1], (str,), "model name")):
            return

        # make parameters for a single buffer
        if isinstance(args[0], int) or ('type' in kwargs and
                                        kwargs['type'] == 'independent'):
            num_bufs = 1
        # make parameters for multiple buffers.
        elif isinstance(args[0], tuple):
            num_bufs = len(args[0])
        model_name = args[1]

        self.do_parameters("{0} {1}".format(num_bufs, model_name))
        kwargs['parameters'] = self.params
        self.savuka.fit(*args, **kwargs)
        plot_funcs.show()

    def do_clear(self, line):
        """Clear the screen. Equivalent to cls on Windows and clear on Unix."""
        os.system('cls' if os.name == 'nt' else 'clear')

    def do_parameters(self, line):
        """Set the parameters for fitting.
        Usage:
            parameters <number of buffers> <model>

        Arguments:
            number of buffers:
                How many buffers should have parameters specified for the fit?
            model:
                name of the model function that will be fit, as specified by the
                models command
                """
        args, kwargs = utils.parse_options(line)

        if not self.length_match(args, 2, "parameters"):
            return

        num_bufs = args[0]
        model = args[1]
        if not self.type_match((num_bufs, (int, tuple), "number of buffers"),
                               (model, (str,), "model")):
            return

        try:
            model = models.get_models(model)  # convert string to function
        except IndexError:
            print("Model name invalid. You entered [{0}]. Use the models command"
                  " for the list of supported models.".format(model))
            return

        self.params = params.main(num_bufs, model)

    def do_fit_result(self, line):
        """If we have run a fit, print its results"""
        self.savuka.report_result()

    def do_fit_plot(self, line):
        """If we have run a fit, plot it"""
        self.savuka.plot_result()
        plot_funcs.show()

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
        if not self.length_match(args, 1, "chi_error"):
            return

        param_name = args[0]
        if not self.type_match((param_name, (str,), "param name")):
            return

        self.savuka.plot_x2(param_name, **kwargs)
        plot_funcs.show()

    #######################
    # CONVENIENCE METHODS #
    #######################

    def do_debug(self, line):
        """Acts as a test to see if fitting is working correctly. For debugging."""
        self.dr(os.path.join(library_root,
                             r'docs\data-files-for-pysavuka\svd\cytc-saxs.v.csv'
                             ),
                'v')

        self.dr(os.path.join(library_root,
                             r'docs\data-files-for-pysavuka\svd\cytc-tcspc-v-vectors.csv'
                             ),
                'v_vectors')
        self.do_fit('(28,29,30) two_state')
        self.do_chi_error('deltag')

    def dr(self, file_, format):
        """Read in an example dataset. For debugging only"""
        self.savuka.read(file_, format)

    def type_match(self, *args):
        """Check each argument (a tuple with form:
        (value, (type1,...), arg_name)
        and return true if all values match the provided types, else print the
        error message with the given arg_name"""
        for arg in args:
            obj = arg[0]
            types = arg[1]
            obj_name = arg[2]

            match = False
            for t in types:
                if isinstance(obj, t):
                    match = True
                    break
            if not match:
                print("{0} must be of type(s) {1}. You entered [{2}]"
                      "".format(obj_name, str([t.__name__ for t in types]),
                                obj))
                return False
        return True

    def ensure_input_type(self, obj, types, f, msg):
        """Keep asking the user for input until the get it right."""
        if obj is None:  # initial input
            obj = input(msg)
            return self.ensure_input_type(obj, types, f, msg)

        # f changes input to proper type
        correct = f(obj)
        if not self.type_match(correct, types, msg):  # subsequent inputs
            obj = input("What you entered, {0}, is improper. "
                        "{1}".format(correct, msg))
            return self.ensure_input_type(obj, types, f, msg)
        return correct

    def length_match(self, tup, length, command):
        """Return True iff len(tup) == length. Otherwise print help text for
        the command"""
        if len(tup) != length:  # user didn't provide necessary options
            print(self.do_help("{0}".format(command)))
            return False

        return True


def main():
    #os.chdir(os.path.dirname(os.path.abspath(__file__)))
    CommandLine().cmdloop()


if __name__ == '__main__':
    main()
