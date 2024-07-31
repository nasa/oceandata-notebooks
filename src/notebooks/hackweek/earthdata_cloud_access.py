# ---
# jupyter:
#   kernelspec:
#     display_name: Python 3 (ipykernel)
#     language: python
#     name: python3
# ---

# # Orientation to Earthdata Cloud Access
#
# **Tutorial Lead:** Anna Windle (NASA, SSAI)
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
# In this example we will use the `earthaccess` package to search for
# OCI products on NASA Earthdata. The `earthaccess` package, published
# on the [Python Package Index][pypi] and [conda-forge][conda],
# facilitates discovery and use of all NASA Earth Science data
# products by providing an abstraction layer for NASA’s [Common
# Metadata Repository (CMR) API][cmr] and by simplifying requests to
# NASA's [Earthdata Cloud][edcloud]. Searching for data is more
# approachable using `earthaccess` than low-level HTTP requests, and
# the same goes for S3 requests.
#
# In short, `earthaccess` helps **authenticate** with an Earthdata Login,
# makes **search** easier, and provides a stream-lined way to **load
# data** into `xarray` containers. For more on `earthaccess`, visit
# the [documentation][earthaccess-docs] site. Be aware that
# `earthaccess` is under active development.
#
# To understand the discussions below on downloading and opening data,
# we need to clearly understand **where our notebook is
# running**. There are three cases to distinguish:
#
# 1. The notebook is running on the local host. For instance, you started a Jupyter server on your laptop.
# 1. The notebook is running on a remote host, but it does not have direct access to the AWS us-west-2 region. For instance, you are running in [GitHub Codespaces][codespaces], which is run on Microsoft Azure. 
# 1. The notebook is running on a remote host that does have direct access to the NASA Earthdata Cloud (AWS us-west-2 region). This is the case for the PACE Hackweek. 
#
# [pypi]: https://pypi.org/
# [conda]: https://oceancolor.gsfc.nasa.gov/resources/docs/tutorials/notebooks/oci-data-access/
# [cmr]: https://www.earthdata.nasa.gov/eosdis/science-system-description/eosdis-components/cmr
# [edcloud]: https://www.earthdata.nasa.gov/eosdis/cloud-evolution
# [earthaccess-docs]: https://earthaccess.readthedocs.io/en/latest/
# [codespaces]: https://github.com/features/codespaces
#
# ## Learning Objectives
#
# At the end of this notebook you will know:
#
# * How to store your NASA Earthdata Login credentials with `earthaccess`
# * How to use `earthaccess` to search for OCI data using search filters
# * How to download OCI data, but only when you need to
#
# ## Contents
#
# 1. [Setup](#1.-Setup)
# 2. [NASA Earthdata Authentication](#2.-NASA-Earthdata-Authentication)
# 3. [Search for Data](#3.-Search-for-Data)
# 4. [Open Data](#4.-Open-Data)
# 5. [Download Data](#5.-Download-Data)

# ## 1. Setup
#
# We begin by importing the packages used in this notebook.

import earthaccess
import xarray as xr
from xarray.backends.api import open_datatree

# The last import provides a preview of the `DataTree` object. Once it is fully integrated into XArray,
# the additional import won't be needed, as the function will be available as `xr.open_datree`.

# [back to top](#Contents)

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
#     
# The `persist=True` argument ensures any discovered credentials are
# stored in a `.netrc` file, so the argument is not necessary (but
# it's also harmless) for subsequent calls to `earthaccess.login`.
#
# </div>

auth = earthaccess.login(persist=True)

# [back to top](#Contents)

# ## 3. Search for Data
#
# Collections on NASA Earthdata are discovered with the
# `search_datasets` function, which accepts an `instrument` filter as an
# easy way to get started. Each of the items in the list of
# collections returned has a "short-name".

results = earthaccess.search_datasets(instrument="oci")

for item in results:
    summary = item.summary()
    print(summary["short-name"])

# <div class="alert alert-info" role="alert">
# The short name can also be found on <a href="https://search.earthdata.nasa.gov/search?fi=SPEXone!HARP2!OCI" target="_blank"> Eartdata Search</a>, directly under the collection name, after clicking on the "i" button for a collection in any search result.
# </div>
#
# Next, we use the `search_data` function to find granules within a
# collection. Let's use the `short_name` for the PACE/OCI Level-2 near real time (NRT), product for biogeochemical properties (although you can
# search for granules accross collections too).
#
#
#
# The `count` argument limits the number of granules whose metadata is returned and stored in the `results` list.

results = earthaccess.search_data(
    short_name="PACE_OCI_L2_BGC_NRT",
    count=1,
)

results

# We can refine our search by passing more parameters that describe
# the spatiotemporal domain of our use case. Here, we use the
# `temporal` parameter to request a date range and the `bounding_box`
# parameter to request granules that intersect with a bounding box. We
# can even provide a `cloud_cover` threshold to limit files that have
# a lower percetnage of cloud cover. We do not provide a `count`, so
# we'll get all granules that satisfy the constraints.

tspan = ("2024-07-01", "2024-07-31")
bbox = (-76.75, 36.97, -75.74, 39.01)
clouds = (0, 50)

results = earthaccess.search_data(
    short_name="PACE_OCI_L2_BGC_NRT",
    temporal=tspan,
    bounding_box=bbox,
    cloud_cover=clouds,
)

# Displaying results shows the direct download link: try it! The
# link will download one granule to your local machine, which may or
# may not be what you want to do. Even if you are running the notebook
# on a remote host, this download link will open a new browser tab or
# window and offer to save a file to your local machine. If you are
# running the notebook locally, this may be of use. However, in the
# next section we'll see how to download all the results with one
# command.

results[0]

results[1]

results[2]

# [back to top](#Contents)

# ## 4. Open Data
#
# Let's go ahead and open a couple granules using `xarray`. The `earthaccess.open` function is used when you want to directly read
# a bytes from a remote filesystem, but not download a whole file. When
# running code on a host with direct access to the NASA Earthdata
# Cloud, you don't need to download the data and `earthaccess.open`
# is the way to go.

paths = earthaccess.open(results)

# The `paths` list contains references to files on a remote filesystem.

paths

dataset = xr.open_dataset(paths[0])
dataset

# Notice that this `xarray.Dataset` has nothing but "Attributes". The NetCDF data model includes multi-group hierarchies within a single file, where each group maps to an `xarray.Dataset`. The whole file maps to a `DataTree`, which we will only use lightly because the implementation in XArray remains under development.

datatree = open_datatree(paths[0])
datatree

dataset = xr.merge(datatree.to_dict().values())
dataset

# Let's do a quick plot of the `chlor_a` variable. You'll do more plotting in the Multidimensional Data Visualization tutorial.

artist = dataset["chlor_a"].plot(vmax=5)

# [back to top](#Contents)

# ## 5. Download Data
#
# Let's go ahead and download a couple granules. 

# Let's look at the `earthaccess.download` function, which is used
# to copy files onto a filesystem local to the machine executing the
# code. For this function, provide the output of
# `earthaccess.search_data` along with a directory where `earthaccess` will store downloaded granules.
#
# Even if you only want to read a slice of the data, and downloading
# seems unncessary, if you use `earthaccess.open` while not running on a remote host with direct access to the NASA Earthdata Cloud,
# performance will be very poor. This is not a problem with "the
# cloud" or with `earthaccess`, it has to do with the data format and may soon be resolved.
#

results = earthaccess.search_data(
    short_name="PACE_OCI_L2_BGC_NRT",
    temporal=tspan,
    bounding_box=bbox,
    cloud_cover=clouds,
)

# The `paths` list now contains paths to actual files on the local
# filesystem.

paths = earthaccess.download(results, local_path="data")
paths

# We can open up that locally saved file using `xarray` as well.

open_datatree(paths[0])

# [back to top](#Contents)

Lessons learned?

# + active=""
# present on file structure? difference btwn short names and what will have coordinates/what not. L3- show how to use granule name filter, and spatial (point, line, etc.) filter.
#
