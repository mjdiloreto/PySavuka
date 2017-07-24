"""A setuptools based setup module for pysavuka"""
#!/usr/bin/env python
# -*- coding: utf-8 -*-

from codecs import open
from os import path, system
from setuptools import setup, find_packages

from sys import platform, stdout


here = path.abspath(path.dirname(__file__))

with open(path.join(here, 'README.rst'), encoding='utf-8') as readme_file:
    readme = readme_file.read()

unix_requirements = [  # should work for mac and linux
    'numpy',
    'matplotlib',
    'scipy',
    'PyQt5',
]

win32_requirements = [
    'numpy',
    'matplotlib',
    'PyQt5',
    # 'scipy'  # -need to install wheel from Christopher Gohlke's website
]

requirements = win32_requirements if platform == 'win32' else unix_requirements

test_requirements = [
    'unittest',
]

setup(
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
            'savuka=src.commandline:main',
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

if platform == 'win32':
    try:
        import tkinter
    except ImportError:
        system("pip3 install tkinter")

    from os import fdopen
    s = stdout  # remember current stdout

    # Needed for unbuffered I/O
    unbuffered = fdopen(stdout.fileno(), 'w', 0)
    stdout = unbuffered

    stdout.write("Im in windows")

    # set it back to original
    stdout = s

else:
    system("sudo apt install python3-tk")