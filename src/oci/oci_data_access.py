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

# # Access OCI Data with `earthaccess`
#
# **Authors:** Anna Windle (NASA, SSAI), Ian Carroll (NASA, UMBC), Carina Poulin (NASA, SSAI)
#
# <div class="alert alert-block alert-warning">
# <b>PREREQUISITES</b>
# <p>This notebook has the following prerequisites:</p>
# <ul>
#     <li>
#     <a href="https://urs.earthdata.nasa.gov/" target="_blank"> An <b>Earthdata Login</b> account</a> is required to access data from the NASA Earthdata system, including NASA ocean color data.
#     </li>
# </ul>
# <p>There are no prerequisite notebooks for this module.</p>
# </div>
#
# ## Learning objectives
#
# At the end of this notebook you will know:
#
# * How to store your NASA Earthdata Login credentials with `earthaccess`
# * How to use `earthaccess` to search for PACE data using search filters
# * How to download PACE data, but only when you need to
#
# ## Summary
#
# In this example we will use the `earthaccess` package to search for data collections from NASA Earthdata. This package, published on the [Python Package Index][pypi] and [conda-forge][conda], facilitates discovery and use of all NASA Earth Science data products by providing an abstraction layer for NASA’s [Common Metadata Repository (CMR) API][cmr] and by simplifying requests to NASA's [Earthdata Cloud][edcloud]. Searching for data is more approachable using `earthaccess` than low-level HTTP requests, and the same goes for S3 requests.
#
# In short, `earthaccess` helps **authenticate** with Earthdata Login, makes **search** easier, and provides a stream-lined way to **load data** into `xarray` containers. For more on `earthaccess`, visit the [documentation][earthaccess-docs] site. Be aware that `earthaccess` is under active development.
#
# <div class="alert alert-info" role="alert">
# <h2>Contents</h2><a name="toc"></a>
# </div>
#
# 1. [Imports](#imports)
# 1. [NASA Earthdata authentication](#auth)
# 1. [Search for data](#search)
# 1. [Download data](#download)
#
# <div class="alert alert-info" role="alert">
# <h2>1. Imports</h2><a name="imports"></a>
# <a href="#toc">[Back to top]</a>
# </div>
#
# We begin by importing the only library we need to run this notebook. If you have created an environment following the [guidance][tutorials] provided with this tutorial, then the package will be sucessfully imported.
#
# [tutorials]: https://oceancolor.gsfc.nasa.gov/resources/docs/tutorials
# [edcloud]: https://www.earthdata.nasa.gov/eosdis/cloud-evolution
# [earthaccess-docs]: https://earthaccess.readthedocs.io/en/stable/
# [cmr]: https://cmr.earthdata.nasa.gov/search/site/docs/search/api.html
# [conda]: https://anaconda.org/conda-forge/earthaccess
# [pypi]: https://pypi.org/project/earthaccess/

import earthaccess

# <div class="alert alert-info" role="alert">
# <h2>2. Authenticate with Earthdata</h2><a name="auth"></a>
# <a href="#toc">[Back to top]</a>
# </div>
#
# Next, we authenticate using our Earthdata Login credentials. Authentication is not necessarily needed to search for publicaly available data collections in Earthdata, but is always needed to download or open data from the NASA Earthdata archives. We can use the `login` method from the `earthaccess` package. This will create a authenticated session when we provide a valid Earthdata Login username and password.
#
# The `earthaccess` package will search for credentials defined by **environmental variables** or within a **.netrc** file saved in the home directory. If credentials are not found, an interactive prompt will allow you to input credentials. The `persist=True` argument ensures any discovered credentials
# are stored in a `.netrc` file, so the argument is not necessary (but it's also harmless) for subsequent calls to `earthaccess.login`.

auth = earthaccess.login(persist=True)

# <div class="alert alert-info" role="alert">
# <h2>2. Search for Data</h2><a name="search"></a>
# <a href="#toc">[Back to top]</a>
# </div>
#
# There are multiple ways to identify "collections" on NASA Earthdata (discovered with the `search_datasets` method) and the "granules" contained in a collection (discovered with the `search_data` method). You can search collections by `instrument` to get started.

results = earthaccess.search_datasets(
    instrument="oci",
)
for item in results:
    summary = item.summary()
    print(summary["short-name"])

# The `search_datasets` method returned collections. Next we use the `search_data` method to find data objects within a collection using the `short_name` for the PACE/OCI Level-2 quick-look product for apparent optical properties (although you could search accross collections too). The `count` argument limits the number of granules returned and stored in the `results` list.

results = earthaccess.search_data(
    short_name = "PACE_OCI_L2_AOP_NRT",
    count = 1,
)

# We can refine our search by passing more parameters that describe the spatiotemporal domain of our use case. Here, we use the `temporal` parameter to request a date range and the `bounding_box` parameter to request granules that intersect with a bounding box. We can even provide a `cloud_cover` threshold to limit files that have a lower percetnage of cloud cover. We do not provide a `count`, so we'll get all granules that satisfy the constraints.

# +
dates = ("2024-04-01", "2024-04-16")
bbox = (-76.75, 36.97, -75.74, 39.01)
clouds = (0, 50)

results = earthaccess.search_data(
    short_name = "PACE_OCI_L2_AOP_NRT",
    temporal = dates,
    bounding_box = bbox, 
    cloud_cover = clouds,
)
# -

# Displaying a result showes a direct download link. The link will download the granule to your local machine, which may or may not be what you want to do. Remember, the "local machine" is the one running the web browser application which may or may not be the machine executing this notebook.

results[0]

# If the URL shown in your web browser begins with "localhost", then clicking the data link will have roughly the same effect as the scripted download discussed next. If the URL shown in your browser is not "localhost", then the code is not running on your local machine and you need the following scripted method below to download data to the machine running the code.
#
# <div class="alert alert-info" role="alert">
# <h2>4. Download Data</h2><a name="download"></a>
# <a href="#toc">[Back to top]</a>
# </div>
#
# First, let's see what happens if you don't download the granules. If you instead use `earthaccess.open` on the
# list of granules, you end up with a list of file-like objects, which are meant to be use like a path to an actual file.

paths = earthaccess.open(results)

# The list of file-like objects held in `paths` can each be read like a normal file. That's true for NetCDF readers, but for a quick demo we just read the first few bytes without any specialized reader.

with paths[0] as file:
    line = file.readline().strip()
line

# Of course that doesn't mean anything (does it? 😉), because this is a binary file that needs a reader which
# understands the file format.
#
# The `earthaccess.open` method is used when you want to directly read a file from a remote filesystem, and not to download it. When running code adjacent to the Earthdata Cloud, so that you don't need to download data, the `earthaccess.open` method is the way to go.
#
# The `earthaccess.download` method is used to copy files onto a filesystem local to the machine executing the function. For this method, provide the output of `earthaccess.search_data` along with the local path to store downloaded granules. Remember, this "local" filesystem is not on the machine running your web browser (unless the url shown by the browser begins with "localhost"). Even if you only want to read the data once, and downloading seems unncessary, if you use `earthaccess.open` while not adjacent to the Earthdata Cloud, performance will be very poor. This is not a problem with "the cloud" or with `earthaccess`, it has to do with the data format and may soon be resolved.

paths = earthaccess.download(results, "L2_AOP")

# The `paths` list now contains paths to actual files on the local filesystem.

paths

# <div class="alert alert-block alert-warning">
# Anywhere in any of <a href="https://oceancolor.gsfc.nasa.gov/resources/docs/tutorials/">these notebooks</a> where <pre>paths = earthaccess.open(...)</pre> is used to read data directly from a remote filesystem, you need to substitue <pre>paths = earthaccess.download(..., local_path)</pre> before running the notebooks on a machine that does not have direct access to the Earthdata Cloud.
# </div>
# <div class="alert alert-info" role="alert">
# <p>You have completed the notebook on downloading and opening datasets. We now suggest starting the notebook on opening OCI data with XArray.</p>
# </div>
