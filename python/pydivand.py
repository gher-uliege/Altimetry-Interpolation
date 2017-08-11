import os
import numpy as np
import matplotlib.pyplot as plt
import netCDF4
import logging
import datetime
import glob


class Parameters(object):
    """
    Class to store all the analysis parameters
    """

    def __init__(self, origins=None, ends=None, steps=None):
        """
        :param origins: tuple of floats representing the coordinates of the 1st point
        :param ends: tuple of floats representing the coordinates of the last point
        :param steps: tuple of floats representing the spatial/temporal steps
        """

        self.origins = origins
        self.ends = ends
        self.steps = steps
        if self.origins is not None:
            self.ndim = len(self.origins)
        else:
            self.ndim = 0

    def get_domain_size(self):
        """
        Compute the number of points in each dimension
        :return: npoints
        :type npoints: list of integers
        """
        self.npoints = []
        for i in range(0, self.ndim):
            self.npoints.append((self.ends[i] - self.origins[i]) / self.steps[i])

    def to_file(self, filename):
        """
        Write the domain of interest to a file
        :param filename: path to the file to write
        :type filename: str
        """
        with open(filename, 'w') as f:
            for i in range(0, self.ndim):
                f.write("\n".join((str(self.origins[i]),
                                       str(self.steps[i]),
                                       str(self.ends[i]), ""))
                       )

    def from_file(self, filename):
        """
        Read the parameters from a file
        :param filename: path to the file from which the parameters will be read
        :type
        :return: self
        """
        if os.path.exists(filename):
            with open(filename, 'r') as f:
                pass




        return self

