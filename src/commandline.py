import savuka
import utils
import svd

import cmd
import matplotlib.pyplot as plt
import re

from os import path

# don't change the location of any files in this package.
library_root = path.abspath(path.join(__file__, "..\.."))

formats_path = path.join(library_root, r'docs\supported_formats.txt')

FORMATS = open(formats_path).read()



class CommandLine(cmd.Cmd):
    intro = "Welcome to PySavuka. type 'help' for help"

    def __init__(self):
        super(CommandLine, self).__init__()
        self.savuka = savuka.Savuka()

    def do_quit(self, line):
        """Exit savuka"""
        print("Exit")
        return True

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

    def do_plot(self, line):
        """usage: plot |
            plot (start, end) (start, end) ...

            OPTIONS:
            -s      superimpose the plots from this point forward.

            plots the buffers specified by the given ranges (either integers
            or python tuples)."""
        if line is "":
            # default behavior is to plot everything in separate windows.
            self.savuka.plot_all_buffers()
        else:
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
                        print("the given option"
                              " is unsupported: {0}\n{1}".format(x, e))
        plt.show()

    def do_svd(self, line):
        """usage: svd [file path] [# of spectra]
        Singular value decomposition."""

        filename = utils.get_filename()
        spectra = input("\n# of spectra to be read: ")

        return svd.svd(filename, spectra)

    def do_load(self, line):
        """usage: read [file path] [format type]
            format type will be the name of the instrument
            used to collect the data. /docs/supported_formats.txt
            for more"""
        if line is "":
            filepath = input("\nFile path to be read: ")
            formstyle = input("\nWhat is the format of the file?: ")
            return self.load_help(filepath, formstyle)
        else:
            parsed = cmd.Cmd.parseline(self, line)
            return self.load_help(parsed[0], parsed[1])

    @utils.check_input(exceptions_and_params={FileNotFoundError: 0,
                                              NameError: 1})
    def load_help(self, filepath, formstyle):
        self.savuka.read(filepath, formstyle)

    @utils.check_input(exceptions_and_params={TypeError: 0,
                                              ValueError: 0})
    def check(self, idx, a='s'):
        print("checking {0} {1}".format(a, float(idx)**2))


def main():
    return CommandLine().cmdloop()


if __name__ == '__main__':
    main()
    #c = CommandLine()
    #c.check(None, a=None)

