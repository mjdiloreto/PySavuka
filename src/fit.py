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


def objective(params, data, model):
    """Calculate total residual for fits to either a single dataset or
    multiple datasets contained in a 2D array, and fit to the model."""
    ndata = len(data)
    # There should really be two functions, one for fitting single buffers, and
    # one for fitting multiple. This will work though.

    try:  # multiple buffer case
        resid = 0.0 * np.asarray([data[i]['y'] for i in range(ndata)])
        # make residual per data set
        for i in range(ndata):
            resid[i] = data[i]['y'] - generate_dataset(params, i, data[i]['x'],
                                                       model)
        # now flatten this to a 1D array, as minimize() needs
        return resid.flatten()
    except ValueError:  # This is the case for single buffers
        resid = data[0]['y'] - generate_dataset(params, 0, data[0]['x'], model)
        return resid.flatten()


def fit(data, model, params={}):
    """Fit the data [a 1-d array] to the model with the x axis [a 1-d array]."""
    # find the function object with the given name from the models.
    model = models.get_models(model)

    result = minimize(objective, params, args=(data, model))
    return (result, data, model)


def report_result(result):
    """If there is a result, display it."""
    if isinstance(result, MinimizerResult):
        print(fit_report(result.params))
        if hasattr(result, "chisq"):
            print("[[Chi sq]]\n\s\s\s\s{0}".format(result.chisq))
        if hasattr(result, "redchi"):
            print("[[Chi sq (reduced)]]\n\t{0}".format(result.redchi))
    else:
        print("There was no result to the fit. "
              "<{0}> was returned instead".format(result))


def plot_result(result, data, model):
    """Plot the fitted curves from a MinimizerResult object."""
    plt.figure()

    # TODO handle discrepancy between one and multiple buffers. DRY
    if len(data) == 1:
        fitted_ys = generate_dataset(result.params, 0, data[0]['x'], model)
        plt.plot(data[0]['x'], data[0], 'o', data[0]['x'], fitted_ys, '-')

    else:
        for name, param in result.params.items():
            print("{0}: {1}".format(name, param.value))
        for i in range(len(data)):
            xs = data[i]['x']
            ys = data[i]['y']

            fig = plt.figure()
            frame1 = fig.add_axes((.1,.3,.8,.6))
            fitted_ys = generate_dataset(result.params, i, xs, model)
            plt.plot(xs, ys, 'o', xs, fitted_ys, '-')
            frame2 = fig.add_axes((.1,.1,.8,.2))
            new_x = np.linspace(xs[0], xs[-1], result.residual.shape[0])
            plt.plot(new_x, result.residual, '-')
            frame2.set_ylabel('$Residual$')


    plt.show()