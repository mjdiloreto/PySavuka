"""A setuptools based setup module for pysavuka"""
#!/usr/bin/env python
# -*- coding: utf-8 -*-

from codecs import open
import os
from os import path, system, popen, walk
from setuptools import setup, find_packages
from setuptools.command.install import install

from sys import platform, stdout

# Get the location of the README.rst file
here = path.dirname(path.realpath(__file__))
with open(os.path.join(here, 'README.rst'), encoding='utf-8') as readme_file:
    readme = readme_file.read()

# any extra files that should be included with the installation of pysavuka
# should be added to this list. This will add the files to the docs folder
# of the src package when it is installed on a user's machine.
files = []
for path, directories, filenames, in walk(os.path.join(here, 'src/docs')):
    for filename in filenames:
        if filename.startswith("cytc"):  # example svd data
            files.append(os.path.join('..', path, filename))
        elif "json" in filename:  # actually necessary for program to run.
            files.append(os.path.join('..', path, filename))

unix_requirements = [
    'numpy',
    'matplotlib',
    'scipy',
    'lmfit',
    # 'PyQt5'  # Downloaded explicitly, just in case.
]

win32_requirements = [
    'matplotlib',
    'PyQt5',
    'lmfit'
    # 'numpy',  # must be installed manually (Don't go down this rabbit hole).
    # 'scipy',  # must be installed manually (Don't go down this rabbit hole).
]

test_requirements = [
    'unittest',
]

# determine which requirements to use.
requirements = win32_requirements if platform == 'win32' else unix_requirements


class CustomInstallCommand(install):
    """Custom install setup to help run shell commands (outside shell)
    before installation"""

    # either pip or pip3, depending on which version(s) of python are installed.
    _pip = "pip"

    # change to brew or port for mac
    _apt = 'apt-get'

    _requirements = requirements

    def _init_cmd_tools(self, plat):
        """Determines which version of pip to use, pip or pip3."""
        if plat == 'win32':
            # Use the where command to find python, then find version number.
            pypath = popen("where python").read()
            version = popen("{0} --version".format(pypath)).read()

            # if python is automatically 3, then pip == pip3
            if version.startswith("Python 3."):
                self._pip = 'pip'
            # 90% sure python aliases pip to pip3 when downloading python3 on
            # top of python 2.
            elif version.startswith("Python 2."):
                self._pip = 'pip3'
        elif plat == 'darwin':
            # either brew or port, not sure which is better.
            # install brew
            brew = popen("which brew").read()
            if not brew:  # install brew if it isn't already.
                system("/usr/bin/ruby -e \"$(curl -fsSL https://raw.githubusercontent.com/Homebrew/install/master/install)\"")
            self._apt = 'brew'
            system("sudo {0} install python3-pip".format(self._apt))
            self._pip = 'pip3'
        # I've found that PyQt5 ONLY installs with pip3.
        elif plat.startswith("linux"):
            # install pip3.
            system("sudo {0} install python3-pip".format(self._apt))
            self._pip = 'pip3'

    def windows_install(self):
        # Does not check for tkinter. Should be included in any new python
        # version though.
        try:
            import scipy
        except ImportError:
            stdout.write("You must install "
                         "numpy-1.13.1+mkl-cp36-cp36m-win_amd64.whl"
                         "and scipy-0.19.1-cp36-cp36m-win_amd64.whl from "
                         "http://www.lfd.uci.edu/~gohlke/pythonlibs/#numpy. "
                         "Follow the instructions outlined in README.rst")
            raise SystemExit
        try:
            import tkinter
        except ImportError:
            stdout.write("You must have tkinter installed. You can either "
                "reinstall Python 3.6.1, or follow the instructions at"
                " http://www.tkdocs.com/tutorial/install.html#installwin"
                "\nLink to the site is in README.rst.")
            raise SystemExit

    def mac_install(self):
        # 90% sure this will work. Once brew is installed, the packages should
        # be exactly identical. Has not been tested.
        self.unix_install()

    def unix_install(self):
        try:
            import tkinter
        except ImportError:
            stdout.write("Collecting tkinter...\n")
            system("sudo {0} install python3-tk".format(self._apt))
        try:
            import PyQt5
        except ImportError:
            stdout.write("Collecting PyQt5...\n")
            system("{0} install PyQt5".format(self._pip))

    def install_requirements(self):
        for req in self._requirements:
            stdout.write("Installing {0}...\n".format(req))
            system("{0} install {1}".format(self._pip, req))

    def run(self):
        self._init_cmd_tools(platform)

        if platform == 'win32':
            self.windows_install()
        elif platform.startswith('linux'):
            self.unix_install()
        elif platform == 'darwin':
            self.mac_install()

        self.install_requirements()
        install.run(self)


setup(
    cmdclass={'install': CustomInstallCommand},
    name='pysavuka',
    version='1.0',
    description="pysavuka",
    long_description=readme,
    author="Matthew DiLoreto",
    author_email='mjdiloreto@gmail.com',
    url='https://github.com/mjdiloreto/pysavuka',
    packages=['src'],
    entry_points={
        'console_scripts': [
            'pysavuka=src.commandline:main',
            ],
        },
    include_package_data=True,
    # include formats.json and example data in package when installing.
    package_data={"": files},
    install_requires=requirements,
    license="MIT",
    classifiers=[
        'Development Status :: 2 - Pre-Alpha',
        'License :: OSI Approved :: MIT License',
        'Natural Language :: English',
        'Programming Language :: Python :: 3.3',
        'Programming Language :: Python :: 3.4',
        'Programming Language :: Python :: 3.5',
        'Programming Language :: Python :: 3.6',
    ],
    test_suite='tests',
)
