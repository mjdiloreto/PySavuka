PySavuka
########

PySavuka is a complete re-design of Savuka - a general purpose global analysis program. The program is implemented in python 3 and designed to be used on any machine with a python interpreter. To read more about the original Savuka program, visit http://www.osmanbilsel.net/software/savuka


Installation
============
Regardless of operating system, it is recommended to install `Anaconda 4.4.0 <https://www.continuum.io/downloads>`_.

Next, download this repo:

.. code-block:: bash

    $ git clone https://github.com/mjdiloreto/PySavuka.git

navigate to the PySavuka folder, then:

.. code-block:: bash

    $ pip install .

To use the program, use the pysavuka command in terminal from any directory.

.. code-block:: bash

    $ pysavuka


It is also possible to download the necessary packages in the Anaconda libraries manually.
First, download and install:
    `numpy‑1.13.1+mkl‑cp36‑cp36m‑win_amd64.whl <http://www.lfd.uci.edu/~gohlke/pythonlibs/#numpy>`_.
It is important to make sure that you use this version of numpy, and not just the version downloaded by 'pip install numpy' because that will not include the Intel Math Kernal Library.
Next, install:
    `scipy‑0.19.1‑cp36‑cp36m‑win_amd64.whl <http://www.lfd.uci.edu/~gohlke/pythonlibs/#scipy>`_.

You should then be able to clone this repository (see above), install it with pip, and use the pysavuka command