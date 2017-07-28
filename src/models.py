"""This module should contain all models to be used by the fitting routines."""

import matplotlib.pyplot as plt
import numpy as np

import inspect
import sys

# All the models currently implemented
MODELS = ['linear', 'gaussian_1d']

#  look to lmfit.lineshapes for a sampling of models

# Guesses for models if user doesn't specify any parameters.
INITIAL_GUESSES = {
    'linear': {'slope': 1.0, 'intercept': 0.0},
    'gaussian_1d': {'amp': 1.0, 'cen': 0.0, 'wid': 1.0},
}


def list_models(name=None):
    """Return a list of all the model functions in this module."""
    funcs = inspect.getmembers(sys.modules[__name__], inspect.isfunction)

    if not name:
        # return the functions from all models in the list
        fit_models = [f for f in funcs if f[0] in MODELS]
    else:
        fit_models = [f for f in funcs if f[0] in MODELS and name in f[0]]

    return fit_models


def get_helps(name=None):
    """Return the list of help texts from the model functions (__doc__ aka the
    triple-quoted lines below the fucntion definition."""
    return [m[1].__doc__ for m in list_models(name)]


def linear(x, slope, intercept):
    """
    linear:
        Parameters
                ----------
                x : array of values (data to be fit to linear model).
                slope : float
                    rate of change of x.
                intercept : float
                    y-intercept of fitted linear model.

            """
    return slope * x + intercept


def gaussian_1d(x, amp, cen, wid):
    """
    gaussian (1-d):
        Parameters
                ----------
                x : array of values (data to be fit to gaussian model).
                amplitude : float
                    rate of change of x.
                center : float
                    y-intercept of fitted linear model.
                sigma : float
                    standard deviation

                    """

    return (amp/(np.sqrt(2*np.pi)*wid)) * np.exp(-(x-cen)**2/(2*wid**2))






