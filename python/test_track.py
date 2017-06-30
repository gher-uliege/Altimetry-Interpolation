import unittest
import divaaltimetry
import numpy as np

class TestTrackMethods(unittest.TestCase):

    def setUp(self):
        self.ncfile = "../data/dt_med_al_adt_vfec_20140101_20140829.nc"
        self.noncfile = "./nofile.nc"
        self.timescale = 5.
        self.timemid = 23520.

    def test_init(self):
        track = divaaltimetry.Track(self.ncfile)
        self.assertAlmostEqual(track.time[6], 23376.1830808189)
        self.assertEquals(len(track.lon), 182)
        self.assertAlmostEqual(track.adt[-1], 197 * 0.001)
        self.assertTrue(np.max(np.array(track.lon)) <= 180.)

    def test_init_nofile(self):
        """
        Try with a non-existing file
        """
        track = divaaltimetry.Track(self.noncfile)
        self.assertEqual(track.lon, [])
        self.assertEqual(track.lat, [])
        self.assertEqual(track.time, [])
        self.assertLogs(logger=None, level=Warning)

    def test_compute_time_weights(self):
        track = divaaltimetry.Track(self.noncfile)
        weight = track.compute_time_weights(self.timescale, self.timemid)



if __name__ == '__main__':
    unittest.main()