from src import models
import numpy as np
import matplotlib.pyplot as plt
import lmfit


def fit(data, model, x, params={}):
    """Fit the data [a 1-d array] to the model with the x axis [a 1-d array]."""

    for m in models.list_models():  # get the model function from the string name
        if model in m[0]:   # the function name
            model = m[1]  # the function object
            break

    m = lmfit.models.Model(model)
    result = m.fit(data, x=x, **params)
    print(result.fit_report())
    result.plot()
    plt.show()

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
