from src import models

import re

import numpy as np
import matplotlib.pyplot as plt
from lmfit import minimize


def generate_dataset(params, i, x, model):
    """calc data from params for data set i"""
    # get all the parameters whose names end in the number i
    parameters = [v.value for k, v in params.items()
                  if re.match('.*(?<=_){0}'.format(i), k) is not None
                  and re.match('.*(?<=_){0}'.format(i), k).end() == len(k)]
    return model(x, *parameters)


def objective(params, x, data, model):
    """Calculate total residual for fits to either a single dataset or
    multiple datasets contained in a 2D array, and fit to the model."""
    ndata = data.shape
    if len(data.shape) == 1:  # fit a single dataset
        resid = 0.0 * data[:]
        resid[:] = data[:] - generate_dataset(params, 0, x, model)
        return resid.flatten()

    elif len(data.shape) == 2:  # fit multiple datasets
        resid = 0.0*data[:]
        # make residual per data set
        for i in range(ndata[0]):
            resid[i, :] = data[i, :] - generate_dataset(params, i, x, model)
        # now flatten this to a 1D array, as minimize() needs
        return resid.flatten()


def fit(data, model, x, params={}):
    """Fit the data [a 1-d array] to the model with the x axis [a 1-d array]."""
    '''
    

    m = lmfit.models.Model(model)
    result = m.fit(data, x=x, **params)
    print(result.fit_report())
    result.plot()
    plt.show()'''

    # find the function object with the given name from the models.
    model = models.get_models(model)

    result = minimize(objective, params, args=(x, data, model))
    print(result.params)


# TODO how to plot data?
#    TODO either use builtin result.plot()
#    TODO or pass data and return values to plot_funcs

if __name__ == '__main__':
    x = np.linspace(0, 15, 200)
    y = x + np.random.normal(size=200, scale=.35)


    fit(y, 'linear', x)
    plt.show()

    """m = lmfit.models.Model.GaussianModel
        result = m.fit(y, x=x, amp=2, cen=2, wid=2)

        print(result.fit_report())

        lm = lmfit.models.Model(linear)
        lresult = lm.fit(y, x=x, slope=1.5, intercept=1.0)
        print(lresult.fit_report())

        plt.plot(x, y, 'bo')
        plt.plot(x, result.init_fit, 'k--')
        plt.plot(x, result.best_fit, 'r-')

        plt.figure(2)
        plt.plot(x, y, 'bo')
        plt.plot(x, lresult.init_fit, 'k--')
        plt.plot(x, lresult.best_fit, 'r-')
        plt.show()"""
