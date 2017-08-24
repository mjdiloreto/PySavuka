from src import models
from src import params

import re

import numpy as np
import matplotlib.pyplot as plt
from lmfit import minimize
from lmfit.printfuncs import fit_report
from lmfit.minimizer import MinimizerResult


def generate_dataset(parameters, i, x, model):
    """calc data from params for data set i. This function depends on the
    essential requirement that ALL Parameter names are in the form:
    name_i
    where name is the parameter name, and i is the number buffer that
    it is tied to. This is run thousands of times. If any optimization must be
    done, it should be here.

    Parameters
    ----------
        parameters: lmfit.Parameters
            OrderedDict of lmfit.Parameter objects that will be passed to
            the objective function to be dispatched to the model function.
        i: int
            Index of dataset to have its model result calculated. Used to
            determine which Parameter objects belong to which datasets.
        x: np.ndarray (1D)
            X-axis values that data was collected at.
        model: function object
            The actual function used to calculate the fit.
    """
    # get all the parameters whose names end in the number i, and assign them
    # to parameter names that do not end in i
    parameters = {re.sub('_[0-9]*', '', k): v.value for k, v in parameters.items()
                  if re.match('.*(?<=_){0}'.format(i), k) is not None
                  and re.match('.*(?<=_){0}'.format(i), k).end() == len(k)}

    return model(x, **parameters)


def calc_resids(parameters, data, i, x, model):
    """Calculate the residuals for dataset i in data.

    Parameters
    ----------
        parameters: lmfit.Parameters
            OrderedDict of lmfit.Parameter objects that will be passed to
            the objective function to be dispatched to the model function.
        data: np.ndarray (multi-dimensional)
            Experimental data. Passed to objective to calculate residuals.
        i: int
            Index of dataset to have its model result calculated. Used to
            determine which Parameter objects belong to which datasets.
        x: np.ndarray (1D)
            X-axis values that data was collected at.
        model: function object
            The actual function used to calculate the fit.

    Returns
    -------
        1D np.ndarray of residual values for fit calculated by
        subtracting experimental y-values from calculated y-values from the
        model function using the parameters applicable to dataset i."""
    resid = 0.0 * data[i]
    resid[:] = data[i, :] - generate_dataset(parameters, i, x, model)
    return resid.flatten()


def objective(parameters, x, data, model):  # TODO fine to make x have many xs
    """Calculate total residual for fits to either a single dataset or
    multiple datasets contained in a 2D array, and fit to the model. Used by
    lmfit's minimization methods to calculate the fit. This runs thousands of
    times. If any optimization must be done, it should be here.

    Parameters
    ----------
        parameters: lmfit.Parameters
            OrderedDict of lmfit.Parameter objects that will be passed to
            the objective function to be dispatched to the model function.
        x: np.ndarray (1D)
            X-axis values that data was collected at.
        data: np.ndarray (multi-dimensional)
            Experimental data. Passed to objective to calculate residuals.
        model: function object
            The actual function used to calculate the fit.

    Returns
    -------
        1D np.ndarray of residual values for fit iterations calculated by
        subtracting experimental y-values from calculated y-values from the
        model function.
        """
    ndata = data.shape
    if len(data.shape) == 1:  # fit a single dataset
        print("\n\n\n\n\nYou should never see this\n\n\n\n\n")
        resid = 0.0 * data[:]
        resid[:] = data[:] - generate_dataset(parameters, 0, x, model)
        return resid.flatten()

    elif len(data.shape) == 2:  # fit multiple datasets
        resid = 0.0 * data[:]
        # make residual per data set
        for i in range(ndata[0]):
            resid[i, :] = data[i, :] - generate_dataset(parameters, i, x, model)
        # now flatten this to a 1D array, as minimize() needs
        return resid.flatten()


def fit(data, x, model, parameters, debug=False):
    """Fit the data [a 1-d array] to the model with the x axis [a 1-d array].

    Parameters
    ----------
        data: np.ndarray (multi-dimensional)
            Experimental data. Passed to objective to calculate residuals.
        x: np.ndarray (1D)
            X-axis values that data was collected at.
        model: string OR function object
            The model function that data should be fit to. Either the name of
            the function (or alias) defined in src.models.py, or the actual
            function itself.
        parameters: lmfit.Parameters
            OrderedDict of lmfit.Parameter objects that will be passed to
            the objective function to be dispatched to the model function.
        debug: boolean
            If true, fitting routine will print its values for parameters at
            each iteration.

    Returns
    -------
        result: lmfit.MinimizerResult
            The result of the fit. Contains the optimized values for all
            parameters, X^2, residuals, among other things.
        data: np.ndarray (multi-dimensional)
            The same unchanged data values that were passed into the function.
            Returned so that fits can be rerun, and plots can be created only
            from the returned values of this function.
        x: np.ndarray (1D)
            The same unchanged x-axis values that data was collected at.
        model: function object
            The actual function used to calculate the fit.

    """
    # find the function object with the given name from the models.
    # otherwise it should already be a function object
    if isinstance(model, str):
        model = models.get_models(model)

    # TODO if more than one model, join the models. If a buffer is not linked, take it out and fit separately. Ask Osman if this should be necessary.
    if debug:
        iter_cb = debug_fitting
    else:
        iter_cb = None

    result = minimize(objective, parameters, args=(x, data, model),
                      iter_cb=iter_cb)
    return result, data, x, model


def debug_fitting(params, nfev, out, *args, **kwargs):
    """Function to be called after each iteration of the minimization method
    used by lmfit. Should reveal information about how parameter values are
    changing after every iteration in the fitting routine. See
    lmfit.Minimizer.__residual for more information."""
    print("\nIteration {0}".format(nfev))
    for name, param in params.items():
        print("{0}\t{1}".format(name, param.value))


def generate_error_landscape(result, data, x, model, param_name, nsamples=15,
                             plus_minus=0.2):
    """Create a chi sq landscape of the result fit. Set the parameter for each
    dataset to a values between the true value plus or minus plus_minus, and
    redo the fit with the new fixed parameters. Should work for both
    linked(global) and unlinked parameters.

    Parameters
    ----------
        result: lmfit.MinimizerResult
            result of the fit
        data: np.ndarray (multi-dimensional)
            actual data values used to calc residuals in fit
        x: np.ndarray (1D)
            the x values that data was collected at
        model: funtion object
            the model used to calculate the fit
        param_name: string
            name of the parameter (w/o underscore and int) to be the x
            axis of X^2 landscape
        nsamples: int
            how many values of param to take X^2 at. Odd number will
            include true param value
        plus_minus: float
            percentage value representing how far from the true value of param
            you should vary in the X^2 analysis.

    Returns
    -------
        param_axis: np.ndarray (1D)
            Array of X values that X^2 was sampled at
        all_chis: np.ndarray (1D)
            Array of X^2 values for the fits with parameter values sampled
            at those specified in param_axis.
        """

    # perturb fitted values to not create false minima.
    # default_params = params.create_params_without_window(len(data), model)
    default_params = params.deep_copy(result.params)


    sample_spaces = []
    # loop through all the fitted data and generate parameter values to
    # sample X^2 at
    for i, y in enumerate(data):
        param_i = result.params["{0}_{1}".format(param_name, i)]

        val = param_i.value  # true value of the parameter

        # all the values of the parameter to take fits for
        sample_space = np.linspace(val - val*plus_minus,
                                   val + val*plus_minus,
                                   num=nsamples)
        sample_spaces.append(sample_space)

    all_chis = []
    # create fits for each parameter value
    for a in range(nsamples):
        # change all the values of the parameters
        for i, sample_space in enumerate(sample_spaces):
            param_i = default_params["{0}_{1}".format(param_name, i)]
            # X^2 analysis doesn't make sense if parameter can vary from what we set it.
            param_i.vary = False
            param_i.value = sample_space[a]

        # fit the data
        new_result, new_data, new_x, new_model = fit(data, x, model,
                                                     default_params)

        all_chis.append(new_result.redchi)
        report_result(new_result)

    # relative distance away from true fit X^2
    param_axis = np.linspace(-plus_minus, plus_minus, nsamples)

    # x and y values to plot
    return param_axis, all_chis


def report_result(result):
    """If there is a result, display it.

    Parameters
    ----------
        result: lmfit.MinimizerResult
            result of the fit. First thing returned by src.fit.fit

    Returns
    -------
        None
    """
    if isinstance(result, MinimizerResult):
        print(fit_report(result.params))
        if hasattr(result, "chisq"):
            print("[[Chi sq]]\n\s\s\s\s{0}".format(result.chisq))
        if hasattr(result, "redchi"):
            print("[[Chi sq (reduced)]]\n\t{0}".format(result.redchi))
    else:
        print("There was no result to the fit. "
              "<{0}> was returned instead".format(result))



