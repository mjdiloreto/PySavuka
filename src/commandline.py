"""This module contains the main program loop and all code for commands passed
to the program."""

from src import savuka
from src import plot_funcs
from src import utils
from src import svd

import cmd
import re
import os

from sys import stderr, stdout
from time import sleep

# don't change the location of any files in this package.
library_root = os.path.abspath(os.path.join(__file__, "..\.."))

formats_path = os.path.join(library_root, r'docs\supported_formats.txt')

FORMATS = open(formats_path).read()

# TODO change tuple command to use int-int syntax and convert that to tuple


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
        return True

    def do_help(self, arg):
        """Print help text in red. Kind of a hack since stderr is always red."""
        self.stdout = stderr
        cmd.Cmd.do_help(self, arg)
        self.stdout = stdout

    # TODO add command to show data in savuka

    def default(self, line):
        print("This command is unsupported: {0}".format(line))

    def do_read(self, line):
        """usage: read
           user will be prompted to select file(s) and asked about the
           format of those files, as specified by supported_formats.txt
           in the docs folder of this project."""
        filepaths = utils.get_filenames()
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
        self.savuka.shift_buffer(utils.intify(args[0]),
                                 utils.floatify(args[1]))

    @utils.check_input(exceptions_and_params={})
    def do_scale(self, line):
        args = utils.parseline(line)
        self.savuka.scale_buffer(utils.intify(args[0]),
                                 utils.floatify(args[1]))

    @utils.check_input(exceptions_and_params={})
    def do_pow(self, line):
        args = utils.parseline(line)
        self.savuka.pow_buffer(utils.intify(args[0]),
                               utils.floatify(args[1]))

    def do_check(self, line):
        pass


def main():
    CommandLine().cmdloop()


if __name__ == '__main__':
    main()
    #c = CommandLine()
    #c.check(None, a=None)

