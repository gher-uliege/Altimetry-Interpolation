import os
import numpy as np
import matplotlib.pyplot as plt
import netCDF4
import logging
import datetime
import glob

class Track(object):
    """
    Object that represent an altimeter track: positions, time and altimetry measurements
    (ADT, MDT, SLA, ...).
    """
    def __init__(self, filename):
        """
        Read the values from the selected file name
        """
        self.filename = filename
        
        if os.path.exists(self.filename):
            with netCDF4.Dataset(self.filename, 'r') as nc:
                self.lon = nc.variables['longitude'][:]
                self.lat = nc.variables['latitude'][:]
                self.time = nc.variables['time'][:]
                self.adt = nc.variables['ADT'][:]
                self.npoints = len(self.lon)
            # Change longitude so that they lie between -180 and 180
            self.lon[self.lon > 180.] -= 360.
            
        else:
            logging.warning("File {0} doesn't exist".format(self.filename))
            self.lon = []
            self.lat = []
            self.time = []
            self.adt = []
            self.npoints = 0
            
    def compute_time_weights(self, timescale, timemid):
        """
        Compute the data weights (4th column in Diva2D data files) 
        using the time difference between the actual measurement and 
        the mean time of the considered period
        Parameters:
        -----------
        timescale: float indicating the temporal scale (in days ; has to be 
        consistent with the units of the time in the AVISO files).
        timemid: float indicating the reference time (in days since 
        January 1st, 1950 to ensure consistency with AVISO files).
        """

        if len(self.time):
            timeweight = np.exp(- abs(self.time - timemid) / timescale)
        else:
            timeweight = []

        return timeweight

    def add_to_plot(self, **kwargs):
        """
        Add the data points as a scatter plot
        """
        plt.scatter(self.lon, self.lat, c=self.adt, **kwargs)
        
    def add_to_map(self, m, **kwargs):
        """
        Add the data points as a scatter plot to an existing map
        """
        m.scatter(self.lon, self.lat, c=self.adt, latlon=True, **kwargs)
        
    def write_textfile(self, filename):
        if not os.path.exists(filename):
            logging.info("Creating new file {0}".format(filename))
            
        with open(filename, 'a') as f:
            for lon, lat, time, adt in zip(self.lon, self.lat, self.time, self.adt):
                f.write(' '.join((str(lon), str(lat), str(time), str(adt), '\n')))
                
    def write_divafile(self, filename, timescale, timemid):
        """
        Write a Diva2D file: lon | lat | field | weight
        where the weights are computed using the time difference between the actual measurement and 
        the mean time of the considered period
        """
        timeweight = self.compute_time_weights(timescale, timemid)
        # self.timeweight = np.exp( - abs(self.time - timemid) / timescale)
        
        if not os.path.exists(filename):
            logging.info("Creating new file {0}".format(filename))
            
        with open(filename, 'a') as f:
            for lon, lat, adt, weight in zip(self.lon, self.lat, self.adt, timeweight):
                f.write(' '.join((str(lon), str(lat), str(adt), str(weight), '\n')))


def prepare_datestrings(year, month, day, interval):
    """
    Create a string that will be used as a suffix in the file name
    And another one used on the figure title
    """
    datemid = datetime.datetime(year, month, day)
    datestart = datemid - datetime.timedelta(interval)
    dateend = datemid + datetime.timedelta(interval)
    logging.debug("Start date: {0}".format(datestart))
    logging.debug("End   date: {0}".format(dateend))

    # Create string that will be used for filename
    fignamesuffix = datestart.strftime("%Y%m%d") + '_' + dateend.strftime("%Y%m%d")
    figtitledate = datestart.strftime("%Y-%m-%d") + '$-$' + dateend.strftime("%Y-%m-%d")
    return fignamesuffix, figtitledate


def make_filelist(databasedir, missionlist, year, month, day, interval):
    """
    Create a list of files from the selected directory and missions
    with dates that are inside the interval determined by year, month, day and interval
    Parameters:
    -----------
    databasedir: main directory containing the data files
    missionlist: list or tuple of strings for the sub-directories, one per mission
    year, month, day: integers that sets the central day of the period of interest
    interval: integer indicating the number of days before and after the central day of the period
    """
    datemid = datetime.datetime(year, month, day)
    datestart = datemid - datetime.timedelta(interval)
    dateend = datemid + datetime.timedelta(interval)
    logging.debug("Start date: {0}".format(datestart))
    logging.debug("End   date: {0}".format(dateend))

    # Create list of days in format YYYYMMDD
    datelist = []
    nfiles = 0
    dd = datestart
    while dd != dateend:
        datelist.append(dd.strftime("%Y%m%d"))
        dd += datetime.timedelta(1)

    # Create the file list
    filelist = []
    for mission in missionlist:
        logging.info("Working on file from mission {0}".format(mission))
        datadir = os.path.join(databasedir, mission)
        for dates in datelist:
            logging.debug(dates)
            fname = "dt_med_{0}_adt_vfec_{1}_{2}.nc".format(mission, dates, '*')
            flist = glob.glob(os.path.join(datadir, "".join((dates[:4], '/', fname))))

            # Check if at least one file is found
            # with H2 mission some files are missing
            if len(flist) != 0:
                filelist.append(flist[0])
                nfiles += 1
    logging.info("Found {0} files for the selected period and missions".format(nfiles))
    return filelist
