PySavuka
########

PySavuka is a complete re-design of Savuka - a general purpose global analysis program, originally written in FORTRAN in the 1980s. The program is implemented in python 3 and designed to be used on any machine with a python interpreter. To read more about the original Savuka program, visit http://www.osmanbilsel.net/software/savuka


Linux/mac Installation
============
Installation has only been tested on Windows and Unix systems.

First, download this repo:

.. code-block:: bash

    $ git clone https://github.com/mjdiloreto/PySavuka.git

Next, navigate to the PySavuka folder, then:

.. code-block:: bash

    $ python setup.py install

If there are more than one python installation on your machine, be sure to use ``python3 setup.py install`` instead.

To use the program, use the pysavuka command in terminal from any directory.

.. code-block:: bash

    $ pysavuka

After following these instructions on Windows, it is possible to get an error message complaining that ``tkinter`` is not installed. All python versions since 3.1 have shipped with tkinter, but it is possible to not install it while setting up python. If you have this issue, you will have to `manually installed tkinter <http://www.tkdocs.com/tutorial/install.html#installwin>`_.

Windows Installation
====================
Windows installation rely on `Anaconda 4.4.0 <https://www.continuum.io/downloads>`_ for numpy and scipy dependencies. If Anaconda is installed, follow the instructions for Unix installation above.

If you do not have Anaconda installed, it is also possible to download the necessary packages in the Anaconda libraries manually.
First, download:
    `numpy‑1.13.1+mkl‑cp36‑cp36m‑win_amd64.whl <http://www.lfd.uci.edu/~gohlke/pythonlibs/#numpy>`_.
Navigate to your Downloads folder, and run:
.. code-block:: bash

    $ pip install numpy‑1.13.1+mkl‑cp36‑cp36m‑win_amd64.whl

It is important to make sure that you use this version of numpy, and not just the version downloaded by 'pip install numpy' because that will not include the Intel Math Kernal Library.
Next, download and install:
    `scipy‑0.19.1‑cp36‑cp36m‑win_amd64.whl <http://www.lfd.uci.edu/~gohlke/pythonlibs/#scipy>`_.
.. code-block:: bash

    $ pip install scipy‑0.19.1‑cp36‑cp36m‑win_amd64.whl

You should then be able to clone this repository (see above), install it with pip, and use the pysavuka command

Usage
=====

The general command syntax for PySavuka reflects that of function calls in python, as opposed to most other comandline programs, which have Unix style commands.
In python, functions are defined as follows:

.. code-block:: python

    def function(*args, **kwargs):
        # code ...
        # ...

where *args is the *unpacked* tuple of positional arguments, and **kwargs is the *unpacked* dictionary of keyword arguments.
For example, when one calls ``function`` as:

.. code-block:: python

    function(1,2,3, keyword1=4, keyword2=5)

The positional arguments 1,2, and 3 are passed to the function in args as ``(1,2,3)``, and 4 and 5 are passed as values to the dictionary kwargs as ``{'keyword1': 4, 'keyword2': 5}``.

PySavuka uses this type of syntax for commands to reflect the fact that each command is really just calling a python function.
To denote positional arguments, the user simply separates values from the command using spaces. So the PySavuka command:

.. code-block:: bash

    (pysavuka) fit 0 gauss

will pass ``(0, 'gauss')`` to the fitting function as args, and an empty dictionary as kwargs.

To denote keyword arguments, PySavuka uses the ``-`` character. For example:

.. code-block:: bash

    (pysavuka) fit 0 gauss -debug True -method differential_evolution

will pass (0, 'gauss') to the fitting function as args, but pass ``{'debug':True, 'method': 'differential_evolution'}`` as kwargs.
Typing:
.. code-block:: bash
    (pysavuka) help fit
will provide requirements for positional arguments, and give a list of valid keyword arguments and values.