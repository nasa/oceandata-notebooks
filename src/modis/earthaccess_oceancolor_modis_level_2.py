# # Accessing OB.DAAC Ocean Color Data With earthaccess
#
# **Authors:** Guoqing Wang (NASA, GSFC); Ian Carroll (NASA, UMBC), Eli Holmes (NOAA), Anna Windle (NASA, GSFC)
#
# > **PREREQUISITES**
# >
# > This notebook has the following prerequisites:
# > - An **<a href="https://urs.earthdata.nasa.gov/" target="_blank">Earthdata Login</a>**
# >   account is required to access data from the NASA Earthdata system, including NASA ocean color data.
# > - There are no prerequisite notebooks for this module.
#
#
# ## Summary
# This tutorial demonstrates accessing and analyzing NASA ocean color data using Python from the NASA Ocean Biology Distributed Active Archive Center (OB.DAAC) archives. Currently, there are several ways to find and access ocean color data:
# 1. [NASA's Earthdata Search](https://search.earthdata.nasa.gov/search)
# 2. [NASA's CMR API](https://cmr.earthdata.nasa.gov/search/site/docs/search/api.html)
# 3. [OB.DAAC OPENDAP](https://oceandata.sci.gsfc.nasa.gov/opendap/)
# 4. [Ocean color file search](https://oceandata.sci.gsfc.nasa.gov/api/file_search_help)
#
# In this tutorial, we will focus on using `earthaccess` Python module to access MODIS Aqua ocean color data through NASA's Common Metadata Repository (CMR), a metadata system that catalogs Earth Science data and associated metadata records. The level 2 dataset of MODIS Aqua is one of the most popular datasets of OB.DAAC. Here we will use MODIS Aqua L2 Chlorophyll *a* data of the Chesapeake Bay as an example.
# The standard NASA ocean color Chlorophyll *a* algorithm is described in the [Algorithm Theoretical Basis Document (ATBD)](https://www.earthdata.nasa.gov/apt/documents/chlor-a/v1.0).
#
# ## Learning Objectives
#
# At the end of this notebok you will know:
# * How to find OB.DAAC ocean color data
# * How to download files using `earthaccess`
# * How to create a plot using `xarray`
#
# <a name="toc"></a>
# ## Contents
#
# 1. [Setup](#setup)
# 1. [NASA Earthdata Authentication](#auth)
# 1. [Search for Data](#search)
# 1. [Download Data](#download)
# 1. [Plot Data](#plot)
#
# <a name="setup"></a>
# ## 1. Setup
#
# We begin by importing all of the packages used in this notebook. If you have created an environment following the [guidance][tutorials] provided with this tutorial, then the imports will be successful.
#
# [tutorials]: https://oceancolor.gsfc.nasa.gov/resources/docs/tutorials

import os
import earthaccess
import netCDF4 as nc
import xarray as xr
import numpy as np
import matplotlib.pyplot as plt
import cartopy
import cartopy.crs as ccrs
from cartopy.mpl.ticker import LongitudeFormatter, LatitudeFormatter


# [Back to top](#top)
# <a name="auth"></a>
# ## 2. NASA Earthdata Authentication
#
# Next, we authenticate using our Earthdata Login
# credentials. Authentication is not needed to search publicaly
# available collections in Earthdata, but is always needed to access
# data. We can use the `login` method from the `earthaccess`
# package. This will create an authenticated session when we provide a
# valid Earthdata Login username and password. The `earthaccess`
# package will search for credentials defined by **environmental
# variables** or within a **.netrc** file saved in the home
# directory. If credentials are not found, an interactive prompt will
# allow you to input credentials.
#
# <div class="alert alert-info" role="alert">
# The <code>persist=True</code> argument ensures any discovered credentials are
# stored in a <code>.netrc</code> file, so the argument is not necessary (but
# it's also harmless) for subsequent calls to <code>earthaccess.login</code>.
# </div>

auth = earthaccess.login(persist=True)

# [Back to top](#top)
# <a name="search"></a>
# ## 3. Search for Data
#
# MODIS-Aqua level 1 - level 4 ocean color data products are hosted by the OB.DAAC. In this example, we will use the standard Chlorophyll *a* data from level 2 ocean color files. To find data we will use the `earthaccess` Python library to search on NASA's CMR API.
#
# `earthaccess.search_datasets` is used to search for NASA data collections. Various search parameters can be used to search collections and granules using metadata attributes. See more details [here](https://github.com/nsidc/earthaccess/blob/main/notebooks/Demo.ipynb). Below, CMR Catalog are queried to find collections with **'ocean color'** keyword in them, managed by **'OBDAAC'**. The returned response can be used to retrieve the `ShortName` and `concept-id` for each dataset.

results = earthaccess.search_datasets(
    keyword = 'ocean color',
    daac = "OBDAAC",
)

# The `umm` field has information such as short name and abstract.

for x in results[0:10]:
    print(x['umm']['ShortName'])

# We are interested in the `MODISA_L2_OC` dataset.

[x['umm']['Abstract'] for x in results if x['umm']['ShortName']=='MODISA_L2_OC']

# We can use spatial and temporal arguments to search for granules covering Chesapeake Bay during the time frame of Oct 15 - 23, 2020. We can also add the cloud_cover parameter to filter out granules with too much cloud coverage. 
# cloud_cover = (0, 50) # max 50% of cloud coverage

date_range = ("2020-10-15", "2020-10-23")
bbox = (-76.75,36.97,-75.74,39.01)
results = earthaccess.search_data(
    short_name = 'MODISA_L2_OC',
    temporal = date_range,
    bounding_box = bbox,
    cloud_cover = (0, 50)
)

# Now we can print some info about these granules using the built-in methods
data_links = [{'links': g.data_links(), 'size (MB):': g.size()} for g in results[0:3]]
data_links

# preview the data granules
results[0]

# preview more information
results[0:1]

# [Back to top](#top)
# <a name="download"></a>
# ## 4. Download Data
#
# Since the data are not cloud-hosted, we need to download. This will download the data in a folder called 'data' in your working directory. 

# download the first file granule
files = earthaccess.download(results[0], "data")

# [Back to top](#top)
# <a name="plot"></a>
# ## 5. Plot Data
#

# + active=""
# TODO: clean this up a little

# +
filename = 'data/AQUA_MODIS.20201016T174500.L2.OC.nc'
ds = xr.open_dataset(filename)

ds_geo = xr.open_dataset(filename, group='geophysical_data')['chlor_a']

ds_nav = xr.open_dataset(filename, group='navigation_data')
ds_nav = ds_nav.set_coords(("longitude", "latitude"))
ds_nav = ds_nav.rename({"pixel_control_points": "pixels_per_line"})

dataset = xr.merge((ds_geo, ds_nav.coords))

dataset['log10_chlor_a'] = np.log10(dataset["chlor_a"])
dataset

# + active=""
# TODO: change colorbar label to be log chl 
# -

p = dataset['log10_chlor_a'].plot(aspect=2, size=4,
                        x="longitude", y="latitude",
                        cmap = 'jet', vmin=-2, vmax=1.3)

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

plt.title(ds.time_coverage_start)
# -

# <div class="alert alert-info" role="alert">
# <p>You have completed the notebook MODIS Aqua L2 data access. </p>
# </div>


