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

# ## 1. Setup
#
# We begin by importing the packages used in this notebook.

# +
import cartopy.crs as ccrs
import cf_xarray  # noqa: F401 (unused-import)
import earthaccess
import matplotlib.pyplot as plt
import numpy as np
import xarray as xr
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
    granule_name="*20240701T175112*",
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
# dataset_dict.update({"wavelength_3d":datatree.sensor_band_parameters.wavelength_3d.to_dict()})
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

fig = plt.figure(figsize=(8, 5))
ax = plt.axes(projection=ccrs.PlateCarree())
ax.coastlines(linewidth=0.5)
ax.gridlines(draw_labels={"left": "y", "bottom": "x"}, linewidth=0.25)
rhos_555.plot(x="longitude", y="latitude", cmap="viridis", vmin=0, vmax=1.0)
ax.set_title("Surface reflectance at 555 nm")
# -

# Great! We've plotted the surface reflectance at a single band for the whole scene. However, there are some clouds in this image that we want to exclude from our analysis.

# [back to top](#Contents)

# ## 3. Mask for Clouds and Water
#
# Let's look more closely at the `l2_flags` variable.

dataset.l2_flags

# `l2_flags` is in the same shape as the surface reflectance we plotted above, but plotting the variable doesn't seem to give us any information. That's because `l2_flags` is actually a 2D array of numbers representing bitflags, so they must be treated as bits and not numbers. The meaning of each flag is described [here](https://oceancolor.gsfc.nasa.gov/resources/atbd/ocl2flags/).
#
# For example, in the surface reflectance plot above, say we want to mask clouds. Instead of trying to do some threshold math or applying your own cloud mask algorithm to each pixel, you can use the `l2_flags` variable and use L2gen's cloud mask (CLDICE) instead. Using the reference link above to figure out what bit represents clouds:

bit_position = 9
cloudmasked_dataset = dataset.where(~((dataset.l2_flags & (1 << bit_position)) != 0))
cloudmasked_dataset

# The masked dataset `cloudmasked_dataset` will retain the structure and information contained in the original merged dataset, but will take pixels where the cloud flag is flipped (i.e., where a pixel is flagged as cloudy) and assign them as NaNs. We can plot the data again to see what has changed:

# +
cloudmasked_rhos_555 = cloudmasked_dataset["rhos"].sel(
    {"wavelength_3d": np.argwhere(wavelengths == 555)[0][0]}
)

fig = plt.figure(figsize=(8, 5))
ax = plt.axes(projection=ccrs.PlateCarree())
ax.coastlines(linewidth=0.5)
ax.gridlines(draw_labels={"left": "y", "bottom": "x"}, linewidth=0.25)
cloudmasked_rhos_555.plot(x="longitude", y="latitude", cmap="viridis", vmin=0)
ax.set_title("Surface reflectance at 555 nm with cloud mask")
# -

# To see why this works, let's break down the one line of code which performs the masking.
#
# Each bit in a bitmask represents a specific condition or flag (in the above example, clouds).
#  - The ```(1 << bit position)``` portion of the code isolates the specific "bit" in the bitmask, or in other words the specific condition you want flagged.
# Since clouds are at bit position 9, we set ```bit_position``` to 9 in the example above.
#  - ```ds.l2_flags``` is the variable in our xarray dataset that contains the values for each pixel of the bitmask.
#  - ```ds.l2_flags & (1 << bit_position)``` is basically saying to look only for pixels in the l2_flag variable where the specified bit is set. In other words, to look for pixels that have been flagged as a cloud.
#  - ```~(ds.l2_flags & (1 << bit_position) != 0)```: The entire statement within the parentheses, with ```!= 0```, evaluates any pixel flagged cloudy as ```True```. Adding the ```~``` negates that condition, so that any pixel with the cloud flag set is evaluated to ```False```. We need these pixels to be False for the next step:
#  - ```ds.where(~(ds.l2_flags & (1 << bit_position) != 0))```: ```xarray```'s ```.where``` function applies the mask to the entire dataset, which contains our surface reflectances. It keeps the pixel values which were evaluated to ```True``` in the step above, and assigns anything ```False``` as NaN. In other words, the cloudy pixels we set to "False" above have been set to NaN and therefore have been masked.
#
# We can apply multiple masks to the same datasets as well. Say you wanted to mask for clouds AND water, at the same time. There isn't a dedicated water masked, so instead we'll take the land mask at bit position 1 and invert it to mask out water. We can do that by leaving the ```~``` out of the statement, setting any non-land pixels to ```False``` like we did with clouds above:

# +
masked_dataset = dataset.where(
    ~((dataset.l2_flags & (1 << 9)) != 0) & ((dataset.l2_flags & (1 << 1)) != 0)
)

masked_rhos_555 = masked_dataset["rhos"].sel(
    {"wavelength_3d": np.argwhere(wavelengths == 555)[0][0]}
)

fig = plt.figure(figsize=(8, 5))
ax = plt.axes(projection=ccrs.PlateCarree())
ax.coastlines(linewidth=0.5)
ax.gridlines(draw_labels={"left": "y", "bottom": "x"}, linewidth=0.25)
masked_rhos_555.plot(x="longitude", y="latitude", cmap="viridis", vmin=0)
ax.set_title("Surface reflectance at 555 nm with cloud & water mask")
# -

# #### Alternative method: xarray's masking capabilities
#
# `xarray`'s `cf_xarray` package can read flags as masks as well. This functionality has only been lightly tested, but should work for simple applications like we show below. See the [cf_xarray flag documentation](https://cf-xarray.readthedocs.io/en/latest/flags.html) here for more information.
#
# There are certain requirements our `xarray` dataset must meet in order to be used with `cf_xarray`. First, we need to make sure the package can read the flags properly so we can eventually apply them to the data. Let's check that the flag variable is read as such with `cf_xarray`'s built in check:

print("Is l2_flags a flag variable?: ", dataset.l2_flags.cf.is_flag_variable)

# The above statement shows the package recognizes `l2_flags`. The next step is to apply those flags, similar to the bitmask method. `Xarray` makes it easier by using the `where` function, and you don't have to understand bitwise operators to use it:

# +
cldwater_mask = (dataset.l2_flags.cf == "LAND") & ~(dataset.l2_flags.cf == "CLDICE")
land_values = dataset.where(cldwater_mask)

land_rhos_555 = land_values["rhos"].sel(
    {"wavelength_3d": np.argwhere(wavelengths == 555)[0][0]}
)

fig = plt.figure(figsize=(8, 6))
ax = plt.axes(projection=ccrs.PlateCarree())
ax.coastlines(linewidth=0.5)
ax.gridlines(draw_labels={"left": "y", "bottom": "x"}, linewidth=0.25)
land_rhos_555.plot(x="longitude", y="latitude", cmap="viridis", vmin=0)
ax.set_title("Surface reflectance at 555 nm with cloud & water mask")
# -

# Now that we have our surface reflectance data masked, we have multiple options for analysis. If your preferred data analysis environment is python, great! You can stop here. If you'd prefer to use an analysis software, specifically QGIS, you'll have to go through a couple more steps.

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

transposed_file = masked_dataset.transpose(
    "wavelength_3d", "number_of_lines", "pixels_per_line"
)
transposed_file

# Now we can see that ```rhos``` has the correct dimension order: wavelength, row, column. We can export this new set up using `xarray` again:

output_path = paths[0].replace(".nc", "_transposed.nc")
transposed_file.to_netcdf(path=output_path)

# If we load that new file into QGIS, we see that now wavelength is the dimension that varies! Remember that these data are still in the instrument swath and have not been projected to any coordinate system yet.
#
# We're finally close to being done! If you're fine working with netCDF format, you could stop here. The final thing we'll take you through is how to convert netCDF to a GeoTIFF format.

# ## 5. Veg. Indices/Classification/Working with the data
