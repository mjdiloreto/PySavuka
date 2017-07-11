"""A setuptools based setup module for pysavuka"""
#!/usr/bin/env python
# -*- coding: utf-8 -*-

from codecs import open
from os import path
from setuptools import setup, find_packages


here = path.abspath(path.dirname(__file__))

with open(path.join(here, 'README.rst'), encoding='utf-8') as readme_file:
    readme = readme_file.read()

requirements = [
    # TODO: put package requirements here
    'numpy',
    'matplotlib',
    # 'scipy' - for cubic spline interpolation
]

test_requirements = [
    # TODO: put package test requirements here
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
    tests_require=test_requirements,
)
