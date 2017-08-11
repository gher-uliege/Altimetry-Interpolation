import os
import time
import numpy as np
import unittest
import pydivand


class TestPydivandParameters(unittest.TestCase):

    def setUp(self):
        timestr = time.strftime("%Y%m%d-%H%M%S")
        self.filename = "./param{0}.txt".format(timestr)
        self.origins = (-7., 30., 23520)
        self.ends = (40.1, 48.54, 23525)
        self.steps = (0.125, 0.125, 1.)

    def test_init_empty(self):
        parameters = pydivand.Parameters()
        self.assertTrue(parameters.origins is None)
        self.assertTrue(parameters.ends is None)
        self.assertTrue(parameters.steps is None)
        self.assertEqual(parameters.ndim, 0)

    def test_init(self):
        parameters = pydivand.Parameters(self.origins, self.ends, self.steps)

        self.assertEqual(parameters.origins[0], -7.)
        self.assertEqual(parameters.origins[-1], 23520)
        self.assertEqual(parameters.ends[1], 48.54)
        self.assertEqual(parameters.steps[0], 0.125)

    def test_get_domain_size(self):
        parameters = pydivand.Parameters(self.origins, self.ends, self.steps)

        parameters.get_domain_size()
        self.assertEqual(np.floor(parameters.npoints[0]), 376)
        self.assertEqual(np.floor(parameters.npoints[1]), 148)
        self.assertEqual(np.floor(parameters.npoints[2]), 5)

    def test_write_file(self):
        parameters = pydivand.Parameters(self.origins, self.ends, self.steps)
        parameters.to_file(self.filename)

        self.assertTrue(os.path.exists(self.filename))


    def tearDown(self):
        if os.path.exists(self.filename):
            # os.remove(self.filename)
            pass

if __name__ == '__main__':
    unittest.main()