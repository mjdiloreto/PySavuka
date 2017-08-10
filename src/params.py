"""This module contains the GUI application that prompts the user to specify
their parameters that will be used to fit whatever data they wish to the
model specified."""


from src.utils import eval_string

import inspect
import sys

from lmfit import Model, Parameters, Parameter

from PyQt5.QtWidgets import (QMainWindow, QApplication, QWidget, QAction,
    QTableWidget, QTableWidgetItem, QVBoxLayout, QPushButton, QDesktopWidget)
from PyQt5.QtGui import QIcon
from PyQt5.QtCore import pyqtSlot


class App(QWidget):
    def __init__(self, num_bufs, params):
        super().__init__()

        # The number of buffers that should be fit to the model. Determines
        # how many sets of parameters are needed.
        self.num_bufs = num_bufs

        # Takes in and modifies the default Params item given by Model.make_params()
        self.default_params = params

        self.parameters = Parameters()

        self.title = 'Enter your Params'
        self.left = 0
        self.top = 0
        self.width = 1280
        self.height = 720
        self.initUI()

    def initUI(self):
        self.setWindowTitle(self.title)
        self.setGeometry(self.left, self.top, self.width, self.height)

        self.createTable()
        self.createButton()

        # Add box layout, add table to box layout and add box layout to widget
        self.layout = QVBoxLayout()
        self.layout.addWidget(self.tableWidget)
        self.layout.addWidget(self.button)
        self.setLayout(self.layout)

        self.center()

        # Show widget
        self.show()

    def createButton(self):
        self.button = QPushButton('Update Params', self)
        self.button.setToolTip('Update your parameters with data currently '
                               'entered in the spreadsheet.')
        self.button.move(100, 70)
        self.button.clicked.connect(self.on_click)

    def createTable(self):
        """Use the default parameters to set up a table that the user can then
        change the values of."""

        # Create table
        self.tableWidget = QTableWidget()

        column_headers = [
            'name', 'value', 'vary', 'min', 'max', 'expr',
            'brute_step', 'user_data', 'shared with buffer'
        ]

        header_tooltips = [
                           'name of the parameter',
                           'buffer number that parameter should be tied to (itself by default, i.e not tied to another parameter',
                           'Starting value of the parameter',
                           'Whether the Parameter is varied during a fit (default is True)',
                           'Lower bound of the variable parameter',
                           'Upper bound of the variable parameter',
                           'Constraint expression to describe variable parameter',
                           'Step size for grid points in the `brute` method',
                           'User-definable extra attribute used for a Parameter'
        ]
        # leave an empty column where buffer numbers should go.
        column_count = len(column_headers) + 1
        # There should be a row for each parameter for each buffer, and one for headers
        row_count = len(self.default_params) * self.num_bufs + 1

        current_row = 0

        self.tableWidget.setRowCount(row_count)
        self.tableWidget.setColumnCount(column_count)

        def set_cell_not_editable(cell):
            flags = cell.flags()
            # Bitwise masking of IsEditable flag. Make it NOT editable
            flags ^= 2
            cell.setFlags(flags)

        # initialize column headers. Start in second column
        for column in range(len(column_headers)):
            cell = QTableWidgetItem("{0}".format(column_headers[column]))
            set_cell_not_editable(cell)
            cell.setToolTip("{0}".format(header_tooltips[column]))
            self.tableWidget.setItem(0, column + 1, cell)

        # Move on to the rows containing parameter values.
        current_row += 1

        # create rows for each parameter associated with a dataset.
        for buf in range(self.num_bufs):
            buffer_cell = QTableWidgetItem("Buffer {0}".format(buf))
            set_cell_not_editable(buffer_cell)
            self.tableWidget.setItem(current_row, 0, buffer_cell)
            
            for name, param in self.default_params.items():
                # make a GUI element for each parameter attribute.
                cells = [
                    QTableWidgetItem("{0}".format(name)),
                    QTableWidgetItem("{0}".format(param.value)),
                    QTableWidgetItem("{0}".format(param.vary)),
                    QTableWidgetItem("{0}".format(param.min)),
                    QTableWidgetItem("{0}".format(param.max)),
                    QTableWidgetItem("{0}".format(param.expr)),
                    QTableWidgetItem("{0}".format(param.brute_step)),
                    QTableWidgetItem("{0}".format(param.user_data)),
                    QTableWidgetItem("{0}".format(buf))
                    ]

                # name of the parameter should not be changed.
                set_cell_not_editable(cells[0])

                # place the cells in the proper place in the table
                for idx, cell in enumerate(cells):
                    self.tableWidget.setItem(current_row, idx+1, cell)

                # each row represents one parameter.
                current_row += 1

        self.tableWidget.move(0, 0)

    @pyqtSlot()
    def on_click(self):
        self.createParams()

    def center(self):
        frameGm = self.frameGeometry()
        centerPoint = QDesktopWidget().availableGeometry().center()
        frameGm.moveCenter(centerPoint)
        self.move(frameGm.topLeft())

    def createParams(self):
        """From the data in self.tableWidget, parse out parameters and return
        a Parameters object that lmfit can use to fit data to the model."""
        for x in range(self.tableWidget.rowCount()):
            # name is in the second column. append the buffer number to it
            # e.g. amplitude in row 4 with 3 params will be 'amplitude_1'
            try:
                # What number buffer are we on?
                current_buffer = int(x / len(self.default_params))

                # create a unique name for each parameter, e.g. 'amp_1'
                param_name = self.tableWidget.item(x+1, 1).text()
                full_name = "{0}_{1}".format(param_name, current_buffer)

                # the dictionary of options passed when creating a Parameter object.
                parameter_opts = {'name': full_name}
                # traverse the row picking out parameter options
                for y in range(self.tableWidget.columnCount()-2):
                    # column headers are option names
                    opt_name = self.tableWidget.item(0, y+2).text()
                    # option values are in the rows.
                    opt_val = eval_string(self.tableWidget.item(x+1, y+2).text())

                    # correct erroneous inputs
                    if opt_name == 'shared with buffer':
                        if opt_val != current_buffer:  # it is shared with another buffer
                            # lmfit will reassign a parameter if it's expr is
                            # set to another parameter's name
                            parameter_opts['expr'] = "{0}_{1}".format(param_name, opt_val)
                    elif opt_name == 'max' or opt_name == 'min':
                        if opt_val == 'inf':
                            opt_val = None  # defaults to infinity
                        elif opt_val == '-inf':
                            opt_val = None
                        parameter_opts[opt_name] = opt_val
                    else:
                        parameter_opts[opt_name] = opt_val

                self.parameters.add(Parameter(**parameter_opts))

            except AttributeError:  # uninitialized cells
                pass

        return self.parameters


def create_default_params(model):
    """Create a set of parameters for the given model."""

    m = Model(model)  # leverage lmfit's builtin Model class
    pars = m.make_params()

    return pars


def main(num_bufs, params):
    app = QApplication(sys.argv)
    ex = App(num_bufs, params)
    app.exec()
    return ex.createParams()
