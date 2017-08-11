import unittest
import divaaltimetry
import numpy as np


class TestTrackMethods(unittest.TestCase):

    def setUp(self):
        self.ncfile = "./data/dt_med_al_adt_vfec_20140101_20140829.nc"
        self.noncfile = "./nofile.nc"
        self.cmemsfile = "./data/dt_med_al_phy_vxxc_l3_20140605_20170110.nc"
        self.timescale = 5.
        self.timemid = 23376.69

    def test_read_aviso_adt(self):
        """
        Try to read a data file obtained from AVISO
        """
        track = divaaltimetry.Track()
        track.read_from_aviso_adt(self.ncfile)
        self.assertAlmostEqual(track.time[6], 23376.1830808189)
        self.assertEquals(len(track.lon), 182)
        self.assertAlmostEqual(track.field[-1], 197 * 0.001)
        self.assertTrue(np.max(np.array(track.lon)) <= 180.)

    def test_read_cmems_sla(self):
        """
        Try to read a data file from CMEMS
        """
        track = divaaltimetry.Track()
        track.read_from_cmems_sla(self.cmemsfile)
        self.assertEqual(len(track.lon), 329)
        self.assertEqual(len(track.lat), 329)
        self.assertEqual(track.field.max(), 0.078)
        self.assertEqual(track.lon[300], 18.972246)
        self.assertAlmostEqual(track.lat[123], 40.252148999)
        self.assertAlmostEqual(track.time[-1], 23531.783404077)
        self.assertAlmostEqual(track.time[6], 23531.2030643314)
        self.assertTrue(np.max(np.array(track.lon)) <= 180.)

    def test_read_nofile(self):
        """
        Try to read a file that does not exist
        """
        track = divaaltimetry.Track()
        track.read_from_aviso_adt(self.noncfile)
        self.assertTrue(track.lon is None)
        self.assertTrue(track.lat is None)
        self.assertTrue(track.time is None)
        self.assertTrue(track.field is None)
        self.assertLogs(logger=None, level=Warning)

    def test_compute_time_weights_aviso(self):
        track = divaaltimetry.Track()
        track.read_from_aviso_adt(self.ncfile)
        weight = track.compute_time_weights(self.timescale, self.timemid)
        self.assertEqual(len(weight), 182)
        self.assertAlmostEqual(weight.max(), 0.9992989086)
        self.assertAlmostEqual(weight[45], 0.903758336991)



if __name__ == '__main__':
    unittest.main()