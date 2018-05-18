module DivandAltimetry

using divand
using NCDatasets
using PyPlot

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
    loadaviso_alongtrack(datafile, varname)

Load the coordinates (longitude, latitude, time) and the selected variable
(SLA by default) from a single netCDF file.

"""
function loadaviso_alongtrack(datafile::String, varname::String="SLA")

    if isfile(datafile)
        ds = Dataset(datafile, "r");
        # Get coordinates
        obslon = ds["longitude"][:];
        obslat = ds["latitude"][:];
        obstime = ds["time"][:];
        obsval = ds[varname][:];
        obsdepth = zeros(obsval);
        # Shift longitudes
        obslon = shiftlon.(obslon);
        close(ds)
    else
        obsval,obslon,obslat,obsdepth,obstime = nothing, nothing, nothing, nothing, nothing
    end

    return obsval,obslon,obslat,obsdepth,obstime
end;



"""
    loadaviso_alongtrack(filelist, varname)

Load the coordinates (longitude, latitude, time) and the selected variable
(SLA by default) from a list of netCDF files.

"""
function loadaviso_alongtrack(filelist::AbstractVector, varname::String="SLA")

    nfiles = length(filelist);
    if nfiles == 0
        warn("Empty file list");
        obsvallist,obslonlist,obslatlist,obsdepthlist,obstimelist =
        nothing, nothing, nothing, nothing, nothing;
    else
        obsvallist,obslonlist,obslatlist,obsdepthlist,obstimelist = loadaviso_alongtrack(filelist[1], varname)
        if nfiles > 1
            for datafile in filelist[2:end]
                obsval,obslon,obslat,obsdepth,obstime = loadaviso_alongtrack(datafile, varname)
                obslonlist = vcat(obslonlist, obslon);
                obslatlist = vcat(obslatlist, obslat);
                obsdepthlist = vcat(obsdepthlist, obsdepth);
                obstimelist = vcat(obstimelist, obstime);
                obsvallist = vcat(obsvallist, obsval);
            end
        end
    end;

    return obsvallist,obslonlist,obslatlist,obsdepthlist,obstimelist
end;

"""
    loadaviso_gridded(datafile, varname)

Load the coordinates (longitude, latitude, time) and the gridded field
representing the selected variable (SLA by default) from a netCDF file.

"""
function loadaviso_gridded(datafile::String, varname::String="sla")

    if isfile(datafile)
        ds = Dataset(datafile, "r");
        # Get coordinates
        gridlon = ds["lon"][:];
        gridlat = ds["lat"][:];
        gridtime = ds["time"][:];
        gridval = ds[varname][:,:,1];
        griderr = ds["err"][:,:,1]
        # Shift longitudes
        gridlon = shiftlon.(gridlon);
        close(ds)
    else
        warn("$(datafile) does not exist")
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
    return 1/cos(mean(lat)) * pi/180;
end


end
