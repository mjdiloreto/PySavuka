"""This module should contain all models to be used by the fitting routines.
The default parameters of the functions will be used as starting guesses to
the parameter if the user doesn't provide them."""

import numpy as np

import inspect
import sys

# All the models currently implemented
# The format of the dictionary is:
#   exact_name_of_function: [list of aliases the user can use]
MODELS = {'linear': ['linear', 'line'],
          'gaussian_1d': ['gaussian_1d', 'gauss', 'gaussian', '1dgauss'],
}

#  look to lmfit.lineshapes for a sampling of models


def get_models(name=None):
    """Return a list of all the model functions in this module."""
    funcs = inspect.getmembers(sys.modules[__name__], inspect.isfunction)

    if not name:
        # return the functions from all models in the list
        fit_models = [f[1] for f in funcs if f[0] in MODELS]
    else:
        # return the function if it is in fact a model function and the
        # provided name matches one of the aliases.
        fit_models = [f[1] for f in funcs if f[0] in MODELS.keys()
                      and name in MODELS[f[0]]]
        # if you provide a name, you expect one function
        return fit_models[0]
    # otherwise, you expect a list of function objects.
    return fit_models


def get_helps(name=None):
    """Return the list of help texts from the model functions (__doc__ aka the
    triple-quoted lines below the fucntion definition."""
    return [m.__doc__ for m in get_models(name)]


def linear(x, intercept=0.0, slope=1.0):
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


def gaussian_1d(x, amp=1.0, cen=1.0, wid=1.0):
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






