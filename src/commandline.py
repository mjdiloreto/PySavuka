"""This module contains the main program loop and all code for commands passed
to the program."""

from src import savuka
from src import plot_funcs
from src import utils
from src import models
from src import svd

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
    intro = "Welcome to PySavuka. type 'help' for help"

    def __init__(self):
        super(CommandLine, self).__init__()
        self.savuka = savuka.Savuka()

    def postcmd(self, stop, line):
        # wait 1/10 second after each command. This fixes some weird
        # printing bugs when color is involved.
        sleep(0.1)

    def do_quit(self, line):
        """Exit savuka"""
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
        """usage: read
           user will be prompted to select file(s) and asked about the
           format of those files, as specified by supported_formats.txt
           in the docs folder of this project."""
        filepaths = utils.ask_for_files()
        if filepaths is not "":
            formstyle = input("\nFormat of the file(s): ")
            return self.read_help(filepaths, formstyle)

    def read_help(self, filepaths, formstyle):
        for x in filepaths:
            try:
                # store the file's information in the savuka object.
                self.savuka.read(x, formstyle)
            except FileNotFoundError:
                newfilepath = input("\nThe specified path [{0}] does not exist,"
                                    " enter a new one: ".format(filepaths))
                return self.read_help(newfilepath, formstyle)
            except NameError:
                newformstyle = input(
                    "\nThe specified format [{0}] is unsupported,"
                    " enter a new one: ".format(formstyle))
                return self.read_help(filepaths, newformstyle)

    @plot_funcs.show_after_completion
    @utils.check_input(exceptions_and_params={})
    def do_plot(self, line):
        """usage: plot |
            plot <python style list with no spaces, eg [1,2,3]>

            OPTIONS:
            -s      superimpose the plots

            plots the buffers specified by the given ranges (either integers
            or python tuples)."""
        args = re.split("\s", line)
        if line is '':
            # default behavior is to plot everything in separate windows.
            self.savuka.plot_buffers(range(len(self.savuka)))
        elif '-s' in args:
            self.savuka.plot_superimposed(utils.string_to_index_list(args[0]))
        else:
            self.savuka.plot_buffers(utils.string_to_index_list(args[0]))
            print(utils.string_to_index_list(args[0]))
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

    def do_load(self, line):
        # TODO make the precmd method split line into args and pass to commands. use utils.parse_options and change all arguments <line> to the actual args it should take.
        """usage: load [file path] [format type]
            format type will be the name of the instrument
            used to collect the data. /docs/supported_formats.txt
            for more"""

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
        """Display the data contents of the files read into the program."""
        if line is "":
            print(self.savuka)
            # Todo make line params specify buffer indices and names to print

    @utils.check_input(exceptions_and_params={})
    def do_shift(self, line):
        """Add two buffers along the desired """
        args = utils.parseline(line)
        self.savuka.shift_buffer(utils.intify(args[0]), utils.floatify(args[1]))

    @utils.check_input(exceptions_and_params={})
    def do_scale(self, line):
        args = utils.parseline(line)
        self.savuka.scale_buffer(utils.intify(args[0]), utils.floatify(args[1]))

    @utils.check_input(exceptions_and_params={})
    def do_pow(self, line):
        args = utils.parseline(line)
        self.savuka.pow_buffer(utils.intify(args[0]), utils.floatify(args[1]))

    def do_check(self, line):
        if '\t' in line:
            print('y')
        else:
            print('n')

    def do_formatload(self, line):
        """Dumbest method of formatting. Won't assume anything about data,
        but will ask the user everything and save the answers in
        formats.txt"""
        files = utils.ask_for_files()
        cols = utils.intify(input("How many columns?: "))
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

    def do_fit(self, line):
        """Usage: fit buffer<int> model<name defined in models.py> """
        pass

    def do_models(self, line):
        """list all the descriptions of all available models for fitting."""
        print("".join(models.get_helps(line)))

    def do_fit(self, line):
        """Fit the data from the given buffer index to the given model."""
        # TODO have options associated with parameters and check them here
        args, kwargs = utils.parse_options(line)
        self.savuka.fit(*args, **kwargs)

    def do_dr(self, line):
        """Read in an example dataset."""
        if line == 'xy1':
            self.savuka.read(r"C:\Users\mjdil\Documents\work\Pycharm Projects\PySavuka\docs\xyexample1.txt", "example")
        elif line == 'photo':
            self.savuka.read(r"C:\Users\mjdil\Documents\work\Pycharm Projects\PySavuka\docs\data-files-for-pysavuka\applied-photophysics-stopped-flow-data\R9.csv", "photo")


def main():
    CommandLine().cmdloop()


if __name__ == '__main__':
    main()
