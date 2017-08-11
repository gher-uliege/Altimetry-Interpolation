import os
import numpy as np
import matplotlib.pyplot as plt
import netCDF4
import logging
import datetime
import glob

import warnings
import matplotlib.cbook
warnings.filterwarnings("ignore", category=matplotlib.cbook.mplDeprecation)


class Track(object):
    """
    Object that represent an altimeter track: positions, time and altimetry measurements
    (ADT, MDT, SLA, ...).
    """
    def __init__(self, lon=None, lat=None, time=None, field=None):
        """
        Initialise the track object
        """
        self.lon = lon
        self.lat = lat
        self.time = time
        self.field = field

    def read_from_aviso_adt(self, filename):
        """
        Read the values from the selected netCDF name,
        obtained from AVISO FTP
        """
        
        try:
            with netCDF4.Dataset(filename, 'r') as nc:
                self.lon = nc.variables['longitude'][:]
                self.lat = nc.variables['latitude'][:]
                self.time = nc.variables['time'][:]
                self.field = nc.variables['ADT'][:]
            # Change longitude so that they lie between -180 and 180
            self.lon[self.lon > 180.] -= 360.
        except OSError:
            logging.warning("File {0} doesn't exist".format(filename))

    def read_from_cmems_sla(self, filename):
        """
        Read the values from the selected netCDF name,
        obtained from CMEMS FTP and containing SLA measurements
        """

        try:
            with netCDF4.Dataset(filename, 'r') as nc:
                self.lon = nc.variables['longitude'][:]
                self.lat = nc.variables['latitude'][:]
                self.time = nc.variables['time'][:]
                self.field = nc.variables['sla_unfiltered'][:]
            # Change longitude so that they lie between -180 and 180
            self.lon[self.lon > 180.] -= 360.
        except OSError:
            logging.warning("File {0} doesn't exist".format(filename))

    def compute_time_weights(self, timescale, timemid):
        """
        Compute the data weights (4th column in Diva2D data files) 
        using the time difference between the actual measurement and 
        the mean time of the considered period
        Parameters:
        -----------
        timescale: float indicating the temporal scale (in days ; has to be 
        consistent with the units of the time in the AVISO files).
        ex: 10
        timemid: float indicating the reference time (in days since 
        January 1st, 1950 to ensure consistency with AVISO files).
        ex: 23376
        """

        if self.time is not None:
            timeweight = np.exp(- abs(self.time - timemid) / timescale)
        else:
            timeweight = None

        return timeweight

    def add_to_plot(self, **kwargs):
        """
        Add the data points as a scatter plot
        """
        plt.scatter(self.lon, self.lat, c=self.field, **kwargs)
        
    def add_to_map(self, m, **kwargs):
        """
        Add the data points as a scatter plot to an existing map
        """
        m.scatter(self.lon, self.lat, c=self.field, latlon=True, **kwargs)
        
    def write_divandfile(self, filename):
        """
        Write the coordinates and measurements to an ascii file

        If the file doesnt't exist, it is created
        :param filename: path to the file
        :type filename: str
        """
        if not os.path.exists(filename):
            logging.info("Creating new file {0}".format(filename))
            
        with open(filename, 'a') as f:
            for lon, lat, time, field in zip(self.lon, self.lat, self.time, self.field):
                f.write(' '.join((str(lon), str(lat), str(time), str(field), '\n')))
                
    def write_divafile(self, filename, timescale, timemid):
        """
        Write a Diva2D file: lon | lat | field | weight
        where the weights are computed using the time difference between the actual measurement and 
        the mean time of the considered period
        :param filename: path to the file
        :type filename: str
        :param timescale: temporal scale for the weight smoothing
        :type timescale: float
        :param timemid: central time of the considered period
        :type timemid: float (in days since January 1st, 1950)
        """
        timeweight = self.compute_time_weights(timescale, timemid)
        # self.timeweight = np.exp( - abs(self.time - timemid) / timescale)
        
        if not os.path.exists(filename):
            logging.info("Creating new file {0}".format(filename))
            
        with open(filename, 'a') as f:
            for lon, lat, field, weight in zip(self.lon, self.lat, self.field, timeweight):
                f.write(' '.join((str(lon), str(lat), str(field), str(weight), '\n')))


class AltimetryField(object):
    """
    Class to represent a 2D gridded field of altimetry

    Variable can be SLA, ADT, MDT. An error field can also be available.
    """

    def __init__(self, lon=None, lat=None, time=None, field=None, error=None, filetime=None):
        self.lon = lon
        self.lat = lat
        self.time = time
        self.field = field
        self.error = error
        self.filetime = filetime

    def add_to_plot_simple(self, **kwargs):

        pcm = plt.pcolormesh(self.lon, self.lat, self.field, **kwargs)
        return pcm

    def add_to_plot(self, figname=None, figtitle=None, m=None,
                    meridians=None, parallels=None,
                    vmin=-0.2, vmax=0.2,
                    cmap=plt.cm.RdYlBu_r,
                    **kwargs):
        """
        Create pcolor plot of the Sea Level Anomaly field
        and generate a figure
        """
        llon, llat = np.meshgrid(self.lon, self.lat)
        plt.figure(figsize=(6, 6))
        ax = plt.subplot(111)

        if m:
            m.ax = ax
            pcm = m.pcolormesh(llon, llat, self.field, latlon=True,
                               cmap=cmap, vmin=vmin, vmax=vmax, zorder=3, **kwargs)

            # Add lines, coastline etc
            m.drawmeridians(meridians, labels=[0, 0, 0, 1], linewidth=.2, zorder=2)
            m.drawparallels(parallels, labels=[1, 0, 0, 0], linewidth=.2, zorder=2)
            m.drawcoastlines(linewidth=.2, zorder=4)

        else:
            pcm = plt.pcolormesh(llon, llat, self.field, vmin=vmin, vmax=vmax, **kwargs)

        cbar = plt.colorbar(pcm, shrink=.5, extend='both')
        cbar.set_label("m", fontsize=12, rotation=0)
        if figtitle is not None:
            plt.title(figtitle)
        if figname is not None:
            plt.savefig(figname, dpi=300)
        # plt.show()
        plt.close()

    def from_aviso_file(self, filename):
        """
        Read gridded altimetry field from a netCDF file
        :param filename: path to the file
        :return: str
        """

        if os.path.exists(filename):
            with netCDF4.Dataset(filename, 'r') as nc:
                self.lon = nc.variables['lon'][:]
                self.lat = nc.variables['lat'][:]
                self.time = nc.variables['time'][:]
                self.field = nc.variables['sla'][:].squeeze()
                self.error = nc.variables['err'][:].squeeze()
                # Change longitude so that they lie between -180 and 180
                self.lon[self.lon > 180.] -= 360.
                timeunits = nc.variables['time'].units
                self.filetime = netCDF4.num2date(self.time, timeunits)

                return self
        else:
            logging.warning("File {0} does not exist".format(filename))

    def from_diva2d_file(self, filename):
        """
        Read gridded altimetry field from a netCDF file
        as generated by Diva2D
        :param filename: path to the file
        :return: str
        """

        if os.path.exists(filename):
            with netCDF4.Dataset(filename, 'r') as nc:
                self.lon = nc.variables['x'][:]
                self.lat = nc.variables['y'][:]
                self.field = nc.variables['analyzed_field'][:]
                self.error = nc.variables['error_field'][:]
                return self
        else:
            logging.warning("File {0} does not exist".format(filename))

    def gradients(self, figname=None, figtitle=None, m=None,
                  meridians=None, parallels=None,
                  vmin=-0.2, vmax=0.2,
                  cmap=plt.cm.RdYlBu_r,
                  **kwargs):
        """
        Compute gradients and plot them
        """
        gx, gy = np.gradient(self.field)

        llon, llat = np.meshgrid(self.lon, self.lat)
        fig = plt.figure(figsize=(6, 6))

        if m:
            ax = plt.subplot(211)
            plt.title(figtitle)
            m.ax = ax
            m.pcolormesh(llon, llat, gx, latlon=True,
                         cmap=cmap, vmin=vmin, vmax=vmax, zorder=3, **kwargs)

            # Add lines, coastline etc
            m.drawmeridians(meridians, labels=[0, 0, 0, 0], linewidth=.2, zorder=2)
            m.drawparallels(parallels, labels=[1, 0, 0, 0], linewidth=.2, zorder=2)
            m.drawcoastlines(linewidth=.2, zorder=4)

            ax = plt.subplot(212)
            m.ax = ax
            pcm = m.pcolormesh(llon, llat, gy,
                               latlon=True, cmap=cmap, vmin=vmin, vmax=vmax, zorder=3, **kwargs)
            # Add lines, coastline etc
            m.drawmeridians(meridians, labels=[0, 0, 0, 1], linewidth=.2, zorder=2)
            m.drawparallels(parallels, labels=[1, 0, 0, 0], linewidth=.2, zorder=2)
            m.drawcoastlines(linewidth=.2, zorder=4)

            fig.subplots_adjust(right=0.85)
            cbar_ax = fig.add_axes([0.875, 0.15, 0.05, 0.7])
            plt.colorbar(pcm, cax=cbar_ax, extend="both")

        else:
            ax = plt.subplot(211)
            plt.title(figtitle)
            plt.pcolormesh(llon, llat, gx, vmin=vmin, vmax=vmax, **kwargs)
            ax.set_xticks([])
            plt.subplot(212)
            pcm = plt.pcolormesh(llon, llat, gx, vmin=vmin, vmax=vmax, **kwargs)
            plt.colorbar(pcm)

        if figname is not None:
            plt.savefig(figname)
            plt.close()


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


def make_filelist(databasedir, missionlist, missiondirlist, year, month, day, interval):
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
    for mission, missiondir in zip(missionlist, missiondirlist):
        logging.info("Working on file from mission {0}".format(missiondir))
        datadir = os.path.join(databasedir, missiondir)
        for dates in datelist:
            logging.debug(dates)
            # fname = "dt_med_{0}_adt_vfec_{1}_{2}.nc".format(mission, dates, '*')
            fname = "dt_med_{0}_phy_vxxc_l3_{1}_{2}.nc".format(mission, dates, '*')
            flist = glob.glob(os.path.join(datadir, "".join((dates[:4], '/', fname))))

            # Check if at least one file is found
            # with H2 mission some files are missing
            if len(flist) != 0:
                filelist.append(flist[0])
                nfiles += 1
    logging.info("Found {0} files for the selected period and missions".format(nfiles))
    return filelist


def plot_data_tracklist(filelist, m, figname=None, figtitledate=None, meridians=None, parallels=None,
                        vmin=-0.20, vmax=0.20, cmap=plt.cm.RdYlBu_r):
    """
    Create a plot with all the along-track SLA or ADT for the selected period
    """
    plt.figure(figsize=(6, 6))
    plt.subplot(111)

    for datafiles in filelist:
        slatrack = Track()
        slatrack.read_from_cmems_sla(datafiles)
        slatrack.add_to_map(m, s=1, vmin=vmin, vmax=vmax, cmap=cmap)

    m.drawmeridians(meridians, labels=[0, 0, 0, 1], linewidth=.2, zorder=2)
    m.drawparallels(parallels, labels=[1, 0, 0, 0], linewidth=.2, zorder=2)
    m.drawcoastlines(linewidth=.2, zorder=4)

    cbar = plt.colorbar(shrink=.5, extend='both')
    cbar.set_label("m", fontsize=12, rotation=0)

    if figtitledate is not None:
        plt.title(figtitledate)

    if figname is not None:
        plt.savefig(figname)
        plt.close()

def write_tracks2file(filelist, divandfile, divafile, timescale, datemid):
    """
    Write the selected tracks in files suitable for divand and for diva
    :param filelist:
    :param divandfile:
    :param divafile:
    :param timescale:
    :param datemid:
    :return:
    """
    for datafiles in filelist:
        slatrack = Track()
        slatrack.read_from_cmems_sla(datafiles)

        # Write the file for divand
        if divandfile is not None:
            slatrack.write_divandfile(divandfile)

        # Write the file for diva (4 columns: lon, lat, field, weigth)
        if divafile is not None:
            slatrack.write_divafile(divafile, timescale, datemid)

