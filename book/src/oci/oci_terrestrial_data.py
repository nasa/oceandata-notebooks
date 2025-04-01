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
import cf_xarray
import xarray as xr
import cartopy
import cartopy.crs as ccrs 
import matplotlib.pyplot as plt 
import earthaccess
import holoviews as hv
import hvplot.xarray
import panel as pn
from xarray.backends.api import open_datatree
# -


# [back to top](#Contents)

# ## 2. Search and Open Surface Reflectance Data
#
# Set and persist your Earthdata login credentials

auth = earthaccess.login(persist=True)

# We will use `earthaccess` to search and open a specific L2 surface reflectance granule covering part of the Great Lakes region of North America. 

# Changing granule to Australia for VI example in sect. 4
results = earthaccess.search_data(
    short_name="PACE_OCI_L2_SFREFL",
    granule_name = "*20240701T175112*"#"*20250117T044314*"
)
results[0]

paths = earthaccess.open(results)
paths

paths = earthaccess.download(results, local_path="data")
paths

# We will use open_datatree() to open up all variables within the NetCDF and set the coordinates to the lat, lon variables.

datatree = open_datatree(paths[0])
all_data = xr.merge(datatree.to_dict().values())
all_data = all_data.set_coords(("longitude", "latitude", "wavelength_3d"))
all_data

# The merged dataset has a lot of variables we won't need in this analysis, so we can pull the subset that we need to make it more manageable.

dataset = all_data[["rhos", "l2_flags"]]
dataset

# In the above print-out of our L2 file, we see the data variables `rhos` and `l2_flags`. The `rhos` variable are surface reflectances, and the `l2_flags` are quality flags as defined by the [Ocean Biology Processing Group].
#
# [Ocean Biology Processing Group]:https://oceancolor.gsfc.nasa.gov/resources/atbd/ocl2flags/
#
# We can also see which wavelengths we have surface reflectance measurements at by accessing the `wavelength_3d` coordinate:

dataset.wavelength_3d

# Let's plot surface reflectance in the NIR at 860 nm, where land is bright and we can differentiate land, water, and clouds.

# +
rhos_860 = dataset.sel(wavelength_3d=860, method='nearest')

fig = plt.figure(figsize=(8,5))
ax = plt.axes(projection=ccrs.PlateCarree())
ax.coastlines(linewidth=0.5)
ax.gridlines(draw_labels={"left": "y", "bottom": "x"}, linewidth=0.25)
ax.add_feature(cartopy.feature.OCEAN, edgecolor='w',linewidth=0.01)
ax.add_feature(cartopy.feature.LAND, edgecolor='w',linewidth=0.01)
rhos_860.rhos.plot(x='longitude', y='latitude', cmap='Greys_r', vmin=0, vmax=1.0)
# -

# Great! We've plotted the surface reflectance at a single band for the whole scene (see [this tutorial](https://pacehackweek.github.io/pace-2024/presentations/hackweek/satdata_visualization.html) for how to do an RGB visualization). However, there are some features in this image that we want to exclude from our analysis. 

# [back to top](#Contents)

# ## 3. Mask for Clouds and Water
#
# Level 2 files generally include some information on the quality of each pixel in the scene, presented in the `l2_flags` variable. Let's look at it a little more closely.

dataset.l2_flags

# At first glance, we can see that `l2_flags` is in the same shape as the surface reflectance we plotted above. The attributes provide some information, but a lot of it looks like random numbers and abbreviations. If we were to plot the variable, it wouldn't look like anything useful, either. This is because the values in `l2_flags` are numerical representations those quality flags mentioned above. In order to decode which flags apply to which pixels, we have to treat them differently than we would a normal geophysical variable.
#
# There are a couple ways to deal with these flags. One of those is to use the `cf_xarray` package, which allows you to access any [CF metadata convention](http://cfconventions.org/) attributes present in an `xarray` object. Since all PACE data follows CF conventions, the package should be able to handle the flags for us.
#
# For example, say we want to mask any pixels flagged as clouds and or water in our data. First, we have to make sure that the `l2_flags` variable is readable by `cf_xarray` so that we can eventually apply them to the data. We can check this using the built in `is_flag_variable` function:

print('Is l2_flags a flag variable?: ', dataset.l2_flags.cf.is_flag_variable)

# The statement returned "True", which means `l2_flags` is recognized as a flag variable. By referencing [this link](https://oceancolor.gsfc.nasa.gov/resources/atbd/ocl2flags/) which describes each flag, we find the name of the ones we want to mask out. In this case, "CLDICE" is the cloud flag, and while there is no specific water mask (this is an ocean mission, after all) there is a "LAND" flag we can invert to mask out water. The expressions in the cell below will retain any pixel identified as land which is also not a cloud (thanks to the `~`):

cldwater_mask = (dataset.l2_flags.cf == 'LAND') & ~(dataset.l2_flags.cf == 'CLDICE')
land_only = dataset.where(cldwater_mask)

# Then, we can see if the mask worked by plotting the data once again. Note that we need to redefine the `rhos_860` selection with the new masked dataset.

# +
rhos_860 = land_only.sel(wavelength_3d=860, method='nearest')

fig = plt.figure(figsize=(9,5))
ax = plt.axes(projection=ccrs.PlateCarree())
ax.coastlines(linewidth=0.25)
ax.gridlines(draw_labels={"left": "y", "bottom": "x"},linewidth=0.25)
ax.add_feature(cartopy.feature.OCEAN, edgecolor='w',linewidth=0.01)
ax.add_feature(cartopy.feature.LAND, edgecolor='w',linewidth=0.01)
ax.add_feature(cartopy.feature.LAKES, edgecolor='k',linewidth=0.1)
#land_only["rhos"][:,:,wl_idx].plot(x='longitude', y='latitude', cmap='Greys_r', vmin=0, vmax=1.0)
#ax.set_title(f'Surface reflectance at {wavelengths[wl_idx]} nm with cloud & water mask')
rhos_860.rhos.plot(x='longitude', y='latitude', cmap='Greys_r', vmin=0, vmax=1.0)
# -

# ## 4. Working with PACE Terrestrial Data
#
# ### Multispectral Vegetation Indices
#
# Now that we have our surface reflectance data masked, we can start doing some analysis. A relatively simple but powerful use of surface reflectance data is in the calculation of vegetation indices (VIs). VIs use the well-known, ideal spectral shape of leaves (and other materials) to determine features of the content in a pixel, like how healthy the vegetation is, or the relative water content, or even the presence of snow. They've been used in terrestrial remote sensing for decades, and are particularly valuable when considering the limited number of bands in previous multispectral sensors. They can, of course, also be calculated with hyperspectral sensors like PACE.
#
# Let's take NDVI for example. NDVI is a metric which quantifies plant "greenness", which is related to the abundance and health of the vegetation in a pixel. It is a normalized ratio of the red and NIR bands:
# $$
# NDVI = \frac{\rho_{NIR} - \rho_{red}}{\rho_{NIR} + \rho_{red}}
# $$
#
# You'll notice that the equation does not mention specific wavelengths, but rather just requires a "red" measurement and a "NIR" measurement. With PACE, as we can see in the spectra below, we have a lot of measurements throughout the red and NIR regions of the spectrum. 

r, c, ct = 900, 300, 0
fig, ax = plt.subplots(1,2, figsize=(10, 5), sharey=True)
while ct < 40:
    ax[0].plot(land_only.wavelength_3d.values, land_only.rhos[r, c,:], ls='', marker='o', markersize=2,alpha=0.2, c='k')
    ax[1].plot(land_only.wavelength_3d.values, land_only.rhos[r, c,:], ls='--', marker='o', markersize=6, alpha=0.2, c='k')
    c, ct = c+1, ct+1
ax[0].set_xlim([340, 900])
ax[1].set_xlim([910, 2290])
ax[0].set_xlabel("Wavelength (nm)")
ax[1].set_xlabel("Wavelength (nm)")
ax[0].set_ylabel("Reflectance")


# To calculate NDVI and other heritage multispectral indices with PACE, you could choose a single band from each region. However, doing so would mean capturing only the information from one of OCI's narrow 5 nm bands. In other words, we would miss out on information from surrounding wavelengths that improve these calculations and would have otherwise been included from other sensors. To preserve continuity with those sensors and calculate a more accurate NDVI, we can take an average of several OCI bands to simulate a multispectral measurement, incorporating as much relevant information into the calculation as possible.
#
# We'll take MODIS's red and NIR bandwidths and average the PACE measurements together:

# +
def avg_rfl(data, wl_range):
    '''
    Finds the index of each boundary wavelength and averages data in 
        that range.
    Args:
        data - xarray object containing reflectances variable "rhos" 
        wl_range - list of bounds of wavelengths to average over     
    '''
    lidx = np.argwhere(land_only.wavelength_3d.values == wl_range[0])[0][0]
    hidx = np.argwhere(land_only.wavelength_3d.values == wl_range[1])[0][0]
    return data.rhos[:,:,lidx:hidx].mean(dim="wavelength_3d", skipna=True)

avg_red = avg_rfl(land_only, [620, 670])
avg_nir = avg_rfl(land_only, [840, 875])


# -

# Now, we can use those averaged reflectances to calculate NDVI from PACE:

# +
def get_ndvi(red, nir):
    return (nir - red) / (nir + red)

pace_ndvi = get_ndvi(avg_red, avg_nir)

fig = plt.figure(figsize=(9,5))
ax = plt.axes(projection=ccrs.PlateCarree())
ax.coastlines(linewidth=0.5)
ax.gridlines(draw_labels={"left": "y", "bottom": "x"}, linewidth=0.25)
ax.add_feature(cartopy.feature.OCEAN, edgecolor='w',linewidth=0.01)
ax.add_feature(cartopy.feature.LAND, edgecolor='w',linewidth=0.01)
ax.add_feature(cartopy.feature.LAKES, edgecolor='k',linewidth=0.1)
pace_ndvi.plot(x='longitude', y='latitude', cmap='RdYlGn', vmin=-0.05, vmax=1.0,
              cbar_kwargs={"label":"Normalized Difference Vegetation Index (NDVI)"})
ax.set_title('NDVI from PACE OCI')
# -

# Making these heritage calculations are important for many reasons, not least of which because the MODIS instruments are reaching the end of their lives and will soon be decommissioned. PACE can then fill the gap that would have otherwise been left in the time series of these VI datasets. However, as a hyperspectral instrument, PACE OCI is able to go beyond these legacy calculations and create new products, as well!
#
# ### Hyperspectral-enabled Vegetation Indices
#
# Hyperspectral-enabled VIs are still band ratios, but rather than using wide bands to capture the general aspects of a spectrum, they target minute fluctuations in surface reflectances to describe detailed features of a pixel, such as relative pigment concentration in plants. This means that, unlike multispectral VIs, these indices require the narrow bandwidths inherent to OCI data. In other words, we don't want to do any band averaging as we did above, because we'd likely dilute the very signal we want to pull out. The calculations for this type of VI then become much simpler!
#
# This time, we'll take the Chlorophyll Index Red Edge (CIRE) as an example. CIRE uses bands from the red edge and the NIR to get at relative canopy chlorophyll content:
# $$
# CIRE = \frac{\rho_{800}}{\rho_{705}} - 1
# $$
#
# Because we're not doing any averaging, all we have to do is grab the bands from our dataset and follow the equation. We'll use the closest bands that the SFREFL suite has to 800 and 705 nm.

# +
rhos_800 = land_only.rhos.sel(wavelength_3d=800, method='nearest')
rhos_705 = land_only.rhos.sel(wavelength_3d=705, method='nearest')

cire = (rhos_800 / rhos_705) - 1
# -

# We can compare these maps side by side to see similarities and differences in the patterns of each VI.

# +
# NOTE: Lat/Lon in the hover shows as NaN, why?
plots = [cire.hvplot.quadmesh(x='longitude', y='latitude', crs=ccrs.PlateCarree(), 
                             clim=(0, 6), tiles='CartoLight', title="CIRE, July 1st, 2024", project=True, 
                             cmap="RdYlGn"),
         pace_ndvi.hvplot.quadmesh(x='longitude', y='latitude', crs=ccrs.PlateCarree(), 
                                   clim=(0,1.0), tiles='CartoLight', 
                                   title="NDVI, July 1st, 2024", project=True, cmap="RdYlGn")]

grid = pn.GridSpec()
for i, plot in enumerate(plots):
    grid[i//2, i%2] = plot

grid.servable()
# -

# Comparing these two plots, we can see some similarities and differences. Generally, the patterns of high and low values fall in the same places - this is because NDVI is essentially measuring the amount of green vegetation, and CIRE is measuring the amount of green pigment in plants. However, CIRE also has a higher dynamic range than NDVI does. For one, NDVI saturates as vegetation density increases, so a wide range of ecosystems with varying amounts of green veegtation may have very similar NDVI values. On the other hand, CIRE is not as affected by the leaf area, and can instead hone in on the relative amount of chlorophyll pigment in a pixel rather than the amount of leaves. This is a major advantage of CIRE and other hyperspectral-enabled VIs like the Carotenoid Content Index (Car), enabling us to track specific biochemical shifts in plants that correspond states of photosynthetic/photoprotective ability and thus providing insight on their physiological condition. 
#
# If calculating these indices manually felt a little tedious, not to worry! PACE OCI provides 10 VIs in its LANDVI product suite - 6 are heritage indices, and the remaining 4 are narrowband pigment indices including CIRE. Read more about it in the ATBD (in review, will link when published)

results = earthaccess.search_data(
    short_name="PACE_OCI_L3M_LANDVI",
    granule_name = "*20240701*MO*0p1*"#"*20250117T044314*"
)
results[0]

paths = earthaccess.download(results, local_path="data")

datatree = open_datatree(paths[0])
datatree


# +
def single_vi(vi):
    return vi.hvplot.image("lon", "lat", tiles="CartoLight", project=True, tools=['hover'], 
                           frame_width=450, frame_height=250, cmap="magma", title=f"{vi.name}, July 2024 Monthly Average")

single_vi(datatree.mari)
# -

# [back to top](#Contents)
