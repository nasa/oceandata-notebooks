# # File Structure at Three Processing Levels for the Ocean Color Instrument (OCI)
#
# **Authors:** Anna Windle (NASA, SSAI), Ian Carroll (NASA, UMBC), Carina Poulin (NASA, SSAI)
#
# <div class="alert alert-success" role="alert">
#
# The following notebooks are **prerequisites** for this tutorial.
#
# - Learn with OCI: [Data Access][oci-data-access]
#
# </div>
#
# <div class="alert alert-info" role="alert">
#
# An [Earthdata Login][edl] account is required to access data from the NASA Earthdata system, including NASA ocean color data.
#
# </div>
#
# [edl]: https://urs.earthdata.nasa.gov/
# [oci-data-access]: https://oceancolor.gsfc.nasa.gov/resources/docs/tutorials/notebooks/oci_data_access/
#
# ## Summary
#
# In this example we will use the `earthaccess` package to access OCI Level-1B (L1B), Level-2 (L2), and Level-3 (L3) NetCDF files and open them using `xarray`. While you can learn alot exploring the datasets in this way, be ready to refer to the full [dataset documentation][user-guides] for details about the data products and processing.
#
# **NetCDF** ([Network Common Data Format][netcdf]) is a binary file format for storing multidimensional scientific data (variables). It is optimized for array-oriented data access and support a machine-independent format for representing scientific data. Files ending in `.nc` are NetCDF files.
#
# **XArray** is a [package][xarray] that supports the use of multi-dimensional arrays in Python. It is widely used to handle Earth observation data, which often involves multiple dimensions — for instance, longitude, latitude, time, and channels/bands.
#
# [netcdf]: https://www.unidata.ucar.edu/software/netcdf/
# [user-guides]: https://oceancolor.gsfc.nasa.gov/resources/docs/technical/#UG
# [xarray]: https://docs.xarray.dev/
#
# ## Learning Objectives
#
# At the end of this notebok you will know:
# * How to find groups in a NetCDF file
# * How to use `xarray` to open OCI data
# * What key variables are present in the groups within OCI L1B, L2, and L3 files
#
# ## Contents
#
# 1. [Setup](#1.-Setup)
# 2. [Explore L1B File Structure](#2.-Explore-L1B-File-Structure)
# 3. [Explore L2 File Structure](#3.-Explore-L2-File-Structure)
# 4. [Explore L3 File Structure](#4.-Explore-L3-File-Structure)

# ## 1. Setup
#
# Begin by importing all of the packages used in this notebook. If your kernel uses an environment defined following the guidance on the [tutorials] page, then the imports will be successful.
#
# [tutorials]: https://oceancolor.gsfc.nasa.gov/resources/docs/tutorials

import cartopy.crs as ccrs
import earthaccess
import h5netcdf
import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
import xarray as xr

# Set (and persist to your user profile on the host, if needed) your Earthdata Login credentials.

auth = earthaccess.login(persist=True)

# [back to top](#Contents)

# ## 2. Explore L1B File Structure
#
# Let's use `xarray` to open up a OCI L1B NetCDF file using `earthaccess`. We will use the same search method used in <a href="oci_data_access.html">OCI Data Access</a>. Note that L1B files do not include cloud coverage metadata, so we cannot use that filter.

tspan = ("2024-05-01", "2024-05-16")
bbox = (-76.75, 36.97, -75.74, 39.01)

results = earthaccess.search_data(
    short_name="PACE_OCI_L1B_SCI",
    temporal=tspan,
    bounding_box=bbox,
)

paths = earthaccess.open(results)

# We want to confirm we are running code on a remote host with direct access to the NASA Earthdata Cloud. The next cell has
# no effect if we are, and otherwise raises an error. If there is an error, consider the substitution explained in the [Data Access][data-access] notebook.
#
# [data-access]: https://oceancolor.gsfc.nasa.gov/resources/docs/tutorials/notebooks/oci_data_access/

try:
    paths[0].f.bucket
except AttributeError:
    raise Exception("The result opened without an S3FileSystem.") from None

# Let's open the first file of the L1B files list:

dataset = xr.open_dataset(paths[0])
dataset

# Notice that this `xarray.Dataset` has nothing but "Attributes". We cannot use `xarray` to open multi-group hierarchies or list groups within a NetCDF file, but it can open a specific group if you know its path. The `xarray-datatree` package is going to be merged into `xarray` in the not too distant future, which will allow `xarray` to open the entire hierarchy. In the meantime, we can use a lower level reader to see the top-level groups.

with h5netcdf.File(paths[0]) as file:
    groups = list(file)
groups

# Let's open the "observation_data" group, which contains the core science variables.

dataset = xr.open_dataset(paths[0], group="observation_data")
dataset

# Now you can view the Dimensions, Coordinates, and Variables of this group. To show/hide attributes, press the paper icon on the right hand side of each variable. To show/hide data representation, press the cylinder icon. For instance, you could check the attributes on "rhot_blue" to see that this variable is the "Top of Atmosphere Blue Band Reflectance".
#
# The dimensions of the "rhot_blue" variable are ("blue_bands", "number_of_scans", "ccd_pixels"), and it has shape (119, 1709, 1272). The `sizes` attribute of a variable gives us that information as a dictionary.

dataset["rhot_blue"].sizes

# Let's plot the reflectance at postion 100 in the "blue_bands" dimension.

im = dataset["rhot_blue"].sel({"blue_bands": 100}).plot()

# [back to top](#Contents)

# ## 3. Explore L2 File Structure
#
# OCI L2 files include retrievals of geophysical variables, such as Apparent Optical Properties (AOP), for each L1 swath. We'll use the same `earthaccess` search for L2 AOP data. Although now we can use `cloud_cover` too.

tspan = ("2024-05-01", "2024-05-16")
bbox = (-76.75, 36.97, -75.74, 39.01)
clouds = (0, 50)
results = earthaccess.search_data(
    short_name="PACE_OCI_L2_AOP_NRT",
    temporal=tspan,
    bounding_box=bbox,
    cloud_cover=clouds,
)

paths = earthaccess.open(results)

with h5netcdf.File(paths[0]) as file:
    groups = list(file)
groups

# Let's look at the "geophysical_data" group, which is a new group generated by the level 2 processing.

dataset = xr.open_dataset(paths[0], group="geophysical_data")
rrs = dataset["Rrs"]
rrs

rrs.sizes

# The Rrs variable has length 184 in the wavelength dimension, so the blue, red, and SWIR wavelengths have been combined. Let's map the Rrs at "wavelength_3d" position 100.

im = rrs.sel({"wavelength_3d": 100}).plot(cmap="viridis", robust=True)

# Right now, the scene is being plotted using `number_of_lines` and `pixels_per_line` as "x" and "y", respectively. We need to add latitude and longitude values to create a true map. To do this, we will create a merged `xarray.Dataset` that pulls in information from the "navigation_data" group.

dataset = xr.open_dataset(paths[0], group="navigation_data")
dataset = dataset.set_coords(("longitude", "latitude"))
dataset = xr.merge((rrs, dataset.coords))
dataset

# Although we now have coordinates, they won't immediately help because the data are not gridded by latitude and longitude.
# The Level 2 data cover the original instrument swath and have not been resampled to a regular grid. Therefore latitude
# and longitude are known, but cannot be used immediately to "look-up" values like you can along an array's dimensions.
#
# Let's make a scatter plot of the pixel locations so we can see the irregular spacing. By selecting a `slice` with a step size larger than one, we get a subset of the locations for better visualization.

im = dataset.sel(
    {
        "number_of_lines": slice(None, None, 1720 // 20),
        "pixels_per_line": slice(None, None, 1272 // 20),
    },
).plot.scatter(x="longitude", y="latitude")

# Let's plot this new `xarray.Dataset` the same way as before, but add latitude and longitude.

rrs_sel = dataset["Rrs"].sel({"wavelength_3d": 100})
im = rrs_sel.plot(x="longitude", y="latitude", cmap="viridis", robust=True)

# Now you can visualize the data projected onto a grid. If you wanna get fancy, add a coastline.

fig = plt.figure()
ax = plt.axes(projection=ccrs.PlateCarree())
im = rrs_sel.plot(x="longitude", y="latitude", cmap="viridis", robust=True, ax=ax)
ax.gridlines(draw_labels={"left": "y", "bottom": "x"})
ax.coastlines()
plt.show()

# Let's plot the full "Rrs" spectrum for individual pixels. A visualization with all the pixels
# wouldn't be useful, but limiting to a bounding box gives a simple way to subset pixels. Note that,
# since we still don't have gridded data (i.e. our latitude and longitude coordinates are two-dimensional),
# we can't `slice` on a built-in index. Without getting into anything complex, we can just box it out.

rrs_box = dataset["Rrs"].where(
    (
        (dataset["latitude"] > 37.52)
        & (dataset["latitude"] < 37.55)
        & (dataset["longitude"] > -75.46)
        & (dataset["longitude"] < -75.43)
    ),
    drop=True,
)
rrs_box.sizes

# The line plotting method will only draw a line plot for 1D data, which we can get by stacking
# our two spatial dimensions and choosing to show the new "pixel dimension" as different colors.

rrs_stack = rrs_box.stack(
    {"pixel": ["number_of_lines", "pixels_per_line"]},
    create_index=False,
)
plot = rrs_stack.plot.line(hue="pixel")

# We will go over how to plot Rrs spectra with accurate wavelength values on the x-axis in an upcoming notebook.
#
# [back to top](#Contents)

# ## 4. Explore L3 File Structure
#
# At Level-3 there are binned (B) and mapped (M) products available for OCI. The L3M remote sensing reflectance (Rrs) files contain global maps of Rrs. We'll use the same `earthaccess` method to find the data.

tspan = ("2024-05-01", "2024-05-08")
results = earthaccess.search_data(
    short_name="PACE_OCI_L3M_RRS_NRT",
    temporal=tspan,
    #    count=1,
)

paths = earthaccess.open(results)

# OCI L3 data do not have any groups, so we can open the dataset without the `group` argument.
# Let's take a look at one of these files. Not just any one; we will search for the one that is a
# high resolution map.

for item in paths:
    dataset = xr.open_dataset(item)
    if dataset.sizes["lat"] == 4320:
        break
dataset

# Notice that OCI L3M data has `lat`, `lon`, and `wavelength` coordinates, so it's easy to slice
# out a bounding box and map the "Rrs" variable at a given wavelength.

rrs_slice = dataset["Rrs"].sel({"lat": slice(-25, -45), "lon": slice(10, 30)})
rrs_slice_442 = rrs_slice.sel({"wavelength": 442}, method="nearest")
rrs_slice_442

fig = plt.figure()
ax = plt.axes(projection=ccrs.PlateCarree())
im = rrs_slice_442.plot(cmap="viridis", robust=True, ax=ax)
ax.gridlines(draw_labels={"left": "y", "bottom": "x"})
ax.coastlines()
plt.show()

# Also becuase the L3M variables have `lat` and `lon` coordinates, it's possible to stack multiple granules along a new dimension that corresponds to time.
# Instead of `xr.open_dataset`, we use `xr.open_mfdataset` to create a single `xarray.Dataset` (the "mf" in `open_mfdataset` stands for multiple files) from an array of paths.
#
# Rather than searching through results for particular resolutions though, we need to augment the CMR query using information
# build into the granule name. Take a look at the attribute on the previous dataset.

dataset.attrs["product_name"]

# We will use a new search filter available in `search_data`: the `granule_name` argument accepts strings with the "*" wildcard. We need this to distinguish daily ("DAY") from eight-day ("8D") composites, as well as to get the desired 0.1 degree resolution projections.

results = earthaccess.search_data(
    short_name="PACE_OCI_L3M_CHL_NRT",
    temporal=tspan,
    granule_name="*.DAY.*.0p1deg.*",
)

paths = earthaccess.open(results)

# The `paths` list is sorted temporally by default, which means the shape of the `paths` array specifies the way we need to tile the files together into larger arrays. We specify `combine="nested"` to combine the files according to the shape of the array of files (or file-like objects), even though `paths` is not a "nested" list in this case. The `concat_dim="date"` argument generates a new dimension in the combined dataset, because "date" is not an existing dimension in the individual files.

dataset = xr.open_mfdataset(
    paths,
    combine="nested",
    concat_dim="date",
)

# Add a date dimension using the dates from the netCDF files.

dates = [xr.open_dataset(a).attrs["time_coverage_end"] for a in paths]
dt = pd.to_datetime(dates)
dataset = dataset.assign_coords(date=dt.values)
dataset

# A common reason to generate a single dataset from multiple, daily images is to create a composite. Compare the map from a single day ...

chla = np.log10(dataset["chlor_a"])
chla.attrs.update(
    {
        "units": f'log({dataset["chlor_a"].attrs["units"]})',
    }
)
im = chla.sel(date="2024-05-02").plot(aspect=2, size=4, cmap="GnBu_r")

# ... to a map of average values, skipping "NaN" values that result from clouds and the OCI's tilt maneuver.

chla_avg = chla.mean("date", keep_attrs=True)
im = chla_avg.plot(aspect=2, size=4, cmap="GnBu_r")

# We can also create a time series of mean values over the whole region.

chla_avg = chla.mean(dim=["lon", "lat"], keep_attrs=True)
im = chla_avg.plot(linestyle="-", marker="o", color="b")

# [back to top](#Contents)
#
# <div class="alert alert-info" role="alert">
#
# You have completed the notebook on OCI file structure.
#
# </div>
