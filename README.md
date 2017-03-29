# Settings

## Domain of interest

The Mediterranean Sea is a region rich of mesoscale features. At the same time the region is small enough to allow for analysis performed in a reasonable time.

## Period of interest

The first test were performed on a period around May 25, 2014, since we have a good data set of in situ measurements to validate the result.


# Data

Provided by [AVISO](http://www.aviso.altimetry.fr/en/data.html). For a given day, severall altimetric mission are available, and the idea is to combine the measurements from those satellite.

The following image shows the data coverage obtained if we combine all the measurements between May 5 and June 4, 2014.

## Variable

In this application we interpolate the *Absolute Dynamic Topography* (ADT), which is computed as the sum of the Sea Level Anomaly (SLA) and the Mean Dynamic Topography (MDT).

## Preprocessing

The along track data selected are *vfec* product, the which stands for Validated Filtered Échantilloné (sampled) Corrected. With this product the mean distance between 2 consecutive measurements is about 14 kilometers.

# Procedure 

## Data download

The gzipped netCDF files are downloaded from AVISO FTP server and decompressed.
The directory structure is kept identical to AVISO inside a Data directory:

${DATADIR}/regional-mediterranean/delayed-time/along-track/filtered/adt/al

where al represent the mission (here: Altika).

## Input file preparation

Among all the netCDF files, only the content of those corresponding to the selected period are read and then written into a simple text file. [This step](./python/plot_AVISO_data.ipynb) is written in python but could be easily translated to Julia.

## Divand execution

A [Julia script](divand_altimetry.ipynb) reads the data, prepare the analysis parameters and run the interpolation.

