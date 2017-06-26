#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
test_PySavuka
----------------------------------

Tests for `PySavuka` module.
"""

import unittest

import numpy as np
import os

import commandline
import savuka
import parse_funcs
import plot_funcs
import utils


class TestPysavuka(unittest.TestCase):

    def setUp(self):
        self.location = os.path.abspath(os.path.join(__file__, "..\.."))
        self.xyexample1 = os.path.join(self.location, r'docs\xyexample1.txt')
        self.xyexample2 = os.path.join(self.location, r'docs\xyexample2.txt')

    def test_parsefuncs(self):

        # test that the function outputs the correct values for x and y
        xs, ys = parse_funcs.parse(self.xyexample1, "example")
        self.assertEqual(xs[0], 0.0)
        self.assertEqual(ys[0], 0.9811704)
        self.assertEqual(xs[2], 0.3265306)
        self.assertEqual(ys[2], 1.005850)

        # Checks that testing an unsupported format raises an error
        with self.assertRaises(NameError):
            parse_funcs.parse(self.xyexample1, "notexample")

    def test_savuka_single_parse(self):
        s1 = savuka.Savuka()
        np.testing.assert_array_equal(s1.data, np.array([]))

        s1.read(self.xyexample1, 'example')

        # Test that the state changed
        with self.assertRaises(AssertionError):
            np.testing.assert_array_equal(s1.data, np.array([]))

        # Test that the data has the correct dimensionality
        self.assertEqual(s1.data.shape, (1, 3, 50))

        self.assertEqual(s1.data[0].shape, (3, 50))

        self.assertEqual(s1.data[0, 0].shape, (50,))

        # What is the associated z value?
        self.assertEqual(s1.data[0, 0, 0], 0.0)

        # what is the first x value?
        self.assertEqual(s1.data[0, 1, 0], 0.0)

        # what is the second x value?
        self.assertAlmostEqual(s1.data[0, 1, 1], 0.1632653)

        # what is the last x value?
        self.assertEqual(s1.data[0, 1, -1], 8.0)

        # what is the first y value?
        self.assertAlmostEqual(s1.data[0, 2, 0], 0.9811704)

        # what is the second y value?
        self.assertAlmostEqual(s1.data[0, 2, 1], 0.9961520)

        # what is the last y value?
        self.assertAlmostEqual(s1.data[0, 2, -1], 9.173535)

    def test_savuka_double_parse(self):
        s1 = savuka.Savuka()
        np.testing.assert_array_equal(s1.data, np.array([]))

        s1.read(self.xyexample1, 'example')
        s1.read(self.xyexample2, 'example')

        # Test that the data has the correct dimensionality
        self.assertEqual(s1.data.shape, (2, 3, 50))

        self.assertEqual(s1.data[0].shape, (3, 50))

        self.assertEqual(s1.data[1].shape, (3, 50))

        self.assertEqual(s1.data[0, 0].shape, (50,))

        # What is the associated z value of example 1?
        self.assertEqual(s1.data[0, 0, 0], 0.0)

        # what is the first x value of example 1?
        self.assertEqual(s1.data[0, 1, 0], 0.0)

        # what is the second x value of example 1?
        self.assertAlmostEqual(s1.data[0, 1, 1], 0.1632653)

        # what is the last x value of example 1?
        self.assertEqual(s1.data[0, 1, -1], 8.0)

        # what is the first y value of example 1?
        self.assertAlmostEqual(s1.data[0, 2, 0], 0.9811704)

        # what is the second y value of example 1?
        self.assertAlmostEqual(s1.data[0, 2, 1], 0.9961520)

        # what is the last y value of example 1?
        self.assertAlmostEqual(s1.data[0, 2, -1], 9.173535)

        # What is the associated z value of example 2?
        self.assertEqual(s1.data[1, 0, 0], 0.0)

        # what is the first x value of example 2?
        self.assertEqual(s1.data[1, 1, 0], 0.01)

        # what is the second x value of example 2?
        self.assertAlmostEqual(s1.data[1, 1, 1], 0.1232653)

        # what is the last x value of example 2?
        self.assertEqual(s1.data[1, 1, -1], 8.0)

        # what is the first y value of example 2?
        self.assertAlmostEqual(s1.data[1, 2, 0], 0.5811704)

        # what is the second y value of example 2?
        self.assertAlmostEqual(s1.data[1, 2, 1], 0.6961520)

        # what is the last y value of example 2?
        self.assertAlmostEqual(s1.data[1, 2, -1], 9.173535)

    def test_savuka_attributes(self):
        s1 = savuka.Savuka()

        self.assertEqual(len(s1.attributes), 0)

        s1.read(self.xyexample1, "example")

        s1.set_name(0, "xyexample1")

        self.assertEqual(len(s1.attributes), 1)

        self.assertEqual(s1.attributes["xyexample1"], 0)

    def debug_plot_funcs(self):
        import matplotlib.pyplot as plt

        s = savuka.Savuka()
        s.read(self.xyexample1, 'example')
        s.read(self.xyexample1, 'example')
        s.read(self.xyexample1, 'example')
        s.read(self.xyexample1, 'example')

        # plot_buffers(s, "(0, 21, 1)")
        #plot_funcs.plot_superimposed(s, [3, (0, 2)])
        plot_funcs.plot_all(s)
        plt.show()

    def debug_savuka(self):
        s = savuka.Savuka()
        s.read(self.xyexample1, 'example')
        s.read(self.xyexample1, 'example')
        s.read(self.xyexample1, 'example')
        s.read(self.xyexample1, 'example')

        s.shift_buffer(1, 100)
        s.scale_buffer(2, 5)
        s.pow_buffer(3, 2)
        s.plot_superimposed([0,1,2,3,])

    def debug_parse_funcs(self):
        s = savuka.Savuka()
        s.read(self.xyexample1, 'example')

    def debug_utils(self):
        print(utils.parseline('a b -s c r (1, 3)', 'arg'))

    def debug_commandline(self):
        commandline.main()

    def debug_check_input(self):
        c = commandline.CommandLine()
        c.check(None, a=None)

    def tearDown(self):
        pass

if __name__ == '__main__':
    '''suite = unittest.TestLoader().loadTestsFromTestCase(TestPysavuka)
    unittest.TextTestRunner(verbosity=2).run(suite)'''
    t = TestPysavuka()
    t.setUp()
    # t.debug_utils()
    t.debug_savuka()
    # t.debug_plot_funcs()
    # t.debug_check_input()
    # t.debug_parse_funcs()