from src import models

import re

import numpy as np
import matplotlib.pyplot as plt
from lmfit import minimize
from lmfit.printfuncs import fit_report
from lmfit.minimizer import MinimizerResult


def generate_dataset(params, i, x, model):
    """calc data from params for data set i. This function depends on the
    essential requirement that ALL Parameter names are in the form:
    name_i
    where name is the parameter name, and i is the number buffer that
    it is tied to."""
    # get all the parameters whose names end in the number i, and assign them
    # to parameter names that do not end in i
    parameters = {re.sub('_[0-9]*', '', k): v.value for k, v in params.items()
                  if re.match('.*(?<=_){0}'.format(i), k) is not None
                  and re.match('.*(?<=_){0}'.format(i), k).end() == len(k)}

    return model(x, **parameters)


def objective(params, x, data, model):
    """Calculate total residual for fits to either a single dataset or
    multiple datasets contained in a 2D array, and fit to the model."""
    ndata = data.shape
    if len(data.shape) == 1:  # fit a single dataset
        resid = 0.0 * data[:]
        resid[:] = data[:] - generate_dataset(params, 0, x, model)
        return resid.flatten()

    elif len(data.shape) == 2:  # fit multiple datasets
        resid = 0.0 * data[:]
        # make residual per data set
        for i in range(ndata[0]):
            resid[i, :] = data[i, :] - generate_dataset(params, i, x, model)
        # now flatten this to a 1D array, as minimize() needs
        return resid.flatten()


def fit(data, model, x, params={}):
    """Fit the data [a 1-d array] to the model with the x axis [a 1-d array]."""
    # find the function object with the given name from the models.
    model = models.get_models(model)

    result = minimize(objective, params, args=(x, data, model))
    return (result, data, x, model)


def report_result(result):
    """If there is a result, display it."""
    if isinstance(result, MinimizerResult):
        print(fit_report(result.params))
    else:
        print("There was no result to the fit. "
              "<{0}> was returned instead".format(result))


def plot_result(result, data, x, model):
    """Plot the fitted curves from a MinimizerResult object."""
    plt.figure()

    # TODO handle discrepancy between one and multiple buffers. DRY
    if len(data.shape) == 1:
        fitted_ys = generate_dataset(result.params, 0, x, model)
        plt.plot(x, data[:], 'o', x, fitted_ys, '-')

    elif len(data.shape) == 2:
        for i in range(data.shape[0]):
            fitted_ys = generate_dataset(result.params, i, x, model)
            plt.plot(x, data[i, :], 'o', x, fitted_ys, '-')

    plt.show()