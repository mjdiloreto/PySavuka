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
        self.prompt = '(savuka)'
        self.params = None
        self.fit = None  #TODO encapsulate fitting

    def postcmd(self, stop, line):
        # wait 1/10 second after each command. This fixes some weird
        # printing bugs when color is involved.
        sleep(0.1)

    def do_quit(self, line):
        """Exit savuka:
        Usage:
            quit <option>

        Options:
            -s save state of the program.
            -d save data loaded in
            """
        print("Exit")
        sys.exit()

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

    @plot_funcs.show_after_completion
    @utils.except_all
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
        '''else:
            # spaces not preceded by commas are used to break up arguments.
            # '(0, 1)' should be represented as '(0, 1)' not '(0,' and '1)'
            for idx, x in enumerate(re.split("(?<!,)\s", line)):
                try:
                    # plot each one
                    self.savuka.plot_buffers(x)
                except NameError as e:
                    # superimpose any plots after the '-s' or '--s' option
                    if re.match("-+s", x) is not None:
                        print("\nsuperimposing plots. "
                              "{0}".format(re.split("(?<!,)\s",
                                                    line)[idx+1:]))
                        self.savuka.plot_superimposed(re.split("(?<!,)\s",
                                                               line)[idx+1:])
                        break
                    else:
                        self.default("{0}\n{1}".format(x, e))'''

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

        @utils.check_input(exceptions_and_params={FileNotFoundError: 0,
                                                  SyntaxError: 1,
                                                  NameError: 1})
        def load_help(filepath, formstyle):
            self.savuka.read(filepath, formstyle)

        if line is "":
            filepath = input("\nFile path to be read: ")
            formstyle = input("\nWhat is the format of the file?: ")
            return load_help(filepath, formstyle)
        else:
            parsed = cmd.Cmd.parseline(self, line)
            return load_help(parsed[0], parsed[1])

    @utils.check_input(exceptions_and_params={})
    def do_print(self, line):
        """Display the data contents of the files read into the program.
        Usage:
            print

        Options:
            None"""
        if line is "":
            print(self.savuka)
            # Todo make line params specify buffer indices and names to print

    @utils.check_input(exceptions_and_params={})
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

    @utils.check_input(exceptions_and_params={})
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

    @utils.check_input(exceptions_and_params={})
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

    @utils.except_all
    def do_fit(self, line):
        # TODO let user redo a fit. Stop calling other methods from this. just save model, fit, result, as attributes.
        """Fit the data from the given buffer index to the given model.
        usage:
            fit <buffer index> -model <name>

            options:
                buffer index: int OR tuple(no spaces, e.g. (0,1,2))
                    What buffers should be fit to the model
                name: string
                    The name of the model as specified in models.py"""
        args, kwargs = utils.parse_options(line)
        if len(args) < 1 or len(kwargs) < 1:
            print(self.do_help("fit"))

        if self.params is None:  # initialize params first
            # make parameters for a single buffer
            if isinstance(args[0], int):
                # THIS DOESNT FOLLOW THE FORMAT SUGGESTED BY self.do_fit!
                num_bufs = 1
            # make parameters for multiple buffers.
            elif isinstance(args[0], tuple):
                # THIS DOESNT FOLLOW THE FORMAT SUGGESTED BY self.do_fit!
                num_bufs = len(args[0])

            self.do_parameters("{0} {1}".format(num_bufs, args[1]))
            self.do_fit(line)
        else:
            kwargs['params'] = self.params
            self.savuka.fit(*args, **kwargs)

    def dr(self, file_, format):
        """Read in an example dataset."""
        self.savuka.read(file_, format)

    def do_parameters(self, line):
        """Set the parameters for fitting.
        Usage:
            pd <number of buffers> <model>

        Options:
            number of buffers:
                How many buffers should have parameters specified for the fit?
            model:
                name of the model function that will be fit, as specified by the
                models command
                """
        args, kwargs = utils.parse_options(line)

        if not line:  # user didn't provide necessary options
            print(self.do_help("parameters"))
            return

        num_bufs = args[0]
        model = args[1]
        model = models.get_models(model)  # convert string to function
        default_params = params.create_default_params(model)
        if self.params is None:  # set the initial guesses
            self.params = default_params
            self.do_parameters('{0}'.format(line))  # rerun with new params
        else:
            self.params = params.main(num_bufs, self.params)

    def do_fit_result(self, line):
        """If we have run a fit, print its results"""
        if isinstance(self.fit, fit.Fit):
            self.fit.report_result()
        else:
            print(self.fit)

    def do_fit_plot(self, line):
        if isinstance(self.fit, fit.Fit):
            self.fit.plot_result()

    def do_rg(self, line):
        self.savuka.read(r'C:\Users\mjdil\Documents\work\Pycharm Projects\PySavuka\docs\data-files-for-pysavuka\gauss_test_data\gauss_data_0.csv',
                         'gauss_test')
        self.savuka.read(
            r'C:\Users\mjdil\Documents\work\Pycharm Projects\PySavuka\docs\data-files-for-pysavuka\gauss_test_data\gauss_data_1.csv',
            'gauss_test')
        self.savuka.read(
            r'C:\Users\mjdil\Documents\work\Pycharm Projects\PySavuka\docs\data-files-for-pysavuka\gauss_test_data\gauss_data_2.csv',
            'gauss_test')
        self.savuka.read(
            r'C:\Users\mjdil\Documents\work\Pycharm Projects\PySavuka\docs\data-files-for-pysavuka\gauss_test_data\gauss_data_3.csv',
            'gauss_test')
        self.savuka.read(
            r'C:\Users\mjdil\Documents\work\Pycharm Projects\PySavuka\docs\data-files-for-pysavuka\gauss_test_data\gauss_data_4.csv',
            'gauss_test')

    def do_debug(self, line):
        self.dr(r'C:\Users\mjdil\Documents\work\Pycharm Projects\PySavuka\docs\data-files-for-pysavuka\svd\cytc-saxs.v.csv',
                   'v')
        self.dr(r'C:\Users\mjdil\Documents\work\Pycharm Projects\PySavuka\docs\data-files-for-pysavuka\svd\cytc-tcspc-v-vectors.csv',
            'v_vectors')
        # THIS DOESNT FOLLOW THE FORMAT SUGGESTED BY self.do_fit!
        self.do_fit('(28,29,30) two_state')

    @utils.except_all
    def do_check(self, line):
        args, kwargs = utils.parse_options(line)
        print("args: {0}".format(args))
        print("kwargs: {0}".format(kwargs))





def main():
    CommandLine().cmdloop()


if __name__ == '__main__':
    main()
