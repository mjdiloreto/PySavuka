#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
test_PySavuka
----------------------------------

Tests for `PySavuka` module.
"""

import unittest
import os

from src import commandline
from src import savuka
from src import parse_funcs
from src import plot_funcs
from src import utils
from src import buffer


class TestPysavuka(unittest.TestCase):

    def setUp(self):
        self.location = os.path.abspath(os.path.join(__file__, "..\.."))
        self.xyexample1 = os.path.join(self.location, r'docs\xyexample1.txt')
        self.xyexample2 = os.path.join(self.location, r'docs\xyexample2.txt')

    def test_parsefuncs(self):

        # test that the function outputs the correct values for x and y
        b = parse_funcs.parse(self.xyexample1, "example")
        self.assertEqual(b['dim1'].data[0], 0.0)
        self.assertEqual(b['dim2'].data[0], 0.9811704)
        self.assertEqual(b['dim1'].data[2], 0.3265306)
        self.assertEqual(b['dim2'].data[2], 1.005850)
        self.assertEqual(b['dim3'].data, 1.0)

        # Checks that testing an unsupported format raises an error
        with self.assertRaises(NameError):
            parse_funcs.parse(self.xyexample1, "notexample")

    def test_savuka_single_parse(self):
        s1 = savuka.Savuka()
        self.assertEqual(len(s1), 0)

        s1.read(self.xyexample1, 'example')
        # Test that the data has the correct dimensionality
        self.assertEqual(len(s1), 1)

        s1.read(self.xyexample2, 'example')
        self.assertEqual(len(s1), 2)

    def test_savuka_attributes(self):
        s1 = savuka.Savuka()

        self.assertEqual(len(s1.attributes), 0)

        s1.read(self.xyexample1, "example")

        s1.set_name(0, "xyexample1")

        self.assertEqual(len(s1.attributes), 1)

        self.assertEqual(s1.attributes["xyexample1"], 0)

    def test_buffer(self):
        b = buffer.Buffer()
        self.assertEqual(b, {})

        a = parse_funcs.parse(self.xyexample1, 'example')
        b1 = buffer.Buffer(a)
        b2 = buffer.Buffer(b1)

        self.assertEqual(b1, b2)
        b3 = buffer.Buffer(b1, b2)
        self.assertEqual(b1, b3)

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

    def test_savuka(self):
        s = savuka.Savuka()
        s.read(self.xyexample1, 'example')
        s.read(self.xyexample1, 'example')
        s.read(self.xyexample1, 'example')
        s.read(self.xyexample1, 'example')

        s.shift_buffer(1, 100)
        s.scale_buffer(2, 5)
        s.pow_buffer(3, 2)
        # s.plot_superimposed([0,1,2,3,])
        print(s)

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
    suite = unittest.TestLoader().loadTestsFromTestCase(TestPysavuka)
    unittest.TextTestRunner(verbosity=2).run(suite)
    # t = TestPysavuka()
    # t.setUp()
    # t.debug_utils()
    # t.debug_savuka()
    # t.debug_plot_funcs()
    # t.debug_check_input()
    # t.debug_parse_funcs()
    # t.test_dimension()
    # t.test_parsefuncs()