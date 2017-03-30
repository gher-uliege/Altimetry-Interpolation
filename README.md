# Settings

## Domain of interest

The Mediterranean Sea is a region rich of mesoscale features. At the same time the region is small enough to allow for analysis performed in a reasonable time.

## Period of interest

The first test were performed on a period around May 25, 2014, since we have a good data set of in situ measurements to validate the result.


# Data

Provided by [AVISO](http://www.aviso.altimetry.fr/en/data.html). For a given day, severall altimetric mission are available, and the idea is to combine the measurements from those satellite.

The following image shows the data coverage obtained if we combine all the measurements between May 5 and June 4, 2014.

![ADT data](figures/ADT_20140515_20140604.png?raw=true)

## Variable

In this application we interpolate the *Absolute Dynamic Topography* (ADT), which is computed as the sum of the Sea Level Anomaly (SLA) and the Mean Dynamic Topography (MDT).


## Preprocessing

The along track data selected are *vfec* product, the which stands for Validated Filtered Échantilloné (sampled) Corrected. With this product the mean distance between 2 consecutive measurements is about 14 kilometers.

# Procedure 

## Data download

The gzipped netCDF files are downloaded from [AVISO FTP server](ftp.aviso.altimetry.fr) and decompressed.
The directory structure is kept identical to AVISO inside a Data directory:

${DATADIR}/regional-mediterranean/delayed-time/along-track/filtered/adt/al

where al represent the mission (here: Altika).

## Input file preparation

Among all the netCDF files, only the content of those corresponding to the selected period are read and then written into a simple text file. [This step](./python/plot_AVISO_data.ipynb) is written in python but could be easily translated to Julia.

## Parameters

* Correlation lengths: <br>
len = (1°, 1°, 4 days);
* Obs. error variance normalized by the background error variance <br>
epsilon2 = 1;
* Output grid: <br>
Time: 1 day<br>
Space: tested from 1° x 1° to 0.25° x 0.25°. 

## Divand execution

A [Julia script](divand_altimetry.ipynb) reads the data, prepare the analysis parameters and run the interpolation.

# Results 

The outputs are converted to netCDF.<br>
The example shows the field corresponding to May 25, 2014. Comparisons with existing gridded field will be performed.

![ADT field](figures/ADT_divand_20140525.png?raw=true "Interpolated field of ADT")

## Computation time

| Spatial resolution  | Temporal resolution | Time   | Allocation   |  
|:--------------------------:|:--------------------------:|-----------|---|
| (° x °)                    | (days)                     | (s)       |    |
| 1 x 1                      | 2                          | 6.130323  | 914.89 k allocations: 424.083 MB, 23.83% gc time |
| 1 x 1                      | 1                          | 15.206535 | 1.39 M allocations: 923.716 MB, 4.65% gc time |
| 1 x 0.5                    | 1                          | 18.585559 | 2.27 M allocations: 1.950 GB, 4.31% gc time |
| 0.5 x 0.5                  | 1                          | 27.129639 | 4.03 M allocations: 3.907 GB, 5.55% gc time | 
| 0.5 x 0.25                 | 1                          | 74.552338 | 7.51 M allocations: 9.136 GB, 3.28% gc time |

