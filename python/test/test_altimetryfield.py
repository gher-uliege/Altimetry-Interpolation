import os
import numpy as np
import unittest
import divaaltimetry
import matplotlib.pyplot as plt
from mpl_toolkits.basemap import Basemap


class TestAltimetryField(unittest.TestCase):

    def setUp(self):
        self.avisofile = "../../data/dt_med_allsat_msla_h_20140221_20140829.nc"
        self.divafile = "../../data/data_20140717_20140806.nc"
        self.noncfile = "./nofile.nc"
        self.figdir = "./figures/"

        if not os.path.exists(self.figdir):
            os.makedirs(self.figdir)
        else:
            pass
            # clean figure directory
            #shutil

    def test_init(self):
        field = divaaltimetry.AltimetryField()
        self.assertTrue(field.lon is None)
        self.assertTrue(field.lat is None)
        self.assertTrue(field.time is None)
        self.assertTrue(field.field is None)
        self.assertTrue(field.error is None)

    def test_read_avisofile(self):
        field = divaaltimetry.AltimetryField().from_aviso_file(self.avisofile)
        self.assertEqual(field.time, 23427)
        self.assertEqual(len(field.lon), 344)
        self.assertEqual(len(field.lat), 128)
        self.assertEqual(field.lon[3], -5.5625)
        self.assertEqual(field.lon[-1], 36.9375)
        self.assertEqual(field.lat[6], 30.8125)
        self.assertEqual(field.lat[-4], 45.5625)
        self.assertEqual(field.field.shape, (128, 344))
        self.assertEqual(field.field.min(), -0.1373)
        self.assertAlmostEqual(field.field.mean(), 0.0177294155093)
        self.assertEqual(field.error.shape, (128, 344))
        self.assertEqual(field.error.min(), 0.0025)
        self.assertAlmostEqual(field.error.mean(), 0.00545835648148)

    def test_read_divafile(self):
        field = divaaltimetry.AltimetryField().from_diva2d_file(self.divafile)
        self.assertEqual(len(field.lon), 426)
        self.assertEqual(len(field.lat), 161)
        self.assertEqual(field.lon[10], -4.5)
        self.assertEqual(np.round(field.lon[-7]), 36.)
        self.assertEqual(np.floor(field.lat[26]), 32.)
        self.assertAlmostEqual(field.field.mean(), 0.01042658344120)
        self.assertAlmostEqual(field.error.mean(), 0.0349892154988)
        # Need to solve issue with round and floor

    def test_plot(self):
        field = divaaltimetry.AltimetryField().from_aviso_file(self.avisofile)
        field.add_to_plot(os.path.join(self.figdir, 'test.png'))
        self.assertTrue(os.path.exists(os.path.join(self.figdir, 'test.png')))

    def test_read_nonexisting_file(self):
        field = divaaltimetry.AltimetryField().from_aviso_file(self.noncfile)
        self.assertTrue(field == None)


if __name__ == '__main__':
    unittest.main()