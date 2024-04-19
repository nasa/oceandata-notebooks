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

# <table><tr>
#
#
# <td> <img src="https://oceancolor.gsfc.nasa.gov/images/ob-logo-svg-2.svg" alt="Drawing" align='right', style="width: 240px;"/> </td>
#
# <td> <img src="https://upload.wikimedia.org/wikipedia/commons/thumb/e/e5/NASA_logo.svg/2449px-NASA_logo.svg.png" align='right', alt="Drawing" style="width: 70px;"/> </td>
#
# </tr></table>

# <font color="dodgerblue">**Ocean Biology Processing Group**</font> <br>
# **Copyright:** 2024 NASA OBPG <br>
# **License:** MIT <br>
# **Authors:** Anna Windle (NASA/SSAI), Ian Carroll (NASA/UMBC)

# <div class="alert alert-block alert-warning">
#     
# <b>PREREQUISITES</b> 
#     
# This notebook has the following prerequisites:
# - **<a href="https://urs.earthdata.nasa.gov/" target="_blank"> An Earthdata Login account</a>** is required to access data from the NASA Earthdata system, including NASA ocean color data.
#
# There are no prerequisite notebooks for this module.
# </div>
# <hr>

# + active=""
# TODO: figure out how to get this all in the orange background
# -

# # 1. Accessing PACE data via the `earthaccess` library
#
# ## Learning objectives
#
# At the end of this notebook you will know:
#
# * How to authenticate with `earthaccess`
# * How to use `earthaccess` to search for PACE data using search filters
# * How to download PACE data
#
# ### Outline
# In this example we will use the `earthaccess` library to search for data collections from NASA Earthdata. `earthaccess` is a Python library that simplifies data discovery and access to NASA Earth science data by providing an abstraction layer for NASA’s [Common Metadata Repository (CMR) API](https://cmr.earthdata.nasa.gov/search/site/docs/search/api.html) Search API. The library makes searching for data more approachable by using a simpler notation instead of low level HTTP queries. `earthaccess` takes the trouble out of Earthdata Login **authentication**, makes **search** easier, and provides a stream-line way to download or stream search results into an `xarray` object.
#
# For more on `earthaccess` visit the [`earthaccess` GitHub](https://github.com/nsidc/earthaccess) page and/or the [`earthaccess` documentation](https://earthaccess.readthedocs.io/en/latest/) site. Be aware that `earthaccess` is under active development. 
#
# <div class="alert alert-info" role="alert">
#
# ## <a id='TOC_TOP'>Contents
#
# </div>
#     
#  1. [`earthaccess` authentication](#section1)
#  1. [Search for data](#section2)
#  1. [Download data](#section3)
#
# <hr>

# We begin by importing all of the libraries that we need to run this notebook. If you have built your python using the environment file provided in this repository, then you should have everything you need. For more information on building environment, please see the repository README.

# + active=""
# TODO: On the OBPG website, include text for "Set up": with either an environment.yml file or requirements.txt. And include text about where you run these notebooks (locally, HPC, cloud)
# -

import earthaccess

# <div class="alert alert-info" role="alert">
#
# ## <a id='section1'>1. Authentication for NASA Earthdata
# [Back to top](#TOC_TOP)
#
# </div>

# Next, we will start by authenticating using our Earthdata Login credentials. Authentication is not necessarily needed to search for publicaly available data collections in Earthdata, but is always need to download or access data from the NASA Earthdata archives. We can use `login` method from the `earthaccess` library here. This will create a authenticated session using our Earthdata Login credential. Our credentials can be passed along via **environmental variables** or by a **.netrc** file save in the home/user profile directory. If your credentials are not available in either location, we will be prompt to input our credentials and a **.netrc** will be created and saved for us.  

auth = earthaccess.login()
# are we authenticated?
if not auth.authenticated:
    # ask for credentials and persist them in a .netrc file
    auth.login(strategy="interactive", persist=True)

# <div class="alert alert-info" role="alert">
#
# ## <a id='section2'>2. Search for data
# [Back to top](#TOC_TOP)
#
# </div>

# There are multiple keywords we can use to discovery data from collections. We will use the `short_name` to find data. 

results = earthaccess.search_data(
    short_name = "PACE_OCI_L2_AOP_NRT",
    cloud_hosted = True,
    count = 10    # Restricting to 10 records returned
)

# We can refine our search by passing more parameters that describe the spatiotemporal domain of our use case. Here, we use the `temporal` parameter to request a date range and the `bounding_box` parameter to request granules that intersect with a bounding box. We can even provide a `cloud_cover` threshold to limit files that have a lower percetnage of cloud cover

date_range = ("2024-04-01", "2024-04-16")
bbox = (-76.75,36.97,-75.74,39.01)

results = earthaccess.search_data(
    short_name = "PACE_OCI_L2_AOP_NRT",
    cloud_hosted = True,
    temporal = date_range,
    bounding_box = bbox, 
    cloud_cover = (0,50)
)

# <div class="alert alert-info" role="alert">
#
# ## <a id='section3'>3. Download data
# [Back to top](#TOC_TOP)
#
# </div>

# TODO: describe how this is only to download locally or have seperate notebook that uses earthaccess.download ? 
# explain alt: section 4- Access data in cloud? use data in the cloud instead of download data. and explain how all other notebooks will follow that format. 

# A quick way to do a direct download is to list the results and press on the link to download each file individually. 

results[0]

# +
# to list all you can uncomment and run:
#[display(r) for r in results]
# -

# In some cases you may want to download multiple files at once. `earthaccess` makes downloading the data from the search results very easy using the `earthaccess.download()` function. Files will be downloaded in 'local_path'.

downloaded_files = earthaccess.download(
    results[0],
    local_path='storage/',
)

# If you have completed this section, you can now continue to work through the rest of the notebooks in the repository and learn more about working with PACE data. 

# <hr>
# <a href="../Index.ipynb"><< Index</a>
# <br>
# <a href="./2_PACE_file_structure.ipynb">Understanding PACE file structure >></a>
# <hr>
#
# <a href="https://oceancolor.gsfc.nasa.gov/" target="_blank">NASA Ocean Color website</a> | <a href="https://oceancolor.gsfc.nasa.gov/resources/docs/tutorials/" target="_blank">NASA Ocean Color Tutorials</a></span></p>


