"""A setuptools based setup module for pysavuka"""
#!/usr/bin/env python
# -*- coding: utf-8 -*-

from codecs import open
from os import path, system, popen
from setuptools import setup, find_packages
from setuptools.command.install import install

from sys import platform, stdout


here = path.dirname(path.realpath(__file__))
with open(path.join(here, 'README.rst'), encoding='utf-8') as readme_file:
    readme = readme_file.read()

unix_requirements = [  # should work for mac and linux
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
    # 'numpy',  # installed from docs/windows_requires folder
    # 'scipy'  # installed from docs/windows_requires folder
]

requirements = win32_requirements if platform == 'win32' else unix_requirements


class CustomInstallCommand(install):
    """Custom install setup to help run shell commands (outside shell) before installation"""

    # either pip or pip3, depending on which version(s) of python are installed.
    _pip = "pip"

    _requirements = requirements

    def _which_pip(self, plat):
        """Determines which version of pip to use, pip or pip3."""
        if plat == 'win32':
            # Use the where command to find python, then find version number.
            pypath = popen("where python").read()
            version = popen("{0} --version".format(pypath)).read()

            # if python is automatically 3, then pip == pip3
            if version.startswith("Python 3."):
                self._pip = "pip"
            # 90% sure python aliases pip to pip3 when downloading python3 on
            # top of python 2.
            elif version.startswith("Python 2."):
                self._pip = "pip3"

        # I've found that PyQt5 ONLY installs with pip3.
        elif plat.startswith("linux"):
            # install pip3.
            system("sudo apt-get install python3-pip")
            self._pip = "pip3"

    def windows_install(self):
        # Does not check for tkinter. Should be included in any new python
        # version though.

        numpy_install = path.abspath(path.join(here,
            r'docs/windows_requires/numpy-1.13.1+mkl-cp36-cp36m-win_amd64.whl'))
        scipy_install = path.abspath(path.join(here,
            r'docs/windows_requires/scipy-0.19.1-cp36-cp36m-win_amd64.whl'))

        try:
            import scipy
        except ImportError:
            stdout.write("Installing numpy...\n")
            system("{0} install \"{1}\"".format(self._pip, numpy_install))

            stdout.write("Installing scipy...\n")
            system("{0} install \"{1}\"".format(self._pip, scipy_install))

    def mac_install(self):
        # TODO add support for Mac. I (mjdiloreto@gmail.com) don't have an os to play with.

        # To implement, try the unix stuff, probably make sure brew or port
        # are downloaded, install tkinter if not included, then see which
        # unix calls break, and replace them with mac-specific commands.
        self.unix_install()

    def unix_install(self):
        try:
            import tkinter
        except ImportError:
            stdout.write("Collecting tkinter...\n")
            system("sudo apt-get install python3-tk")
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
        self._which_pip(platform)
        if platform == 'win32':
            self.windows_install()
        elif platform.startswith('linux'):
            self.unix_install()
        elif platform == 'darwin':
            self.mac_install()

        self.install_requirements()
        install.run(self)


test_requirements = [
    'unittest',
]

setup(
    cmdclass={'install': CustomInstallCommand},
    name='pysavuka',
    version='1.0',
    description="pysavuka",
    long_description=readme,
    author="Matthew DiLoreto",
    author_email='mjdiloreto@gmail.com',
    url='https://github.com/mjdiloreto/pysavuka',
    packages=find_packages(exclude=['contrib', 'docs', 'tests']),
    entry_points={
        'console_scripts': [
            'pysavuka=src.commandline:main',
            ],
        },
    include_package_data=True,
    install_requires=requirements,
    license="MIT",
    classifiers=[
        'Development Status :: 2 - Pre-Alpha',
        'Intended Audience :: Developers',
        'License :: OSI Approved :: MIT License',
        'Natural Language :: English',
        'Programming Language :: Python :: 3.3',
        'Programming Language :: Python :: 3.4',
        'Programming Language :: Python :: 3.5',
        'Programming Language :: Python :: 3.6',
    ],
    test_suite='tests',
)
