# # Accessing OBDAAC Ocean Color Data With earthaccess
#
# **Authors:** Guoqing Wang (NASA, GSFC); Ian Carroll (NASA, UMBC), Eli Holmes (NOAA)
#
# ### Overview
# This tutorial demonstrates accessing and analyzing NASA ocean color data using Python from the NASA Ocean Biology Distributed Active Archive Center (OBDAAC) archives. Currently, there are several ways to find and access ocean color data:
# 1. [NASA's Earthdata Search](https://search.earthdata.nasa.gov/search)
# 2. [NASA's CMR API](https://cmr.earthdata.nasa.gov/search/site/docs/search/api.html)
# 3. [OB.DAAC OPENDAP](https://oceandata.sci.gsfc.nasa.gov/opendap/)
# 4. [Ocean color file search](https://oceandata.sci.gsfc.nasa.gov/api/file_search_help)
#
# In this tutorial, we will focus on using `earthaccess` Python module to access ocean color data through NASA's Common Metadata Repository (CMR), a metadata system that catalogs Earth Science data and associated metadata records.
#
# ## Dataset
#
# The level 2 dataset of MODIS Aqua is one of the most popular datasets of OBDAAC. Here we will use MODIS-Aqua L2 *Chlorophyll a* data at Chesapeake Bay as an example.
# The standard NASA ocean color *Chlorophyll a* algorithm is described in the [Algorithm Theoretical Basis Document (ATBD)](https://www.earthdata.nasa.gov/apt/documents/chlor-a/v1.0).
#
# ## Learning Objectives
#
# At the end of this notebok you will know:
# * How to find OBDAAC ocean color data
# * How to download files using `earthdata`
# * How to create a plot
#
# ## Requirements
#
# 1. **Earthdata Login**. An Earthdata Login account is required to access data from the NASA Earthdata system, including NASA ocean color data. To obtain access, please visit https://urs.earthdata.nasa.gov to register.
# 2. **Additional Requirements**: This tutorial requires the following Python modules installed in your system: 
#
# > `!pip install earthaccess xarray netCDF4 cartopy`
#
# ## **Import packages**

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
# Access to NASA ocean color data requires NASA Earthdata authentication. Here, we authenticate our Earthdata Login (EDL) information credentials stored in a .netrc file using the `earthaccess` Python library: `earthaccess.login()`. This function will prompt for your NASA Earthdata username and password to create a .netrc file if one does not exist. It then uses your account information for authentication purposes.

earthaccess.login(persist=True)

# ## **2. Search for MODIS-Aqua Collections**
#
# MODIS-Aqua level 1 - level 4 ocean color data products are hosted by the OBDAAC. In this example, we will use the standard *Chlorophyll a* data from level 2 ocean color files. To find data we will use the `earthaccess` Python library to search on NASA's CMR API.
#
# `search_datasets` from `earthaccess` is used to search for the NASA data collections. Various search parameters can be used to search collections and granules using attributes associated to them in the metadata. See more details [here](https://github.com/nsidc/earthaccess/blob/main/notebooks/Demo.ipynb). Below, CMR Catalog are queried to find collections with **ocean color** keyword in them, managed by **OBDAAC**. The returned response can be used to retrieve the `ShortName` and `concept-id` for each dataset.

# (xmin=-73.5, ymin=33.5, xmax=-43.5, ymax=43.5)
bbox = (-76.75,36.97,-75.74,39.01)
results = earthaccess.search_datasets(
    keyword = 'ocean color',
    bounding_box = bbox,
    daac = "OBDAAC",
)

# The `umm` field has information such as short name and abstract.

for x in results[0:4]:
    print(x['umm']['ShortName'])

# We are interested in the `MODISA_L2_OC` dataset.

[x['umm']['Abstract'] for x in results if x['umm']['ShortName']=='MODISA_L2_OC']

# ## **3. Search for granules based on spatiotemporal criteria**
# In this example we're querying for grnaules from MODIS-Aqua Level 2 Ocean color dataset (with the `short_name` of `"MODISA_L2_OC"`).
#
# Using spatial and temporal arguments to search for granules covering Chesapeake Bay during the time frame of Oct 15 - 23, 2010.

date_range = ("2010-10-15", "2010-10-23")
# (xmin=-73.5, ymin=33.5, xmax=-43.5, ymax=43.5)
bbox = (-76.75,36.97,-75.74,39.01)
results = earthaccess.search_data(
    short_name = 'MODISA_L2_OC',
    temporal = date_range,
    bounding_box = bbox,
)

# +
# we can add the cloud_cover parameter to filter out granules with too much cloud coverage
# cloud_cover = (0, 20) # max 20% of cloud coverage
# -

# Now we can print some info about these granules using the built-in methods
data_links = [{'links': g.data_links(), 'size (MB):': g.size()} for g in results[0:3]]
data_links

# preview the data granules
results[0]

# preview more information
results[0:1]

# ## **4. Download, and visualize data**
#
# This section demonstrates the downloading and visualization of *Chlorophyll a* map.
# To find the cloud-free granules, the [L1/L2 browser](https://oceancolor.gsfc.nasa.gov/cgi/browse.pl?sen=amod) on [oceancolor website](https://oceancolor.gsfc.nasa.gov/) were used to take a quick look of the RGB imagery.
#
# Since the data are not cloud-hosted, we need to download.

# download the cloud-free file
files = earthaccess.download(results[3], "data")

# Open the datasets with xarray
filename = 'data/AQUA_MODIS.20101017T181000.L2.OC.nc'
ds = xr.open_dataset(filename)
# Load chl-a
ds_geo = xr.open_dataset(filename, group='geophysical_data')['chlor_a']
# Load lat/lon
ds_nav = xr.open_dataset(filename, group='navigation_data')
ds_nav = ds_nav.set_coords(("longitude", "latitude"))
ds_nav = ds_nav.rename({"pixel_control_points": "pixels_per_line"})
# Merge
dataset = xr.merge((ds_geo, ds_nav.coords))
# Add log10 chl-a
dataset['log10_chlor_a'] = np.log10(dataset["chlor_a"])
dataset

# Plot the data.

dataset['log10_chlor_a'].plot(aspect=2, size=4, x="longitude", y="latitude", cmap = 'jet', vmin=-2, vmax=1.3);

# Add some decoration to the plot.

# +
fig = plt.figure(figsize=(10, 7))
map_projection = cartopy.crs.PlateCarree()
ax = plt.axes(projection=map_projection)

ax.coastlines()
ax.add_feature(cartopy.feature.STATES, linewidth=0.5)
ax.set_xticks(np.linspace(-85, -55, 5), crs=map_projection)
ax.set_yticks(np.linspace(26, 48, 5), crs=map_projection)
lon_formatter = LongitudeFormatter(zero_direction_label=True)
lat_formatter = LatitudeFormatter()
ax.xaxis.set_major_formatter(lon_formatter)
ax.yaxis.set_major_formatter(lat_formatter)
plot = dataset['log10_chlor_a'].plot(x="longitude", y="latitude", cmap="jet", vmin=-2, vmax=1.3, ax=ax)

plt.title(ds.time_coverage_start);
# -

# <div class="alert alert-info" role="alert">
# <p>You have completed the notebook on access of L2 data on ocean color at the OBDAAC.</p>
# </div>


