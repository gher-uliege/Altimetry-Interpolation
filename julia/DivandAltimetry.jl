module DivandAltimetry
using DIVAnd
using NCDatasets
using PyPlot
using Statistics

"""
    shiftlon(longitude)

Subtract 360. to the longitude if the value is larger than 180.

# Examples
```julia-repl
julia> shiftlon(187.2)
-172.8
```
"""
function shiftlon(longitude::Number)
    if (longitude.>180.)
        longitude -= 360.;
    end;
    return longitude
end;


"""
Generate a list of netCDF file paths located within a directory `datadir`
"""
function get_file_list(datadir::String, year::Int=0)::Array
    if year == 0
        # Will find all the files
        yearstring = ""
    else
        # Will find only the files for the selected year
        yearstring = string(year)
    end

    filelist = []
    for (root, dirs, files) in walkdir(datadir)
        for file in files
            if endswith(file, ".nc") & (occursin(yearstring, root))
                push!(filelist, joinpath(root, file));
            end
        end
    end
    @info("Found $(length(filelist)) files")
    return filelist
end


"""
    loadaviso_alongtrack(datafile, varname)

Load the coordinates (longitude, latitude, time) and the selected variable
(SLA by default) from a single netCDF file.

"""
function loadaviso_alongtrack(datafile::String, stdname::String="sea_surface_height_above_sea_level")

    if isfile(datafile)
        Dataset(datafile, "r") do ds
            # Get coordinates
            obslon = coalesce.(NCDatasets.varbyattrib(ds, standard_name="longitude")[1][:])
            obslat = coalesce.(NCDatasets.varbyattrib(ds, standard_name="latitude")[1][:]);
            obstime = coalesce.(NCDatasets.varbyattrib(ds, standard_name="time")[1][:]);
            obsval = coalesce.(NCDatasets.varbyattrib(ds, standard_name=stdname)[1][:], NaN);
            # Shift longitudes
            obslon = DivandAltimetry.shiftlon.(obslon);
        end
    else
        obsval,obslon,obslat,obstime = nothing, nothing, nothing, nothing
    end

    return obsval,obslon,obslat,obstime
end;

"""
    loadaviso_alongtrack(filelist, varname)

Load the coordinates (longitude, latitude, time) and the selected variable
(SLA by default) from a list of netCDF files.

"""
function loadaviso_alongtrack(filelist::AbstractVector, stdname::String="sea_surface_height_above_sea_level")

    nfiles = length(filelist);
    if nfiles == 0
        @warn("Empty file list");
        obsvallist,obslonlist,obslatlist,obstimelist =
        nothing, nothing, nothing, nothing;
    else
        obsvallist,obslonlist,obslatlist,obstimelist = loadaviso_alongtrack(filelist[1], stdname)
        if nfiles > 1
            for datafile in filelist[2:end]
                obsval,obslon,obslat,obstime = loadaviso_alongtrack(datafile, stdname)
                obslonlist = vcat(obslonlist, obslon);
                obslatlist = vcat(obslatlist, obslat);
                obstimelist = vcat(obstimelist, obstime);
                obsvallist = vcat(obsvallist, obsval);
            end
        end
    end;

    return obsvallist,obslonlist,obslatlist,obstimelist
end;

"""
    loadaviso_gridded(datafile, varname)

Load the coordinates (longitude, latitude, time) and the gridded field
representing the selected variable (SLA by default) from a netCDF file.

"""
function loadaviso_gridded(datafile::String, stdname::String="sea_surface_height_above_sea_level")

    if isfile(datafile)
        Dataset(datafile, "r") do ds;
            # Get coordinates
            gridlon = coalesce.(NCDatasets.varbyattrib(ds, standard_name="longitude")[1][:])
            gridlat = coalesce.(NCDatasets.varbyattrib(ds, standard_name="latitude")[1][:]);
            gridtime = coalesce.(NCDatasets.varbyattrib(ds, standard_name="time")[1][:]);
            gridval = coalesce.(NCDatasets.varbyattrib(ds, standard_name=stdname)[1][:], NaN);
            griderr = coalesce.(NCDatasets.varbyattrib(ds, long_name = "Formal mapping error")[1][:], NaN);
            # Shift longitudes
            gridlon = DivandAltimetry.shiftlon.(gridlon);
        end

        gridval = dropdims(gridval; dims=3)
        griderr = dropdims(griderr; dims=3)
    else
        @warn("$(datafile) does not exist")
        gridval,griderr,gridlon,gridlat,gridtime = nothing, nothing, nothing, nothing, nothing
    end

    return gridval,griderr,gridlon,gridlat,gridtime

end;

"""
    gradX, gradY = gradient2D(field)

Compute the gradient along X and Y of a 2-D array.

"""
function gradient2D(field::AbstractArray)
    gradX = field[:,2:end] - field[:,1:end-1];
    gradY = field[2:end,:] - field[1:end-1,:];
    return gradX, gradY
end

"""
    get_aspect_ratio(lat)

Compute the aspect ratio of the map based on the mean latitude.

"""
function get_aspect_ratio(lat::AbstractVector)
    return 1. /cos(mean(lat) * pi/180.0);
end


end
