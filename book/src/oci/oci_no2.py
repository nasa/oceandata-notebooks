# ---
# jupyter:
#   jupytext:
#     cell_metadata_filter: all,-trusted
#     notebook_metadata_filter: -all,jupytext,language_info.name
#     text_representation:
#       extension: .py
#       format_name: light
#       format_version: '1.5'
#       jupytext_version: 1.16.0
#   language_info:
#     name: python
# ---

# # Exploring nitrogen dioxide (NO$_\mathrm{2}$) data from OCI 
#
# **Authors:** Zachary Fasnacht (NASA, SSAI), Anna Windle (NASA, SSAI)
#
# <div class="alert alert-success" role="alert">
#
# The following notebooks are **prerequisites** for this tutorial.
#
# - 
#
# </div>
#
# ## Summary
#
# This tutorial describes how to access and download nitrogen dioxide (NO$_\mathrm{2}$) data products developed from PACE OCI data. More information on how these products were created can be found [in this manuscript preprint][paper] and in this [presentation][pres]. 
#
# [paper]:[file:///Users/awindled/Downloads/pace_paper.pdf]
# [pres]:[https://pace.oceansciences.org/docs/2025_01_30-Fasnacht_PACE_No2_Applications.pdf]
#
# ## Learning Objectives
#
# At the end of this notebook you will know:
#
# - How to access and download PACE NO$_\mathrm{2}$ data through the NASA Aura Validation Data Center
# - How to open those data using `xarray's` datatree function
# - How to plot NO$_\mathrm{2}$ vertical column retrievals
#
# ## Contents
#
# 1. [Setup](#1.-Setup)
# 2. [Download NO$_\mathrm{2}$ Data](#2.-Download-NO$_\mathrm{2}$-Data)
# 3. [Style Notes](#3.-Style-Notes)

# ## 1. Setup
#
# Begin by importing all of the packages used in this notebook. If your kernel uses an environment defined following the guidance on the [tutorials] page, then the imports will be successful.
#
# [tutorials]: https://oceancolor.gsfc.nasa.gov/resources/docs/tutorials/

import subprocess
import xarray as xr
from xarray.backends.api import open_datatree
import cartopy
import cartopy.crs as ccrs
import cartopy.feature as cfeature
import matplotlib.colors

# [back to top](#Contents)

# ## 2. Download NO$_\mathrm{2}$ Data
#
# The NO$_\mathrm{2}$ products have been made available at
# [NASA’s Aura Validation Data Center
# (AVDC)][aura]. We will need to manually download files from this site and read them in using `xarray`.
#
# [aura]: https://avdc.gsfc.nasa.gov/pub/tmp/PACE_NO2/
#
# For this exercise, we will download the file named 'PACE_NO2_Gridded_NAmerica_2024m0501.nc' using wget. Running this cell should save the file in the directory you're working in. 
#
# </div>

# [back to top](#Contents)

# ## 2. Read in data using `xarray` and plot
#
# We are downloading the data using the Python modules `subprocess` and `wget`. `subprocess` enables the execution of `wget`, which is a command-line utility for retrieving files from web serviers using https protocols. Here we are telling it to download a file from a publically hosted url. 

# +
url = "https://avdc.gsfc.nasa.gov/pub/tmp/PACE_NO2/NO2_L3_Gridded_NAmerica/PACE_NO2_Gridded_NAmerica_2024m0401.nc"
filename = "PACE_NO2_Gridded_NAmerica_2024m0401.nc"
subprocess.run(["wget", url, "-O", filename], stderr=subprocess.DEVNULL)

dat = open_datatree(filename)
dat = xr.merge(dat.to_dict().values())
#dat = dat.set_coords(("longitude", "latitude"))
dat = dat.swap_dims({"nlat":"latitude", "nlon":"longitude"})
dat
# -

# If you expand the 'nitrogen_dioxide_total_vertical_column' variable, you'll see that it is a 2D variable consisting of total vertical column NO$_\mathrm{2}$ measurements with units of molecules cm$^\mathrm{-2}$. 
# Let's plot it!

# +
fig, ax = plt.subplots(figsize=(8,6), subplot_kw={"projection": ccrs.PlateCarree()})

ax.gridlines(draw_labels={"left": "y", "bottom": "x"}, linewidth=0.25)
ax.coastlines(linewidth=0.5)
ax.add_feature(cfeature.BORDERS, linewidth=0.5)

cmap = matplotlib.colors.LinearSegmentedColormap.from_list("", ["lightgrey","cyan","yellow","orange","red","darkred"])

dat.nitrogen_dioxide_total_vertical_column.T.plot(
    vmin=3e15, vmax=10e15, cmap=cmap)

plt.show()
# -

# Let's zoom in to Los Angeles, California. 

# +
fig, ax = plt.subplots(figsize=(8,6), subplot_kw={"projection": ccrs.PlateCarree()})

ax.gridlines(draw_labels={"left": "y", "bottom": "x"}, linewidth=0.25)
ax.coastlines(linewidth=0.5)
ax.add_feature(cfeature.BORDERS, linewidth=0.5)

cmap = matplotlib.colors.LinearSegmentedColormap.from_list("", ["lightgrey","cyan","yellow","orange","red","darkred"])

dat.nitrogen_dioxide_total_vertical_column.T.plot(
    vmin=3e15, vmax=10e15, cmap=cmap)

ax.set_extent([-125,-110,30,40])
plt.show()
# -

# ## 3. 
#
# interactive plot?
# time series? 

# [back to top](#Contents)
#
# <div class="alert alert-info" role="alert">
#
# You have completed the notebook on ... suggest what's next. And don't add an emptyr cell after this one.
#
# </div>
