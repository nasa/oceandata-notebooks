# ---
# jupyter:
#   jupytext:
#     cell_metadata_filter: all,-trusted
#     notebook_metadata_filter: -all,jupytext,language_info.name
#     text_representation:
#       extension: .py
#       format_name: light
#       format_version: '1.5'
#       jupytext_version: 1.16.7
#   language_info:
#     name: python
# ---

# # Orientation to PACE OCI Terrestrial Products 
# **Tutorial Lead:** Skye Caplan (NASA, SSAI) 
#
# <div class="alert alert-info" role="alert">
#
# An [Earthdata Login][edl] account is required to access data from the NASA Earthdata system, including NASA ocean color data.
#
# </div>
#
# [edl]: https://urs.earthdata.nasa.gov/
#
# ## Summary
#
# This notebook will use `earthaccess` to search and access PACE OCI surface reflectance data and provide tools for visualization and masking. This notebook also includes example code to convert netcdfs to GeoTIFFs, making them compatible in a GIS platform. 
#
# ## Learning objectives
#
# By the end of this notebook you will be able to:
# - Open PACE OCI surface reflectance products
# - Mask those products for features you want to exclude from your analysis that are flagged in the data
# - Convert Level-2 OCI data to a GIS compatible format
# - Export those GIS compatible data as a GeoTIFF
#   
#
# ## Contents
# 1. [Setup](#1.-Setup)
# 2. [Search and Open Surface Reflectance Data](#2.-Search-and-Open-Surface-Reflectance-Data)
# 3. [Mask Data for Clouds and Water](#3.-Mask-Data-for-Clouds-and-Water)
# 4. [GIS Compatibility](#4.-GIS-Compatibility)
# 5. [Convert netCDF to GeoTIFF Format](#5.-Convert-netCDF-to-GeoTIFF-Format)
#    
# -------

# ## 1. Setup
#
# We begin by importing the packages used in this notebook. 

# +
import os
import numpy as np 
import xarray as xr
import cartopy.crs as ccrs 
import matplotlib.pyplot as plt 
import earthaccess
import cf_xarray
from xarray.backends.api import open_datatree
# -


# [back to top](#Contents)

# ## 2. Search and Open Surface Reflectance Data
#
# Set and persist your Earthdata login credentials

auth = earthaccess.login(persist=True)

# We will use 'earthaccess' to search and open a specific L2 surface reflectance granule covering the Great Lakes. 

results = earthaccess.search_data(
    short_name="PACE_OCI_L2_SFREFL",
    granule_name = "*20240701T175112*"
)
results[0]

paths = earthaccess.open(results)
paths

paths = earthaccess.download(results, local_path="data")
paths

# We will use open_datatree() to open up all variables within the NetCDF and set the coordinates to the lat, lon variables.

datatree = open_datatree(paths[0])
wavelengths = datatree.sensor_band_parameters.wavelength_3d.values
dataset_dict = datatree.geophysical_data.to_dict()
dataset_dict.update(datatree.navigation_data.to_dict())
# TODO: Find a way to either add wavelength_3d values to the dataset or create a dict of wavelength 3d indices = actual wavelength?? for plot below.
#dataset_dict.update({"wavelength_3d":datatree.sensor_band_parameters.wavelength_3d.to_dict()})
dataset = xr.merge(dataset_dict.values())
dataset = dataset.set_coords(("longitude", "latitude"))
dataset

# In the above print-out of our L2 file, we see the data variables `rhos` and `l2_flags`. The `rhos` variable are surface reflectances, and the `l2_flags` are quality flags as defined by the [Ocean Biology Processing Group].
#
# [Ocean Biology Processing Group]:https://oceancolor.gsfc.nasa.gov/resources/atbd/ocl2flags/
#
# We can also see which wavelengths the surface reflectances correspond to by opening the `wavelength_3d` coordinate:

# Let's plot surface reflectance at 555 nm.

# +
rhos_555 = dataset["rhos"].sel({"wavelength_3d": np.argwhere(wavelengths == 555)[0][0]})

fig = plt.figure(figsize=(8,5))
ax = plt.axes(projection=ccrs.PlateCarree())
ax.coastlines(linewidth=0.5)
ax.gridlines(draw_labels={"left": "y", "bottom": "x"},linewidth=0.25)
rhos_555.plot(x='longitude', y='latitude', cmap='viridis', vmin=0, vmax=1.0)
ax.set_title('Surface reflectance at 555 nm')
# -

# Great! We've plotted the surface reflectance at a single band for the whole scene. However, there are some clouds in this image that we want to exclude from our analysis. 

# [back to top](#Contents)

# ## 3. Mask for Clouds and Water
#
# Let's look more closely at the `l2_flags` variable.

dataset.l2_flags

# `l2_flags` is in the same shape as the surface reflectance we plotted above, but plotting the variable doesn't seem to give us any information. That's because `l2_flags` is actually a 2D array of numbers representing bitflags, so they must be treated as bits and not numbers.
#
# There are a couple ways to deal with bitflags - thankfully, one of those is to use `cf_xarray`, which is a part of the `xarray` package that allows you to access any [CF metadata convention](http://cfconventions.org/) attributes present in a file. 
#
# For example, say we want to mask any pixels flagged as clouds and or water in our data. First, we have to make sure that the `l2_flags` variable is readable by `cf_xarray` so that we can eventually apply them to the data. We can check this using the built in `is_flag_variable` function:

print('Is l2_flags a flag variable?: ', dataset.l2_flags.cf.is_flag_variable)

# The statement returned "True", which means `l2_flags` is recognized as a flag variable. By referencing [this link](https://oceancolor.gsfc.nasa.gov/resources/atbd/ocl2flags/) which describes each flag, we find the name of the ones we want to mask out. In this case, "CLDICE" is the cloud flag, and while there is no specific water mask (this is an ocean mission, after all) there is a LAND flag we can invert to mask out water. The cell below will retain any pixel identified as land which is also not a cloud (thanks to the `~`):

cldwater_mask = (dataset.l2_flags.cf == 'LAND') & ~(dataset.l2_flags.cf == 'CLDICE')
land_values = dataset.where(cldwater_mask)

# Then, we can see if the mask worked by plotting the same wavelength once again:

# +
land_rhos_555 = land_values["rhos"].sel({"wavelength_3d": np.argwhere(wavelengths == 555)[0][0]})

fig = plt.figure(figsize=(8,6))
ax = plt.axes(projection=ccrs.PlateCarree())
ax.coastlines(linewidth=0.5)
ax.gridlines(draw_labels={"left": "y", "bottom": "x"},linewidth=0.25)
land_rhos_555.plot(x='longitude', y='latitude', cmap='viridis', vmin=0)
ax.set_title('Surface reflectance at 555 nm with cloud & water mask')
# -

# ## 4. Working with PACE Terrestrial Data
#
# Now that we have our surface reflectance data masked, 

# [back to top](#Contents)

# ## 4. GIS Compatibility
#
# Let's take a look at the the `masked_dataset`:

masked_dataset

# Since PACE data is hyperspectral, we're working with a 3D array of reflectances. We have dimensions `number_of_lines` (rows, or our 'y' variable), `pixels_per_line` (columns, or our 'x' variable), and wavelength_3d, which is an array of wavelengths in our hyperspectral data cube. The dimensions are in this *exact* order, so when we load a L2 surface reflectance NetCDF into QGIS, it looks a little funky. 
#
# Because of the way PACE data orders its dimensions - that is, with `number_of_lines` first - QGIS reads that as the dimension we're interested in looking at. There's a simple way to fix this so that instead of reading the y variable, QGIS will show us the surface reflectance, our actual variable of interest. 
#
# All we have to do to fix this is to transpose our dataset. Thankfully, xarray has this capability as well.

transposed_file = masked_dataset.transpose("wavelength_3d", "number_of_lines", "pixels_per_line")
transposed_file

# Now we can see that ```rhos``` has the correct dimension order: wavelength, row, column. We can export this new set up using `xarray` again:

output_path = paths[0].replace(".nc","_transposed.nc")
transposed_file.to_netcdf(path=output_path)

# If we load that new file into QGIS, we see that now wavelength is the dimension that varies! Remember that these data are still in the instrument swath and have not been projected to any coordinate system yet.
#
# We're finally close to being done! If you're fine working with netCDF format, you could stop here. The final thing we'll take you through is how to convert netCDF to a GeoTIFF format.

#



