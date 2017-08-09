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
    'terminaltables'
]

win32_requirements = [
    'numpy',
    'matplotlib',
    'PyQt5',
    'terminaltables'

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

# as it turns out, downloading and installing external whl files is not trivial.
"""if platform == 'win32':
    try:
        import tkinter
    except ImportError:
        system("pip3 install tkinter")
        # download scipy from Gohlke's site and install
        # also download and install numpy+MKL

    # https://stackoverflow.com/questions/7243750/download-file-from-web-in-python-3
    import urllib.request
    import shutil

    def get_from_url(url, file_name):
        # Download the file from `url` and save it locally under `file_name`:
        with urllib.request.urlopen(url) as response, open(file_name,
                                                           'wb') as out_file:
            shutil.copyfileobj(response, out_file)


    get_from_url(r'www.lfd.uci.edu/~gohlke/pythonlibs/numpy‑1.13.1+mkl‑cp36‑cp36m‑win_amd64.whl',
                 path.join(here, 'numpy_download.whl'))

else:  # should work for unix and mac
    system("sudo apt install python3-tk")"""