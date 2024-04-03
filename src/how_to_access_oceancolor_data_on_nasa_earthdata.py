# ---
# jupyter:
#   jupytext:
#     text_representation:
#       extension: .py
#       format_name: light
#       format_version: '1.5'
#       jupytext_version: 1.16.0
#   kernelspec:
#     display_name: Python 3.10 (conda)
#     language: python
#     name: python3
# ---

# + [markdown] id="thB-pNE2YUT7"
# # Accessing OBDAAC Ocean Color Data With Earthaccess
# -

# testing git push

# + [markdown] id="EMTS0oIRY3dj"
# ### Overview
# This article demonstrates accessing and analyzing NASA ocean color data using Python from the NASA Ocean Biology Distributed Active Archive Center (OBDAAC) archives. Currently, there are several ways to find and access ocean color data:
# 1. [NASA's Earthdata Search](https://search.earthdata.nasa.gov/search)
# 2. [NASA's CMR API](https://cmr.earthdata.nasa.gov/search/site/docs/search/api.html)
# 3. [OB.DAAC OPENDAP](https://oceandata.sci.gsfc.nasa.gov/opendap/)
# 4. [Ocean color file search](https://oceandata.sci.gsfc.nasa.gov/api/file_search_help)
#
# In this tutorial, we will focus on using `Earthaccess` python module to access ocean color data through NASA's Common Metadata Repository (CMR), a metadata system that catalogs Earth Science data and associated metadata records.
#
# ## Dataset
#
# The level 2 dataset of MODIS Aqua is one of the most popular datasets of OBDAAC. Here we will use MODIS-Aqua L2 *Chlorophyll a* data at Chesapeake Bay as an example to show how to access, download, and visualize the ocean color/*Chlorophyll a* data in python using the `Earthaccess` python package through NASA Earthdata CMR API.
#
# A demo of Earthaccess can be accessed [here](https://github.com/nsidc/earthaccess/blob/main/notebooks/Demo.ipynb).
#
# The standard NASA ocean color *Chlorophyll a* algorithm is described in the [Algorithm Theoretical Basis Document (ATBD)](https://www.earthdata.nasa.gov/apt/documents/chlor-a/v1.0).
#
#
# ## Requirements
#
#
# 1. **Earthdata Login**. An Earthdata Login account is required to access data from the NASA Earthdata system, including NASA ocean color data. To obtain access, please visit https://urs.earthdata.nasa.gov to register and manage your Earthdata Login account. Creating this account is free and only takes a moment to set up.
# 2. **Additional Requirements**: This tutorial requires the following Python modules installed in your system: `earthaccess`. To install the necessary Python modules, you can run:
#
# > `!pip install earthaccess`

# + id="9vivpFtxIt1O"
# # !pip install earthaccess xarray netCDF4 cartopy
# -
import os
import earthaccess
import netCDF4 as nc
import xarray as xr
import numpy as np
import matplotlib.pyplot as plt
import cartopy
import cartopy.crs as ccrs
from cartopy.mpl.ticker import LongitudeFormatter, LatitudeFormatter


# ## **1. Authentication**
#
# Access to NASA ocean color data requires NASA Earthdata authentication. Here, we authenticate our Earthdata Login (EDL) information credentials stored in a .netrc file using the earthaccess python library: earthaccess.login(). This function will prompt for your NASA Earthdata username and password to create a .netrc file if one does not exist. It then uses your account information for authentication purposes.

earthaccess.login(persist=True)

# ## **2. Search for MODIS-Aqua Collections**
#
# MODIS-Aqua level 1 - level 4 ocean color data products are hosted by the OBDAAC. In this example, we will use the standard *Chlorophyll a* data from level 2 ocean color files. To find data we will use the `earthaccess` Python library to search on NASA's CMR API.
#
# `collection_query` from `earthaccess` is used to search for the NASA data collections. Various query parameters can be used to search collections and granules using attributes associated to them in the metadata. See more details [here](https://github.com/nsidc/earthaccess/blob/main/notebooks/Demo.ipynb). Below, CMR Catalog are queried to find collections with **ocean color** keyword in them, managed by **OBDAAC**. The returned response can be used to retrieve the `concept-id` for each dataset.

# +
Query = earthaccess.collection_query().keyword('ocean color').bounding_box(-76.75,36.97,-75.74,39.01)

print(f'Collections found: {Query.hits()}')

# filtering what UMM fields to print, to see the full record we omit the fields filters
# meta is always included as
collections = Query.fields(['ShortName','Abstract']).get(3)
# Inspect 3 results printing just the ShortName and Abstract
collections[0:3]

# +
# We can now search for collections hosted by OBDAAC.
Query = earthaccess.collection_query().daac("OBDAAC")

print(f'Collections found: {Query.hits()}')
collections = Query.fields(['ShortName']).get(20)
# Printing 3 collections
collections[0:3]
# -

# Printing the concept-id for the first 10 collections
[collection.concept_id() for collection in collections[0:10]]

# ## **3. Search for granules based on spatiotemporal criteria**
# In this example we're querying for grnaules from MODIS-Aqua Level 2 Ocean color dataset (with the `short_name` of `"MODISA_L2_OC"`).
#
# Using spatial and temporal arguments to search for granules covering Chesapeake Bay during the time frame of Oct 15 - 23, 2010.

Query = earthaccess.granule_query().short_name("MODISA_L2_OC").temporal("2010-10-15", "2010-10-23").bounding_box(-76.75,36.97,-75.74,39.01)
# check the number of granules found
print(f"Granules found: {Query.hits()}")

# +
# # the following is an example to use the cloud_cover parameter to filter out granules with too much cloud coverage
# Query = earthaccess.granule_query().short_name("MODISA_L2_OC").temporal("2010-10-15", "2010-10-23").bounding_box(-76.75,36.97,-75.74,39.01).cloud_cover(0, 20) # max 20% of cloud coverage
# -

# Now we can print some info about these granules using the built-in methods
granules = Query.get(4)
data_links = [{'links': g.data_links(), 'size (MB):': g.size()} for g in granules]
data_links

# preview the data granules
granules

# To check whether this granule belongs to a cloud-based collection
granules[0].cloud_hosted

# ## **4. Download, and visulize data**
#
# This section demonstrates the downloading and visualization of *Chlorophyll a* map.
# To find the cloud-free granules, the [L1/L2 browser](https://oceancolor.gsfc.nasa.gov/cgi/browse.pl?sen=amod) on [oceancolor website](https://oceancolor.gsfc.nasa.gov/) were used to take a quick look of the RGB image.

# download the cloud-free file
files = earthaccess.download(granules[3], "data")

# +
# Open the datasets with xarray
filename = '/content/data/AQUA_MODIS.20101017T181000.L2.OC.nc'
ds = xr.open_dataset(filename)
# Load attributes
ds_geo = xr.open_dataset(filename, group='geophysical_data')
ds_nav = xr.open_dataset(filename, group='navigation_data')

# Use .data_vars to find variable names
# ds['navigation_data'].data_vars
# ds['geophysical_data'].data_vars

# Read chlor_a, latitude, and longitude data from their respective groups
lat = ds_nav.latitude
lon = ds_nav.longitude
chlor_a = ds_geo.chlor_a
log_chlor_a = np.log10(chlor_a)

# +
# Plot Chlor_a data
fig = plt.figure(figsize=(10, 7))
map_projection = cartopy.crs.PlateCarree()
ax = plt.axes(projection=map_projection)

im = ax.pcolormesh(lon, lat,np.squeeze(log_chlor_a),cmap = 'jet', vmin=-2, vmax=1.3)
ax.coastlines()
ax.add_feature(cartopy.feature.STATES, linewidth=0.5)

ax.set_xticks(np.linspace(-85, -55, 5), crs=map_projection)
ax.set_yticks(np.linspace(26, 48, 5), crs=map_projection)
lon_formatter = LongitudeFormatter(zero_direction_label=True)
lat_formatter = LatitudeFormatter()
ax.xaxis.set_major_formatter(lon_formatter)
ax.yaxis.set_major_formatter(lat_formatter)

plt.colorbar(im, label='log10(Chlorophyll-a)')
plt.title(ds.time_coverage_start)
