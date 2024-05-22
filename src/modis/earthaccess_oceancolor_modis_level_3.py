# # Accessing OBDAAC Level 3 Ocean Color Data With earthaccess
#
# **Authors:** Guoqing Wang (NASA, GSFC); Ian Carroll (NASA, UMBC), Eli Holmes (NOAA)
#
# This tutorial shows an example of reading and plotting MODIS AQUA level-3 ocean color datasets. You browse the Level 3 data here [https://oceancolor.gsfc.nasa.gov/l3](https://oceancolor.gsfc.nasa.gov/l3).
#

# ### Overview
#
# This tutorial demonstrates accessing and analyzing NASA ocean color data from the NASA Ocean Biology Distributed Active Archive Center (OBDAAC) archives. Currently, there are several ways to find and access ocean color data:
# 1. [NASA's Earthdata Search](https://search.earthdata.nasa.gov/search)
# 2. [NASA's CMR API](https://cmr.earthdata.nasa.gov/search/site/docs/search/api.html)
# 3. [OB.DAAC OPENDAP](https://oceandata.sci.gsfc.nasa.gov/opendap/)
# 4. [Ocean color file search](https://oceandata.sci.gsfc.nasa.gov/api/file_search_help)
#
# In this tutorial, we will focus on using `earthaccess` Python module to access ocean color data through NASA's Common Metadata Repository (CMR), a metadata system that catalogs Earth Science data and associated metadata records.
#
# ## Dataset
#
# The Level 3 datasets of MODIS Aqua include multiple types of temporally and spatially aggregated data. We will look at 8-day averaged and monthly averaged data at the 4km resolution. We will plot chlorophyll-a and Rrs(412) data.
#
# ## Requirements
#
# 1. **Earthdata Login**. An Earthdata Login account is required to access data from the NASA Earthdata system, including NASA ocean color data. To obtain access, please visit https://urs.earthdata.nasa.gov to register.
# 2. **Additional Requirements**: This tutorial requires the following Python modules installed in your system: 
#
# > `!pip install earthaccess`

import warnings
warnings.filterwarnings("ignore")

# +
from matplotlib import pyplot as plt
# from mpl_toolkits.basemap import Basemap
import numpy as np
import xarray as xr                   
import earthaccess

import cartopy
from cartopy.mpl.ticker import LongitudeFormatter, LatitudeFormatter
# -

# ## **1. Authentication**
#
# Access to NASA ocean color data requires NASA Earthdata authentication. Here, we authenticate our Earthdata Login (EDL) information credentials stored in a .netrc file using the `earthaccess` Python library: `earthaccess.login()`. This function will prompt for your NASA Earthdata username and password to create a .netrc file if one does not exist. It then uses your account information for authentication purposes.

earthaccess.login(persist=True)

# ## **2. Search**
#
# In this example, the image to be used is MODIS AQUA L3 8day averaged 4km chlorophyll image for Sep 13-20, 2016 and the January 2020 monthly average for Rrs(412) First we need to search for that data. These data are hosted by the OBDAAC. `search_datasets` from `earthaccess` is used to search for the NASA data collections. To do this search we need to know something about the data information, particularly that we are looking for `MODIS AQUA L3m`.

date_range = ("2016-09-20", "2016-09-20")
results = earthaccess.search_datasets(
    keyword = 'MODIS AQUA L3m',
    temporal = date_range,
    daac = "OBDAAC",
)

for x in results:
    print(x['umm']['ShortName'])

# You will want to go on to https://search.earthdata.nasa.gov/ and enter the short names to read about each data collection. We want to use the `MODISA_L3m_CHL` data collection for our first plot. We can get the files (granules) in that collection with `earthaccess.search_data()`.

results = earthaccess.search_data(
    short_name = 'MODISA_L3m_CHL',
    temporal = date_range,
    daac = "OBDAAC",
)

# We want the 4km files and the 8D (8-day averages) files.

results = [granule for granule in results if "4km" in granule.data_links()[0]]
len(results)

results = [granule for granule in results if "8D" in granule.data_links()[0]]
results

# ## **3. Download**
#
# We need to check if the data are cloud-hosted. If they are, we can load into memory directly without downloading. If they are not cloud-hosted, we need to download the data file.

results[0].cloud_hosted

# The data are not cloud-hosted so we download with `earthaccess.download()`. `earthaccess` will handle authentication for us.

filename = earthaccess.download(results, "data")

# The output is the filenames
filename

# ## **4. Read in the file**

ds = xr.open_dataset(filename[0])
ds

# ## **5. Plot**

ds['log10_chlor_a'] = np.log10(ds["chlor_a"])
ds['log10_chlor_a'].plot(x='lon', y='lat', cmap = 'jet', vmin=-2, vmax=1.3);
plot = plt.title(ds.time_coverage_start)

# We can add some decoration to the plot.

# +
fig = plt.figure(figsize=(10, 5))
map_projection = cartopy.crs.Robinson()
ax = plt.axes(projection=map_projection)
ax.coastlines()
ax.set_global()
plot = ds['log10_chlor_a'].plot(x='lon', y='lat', cmap = 'jet', vmin=-2, vmax=1.3, ax=ax, transform=cartopy.crs.PlateCarree())

plt.title(ds.time_coverage_start)
# -

# ## Repeat with another dataset
#
# Repeat these steps to plot the Oct 2020 Rrs(412) data. This is a monthly product.

date_range = ("2020-10-01", "2020-10-31")
results = earthaccess.search_data(
    short_name = 'MODISA_L3m_RRS',
    temporal = date_range,
    daac = "OBDAAC",
)

results = [granule for granule in results if "4km" in granule.data_links()[0]]
results = [granule for granule in results if ".MO." in granule.data_links()[0]]
results = [granule for granule in results if "Rrs_412" in granule.data_links()[0]]
results

# Download the dataset
filename = earthaccess.download(results, "data")

# **3. Read and plot monthly Rrs(412)**

# Open the datasets with xarray
ds = xr.open_dataset(filename[0])
ds['log10_rrs'] = np.log10(ds["Rrs_412"])

# Plot Rrs(412) with matplotlib and cartopy

# +
fig = plt.figure(figsize=(10, 5))
map_projection = cartopy.crs.Robinson()
ax = plt.axes(projection=map_projection)
ax.coastlines()
ax.set_global()
plot = ds['log10_rrs'].plot(x='lon', y='lat', cmap = 'jet', vmin=-3, vmax=-1, ax=ax, transform=cartopy.crs.PlateCarree())

plt.title(ds.time_coverage_start)
# -

# <div class="alert alert-info" role="alert">
# <p>You have completed the notebook on access of L3 data on ocean color at the OBDAAC.</p>
# </div>


