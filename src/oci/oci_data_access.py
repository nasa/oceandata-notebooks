# ---
# jupyter:
#   jupytext:
#     text_representation:
#       extension: .py
#       format_name: light
#       format_version: '1.5'
#       jupytext_version: 1.16.1
#   kernelspec:
#     display_name: Python 3 (ipykernel)
#     language: python
#     name: python3
# ---

# # Access Data from the Ocean Color Instrument (OCI)
#
# **Authors:** Anna Windle (NASA, SSAI), Ian Carroll (NASA, UMBC), Carina Poulin (NASA, SSAI)
#
# > **PREREQUISITES**
# >
# > This notebook has the following prerequisites:
# > - An **<a href="https://urs.earthdata.nasa.gov/" target="_blank">Earthdata Login</a>**
# >   account is required to access data from the NASA Earthdata system, including NASA ocean color data.
# > - There are no prerequisite notebooks for this module.
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
# In short, `earthaccess` helps **authenticate** with Earthdata Login,
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
# 1. The notebook is running on a remote host, but it does not have direct access to the NASA Earthdata Cloud. For instance, you are running in [GitHub Codespaces][codespaces].
# 1. The notebook is running on a remote host that does have direct access to the NASA Earthdata Cloud. At this time, we cannot provide a "for instance" which is available to everyone.
#
# ## Learning Objectives
#
# At the end of this notebook you will know:
#
# * How to store your NASA Earthdata Login credentials with `earthaccess`
# * How to use `earthaccess` to search for OCI data using search filters
# * How to download OCI data, but only when you need to
#
# <a name="toc"></a>
# ## Contents
#
# 1. [Setup](#setup)
# 1. [NASA Earthdata Authentication](#auth)
# 1. [Search for Data](#search)
# 1. [Download Data](#download)
#
# <a name="setup"></a>
# ## 1. Setup
#
# We begin by importing the only package used in this notebook. If you
# have created an environment following the [guidance][tutorials]
# provided with this tutorial, then the import will be successful.
#
# [codespaces]: https://github.blog/changelog/2022-11-09-using-codespaces-with-jupyterlab-public-beta/
# [tutorials]: https://oceancolor.gsfc.nasa.gov/resources/docs/tutorials
# [edcloud]: https://www.earthdata.nasa.gov/eosdis/cloud-evolution
# [earthaccess-docs]: https://earthaccess.readthedocs.io/en/stable/
# [cmr]: https://cmr.earthdata.nasa.gov/search/site/docs/search/api.html
# [conda]: https://anaconda.org/conda-forge/earthaccess
# [pypi]: https://pypi.org/project/earthaccess/

import earthaccess

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
# Collections on NASA Earthdata are discovered with the
# `search_datasets` function, which accepts an `instrument` filter as an
# easy way to get started. Each of the items in the list of
# collections returned has a "short-name".

results = earthaccess.search_datasets(instrument="oci")

for item in results:
    summary = item.summary()
    print(summary["short-name"])

# Next, we use the `search_data` function to find granules within a
# collection. Let's use the `short_name` for the PACE/OCI Level-2
# quick-look product for apparent optical properties (although you can
# search for granules accross collections too).
#
# <div class="alert alert-info" role="alert">
# The short name can also be found on <a href="https://search.earthdata.nasa.gov/search?fi=SPEXone!HARP2!OCI&fpb0=Space-based%20Platforms" target="_blank"> Eartdata Search</a>, directly under the collection name, after clicking on the "i" button for a collection in any search result.
# </div>
#
# The `count` argument limits the number of granules returned and stored in the `results` list.

results = earthaccess.search_data(
    short_name="PACE_OCI_L2_AOP_NRT",
    count=1,
)

# We can refine our search by passing more parameters that describe
# the spatiotemporal domain of our use case. Here, we use the
# `temporal` parameter to request a date range and the `bounding_box`
# parameter to request granules that intersect with a bounding box. We
# can even provide a `cloud_cover` threshold to limit files that have
# a lower percetnage of cloud cover. We do not provide a `count`, so
# we'll get all granules that satisfy the constraints.

tspan = ("2024-04-01", "2024-04-16")
bbox = (-76.75, 36.97, -75.74, 39.01)
clouds = (0, 50)

results = earthaccess.search_data(
    short_name="PACE_OCI_L2_AOP_NRT",
    temporal=tspan,
    bounding_box=bbox,
    cloud_cover=clouds,
)

# Displaying a single result shows a direct download link: try it! The
# link will download the granule to your local machine, which may or
# may not be what you want to do. Even if you are running the notebook
# on a remote host, this download link will open a new browser tab or
# window and offer to save a file to your local machine. If you are
# running the notebook locally, this may be of use. However, in the
# next section we'll see how to download all the results with one
# command.

results[0]

# [Back to top](#top)
# <a name="download"></a>
# ## 4. Download Data
#
# First, let's understand what the alternative is to downloading
# granules. The `earthaccess.open` function accepts the list of results from
# `earthaccess.search_data` and returns a list of file-like objects,
# but no actual files are transferred.

paths = earthaccess.open(results)

# The file-like objects held in `paths` can each be read like a normal
# file. Here we load the first few bytes without any specialized
# reader.

with paths[0] as file:
    line = file.readline().strip()
line

# Of course that doesn't mean anything (does it? 😉), because this is
# a binary file that needs a reader which understands the file format.
#
# The `earthaccess.open` function is used when you want to directly read
# a bytes from a remote filesystem, but not download a whole file. When
# running code on a host with direct access to the NASA Earthdata
# Cloud, you don't need to download the data and `earthaccess.open`
# is the way to go.
#
# Now, let's look at the `earthaccess.download` function, which is used
# to copy files onto a filesystem local to the machine executing the
# code. For this function, provide the output of
# `earthaccess.search_data` along with a directory where `earthaccess`
# will store downloaded granules.
#
# Even if you only want to read a slice of the data, and downloading
# seems unncessary, if you use `earthaccess.open` while not running on
# a remote host with direct access to the NASA Earthdata Cloud,
# performance will be very poor. This is not a problem with "the
# cloud" or with `earthaccess`, it has to do with the data format and
# may soon be resolved.
#
# Let's continue to downloading the list of granules!

paths = earthaccess.download(results, "L2_AOP")

# The `paths` list now contains paths to actual files on the local
# filesystem.

paths

# <div class="alert alert-block alert-warning">
# Anywhere in any of <a href="https://oceancolor.gsfc.nasa.gov/resources/docs/tutorials/">these notebooks</a> where <pre>paths = earthaccess.open(...)</pre> is used to read data directly from the NASA Earthdata Cloud, you need to substitute <pre>paths = earthaccess.download(..., local_path)</pre> before running the notebook on a local host or a remote host that does not have direct access to the NASA Earthdata Cloud.
# </div>
# <div class="alert alert-info" role="alert">
# <p>You have completed the notebook on downloading and opening datasets. We now suggest starting the notebook on File Structure at Three Processing Levels.</p>
# </div>
