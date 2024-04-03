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

# <table><tr>
#
#
# <td> <img src="https://oceancolor.gsfc.nasa.gov/images/ob-logo-svg-2.svg" alt="Drawing" align='right', style="width: 240px;"/> </td>
#
# <td> <img src="https://upload.wikimedia.org/wikipedia/commons/thumb/e/e5/NASA_logo.svg/2449px-NASA_logo.svg.png" align='right', alt="Drawing" style="width: 70px;"/> </td>
#
# </tr></table>

# <a href="../Index.ipynb"><< Index</a>
# <br>
# <a href="./1_2_OLCI_file_structure.ipynb">Understanding PACE file structure >></a>

# <font color="dodgerblue">**Ocean Biology Processing Group**</font> <br>
# **Copyright:** 2024 NASA OBPG <br>
# **License:** MIT <br>
# **Authors:** Anna Windle (NASA/SSAI), Guoqing Wang (NASA/SSAI), Ian Carroll (NASA/UMBC)

# <div class="alert alert-block alert-warning">
#     
# <b>PREREQUISITES 
#     
# The following modules are prerequisites for this notebook, and will retrieve the data required here.
#   - **<a href="./1_PACE_data_access.ipynb" target="_blank">1_PACE_data_access.ipynb</a>**
#     <br><br>
# </div>
# <hr>

# # 2. Understanding PACE file structure

# In this example we will use the 'earthaccess' library to access a Level-1B, Level-2, and Level-3 PACE files to understand the file structure 
#
# ## Learning objectives
# 1. What a netCDF format is
# 2. Brief introduction to the `xarray` library
# 3. What variables are present in each group for PACE data files (L1B, L2, and L3)

# <div class="alert alert-info" role="alert">
#
# ## <a id='TOC_TOP'>Contents
#
# </div>
#     
#  1. [Intro to xarray](#section1)
#  2. [Querying PACE L1B file structure](#section2)
#  3. [Querying PACE L2 file structure](#section3)
#  4. [Querying PACE L3 file structure](#section4)
#  5. 
#     
#
# <hr>

# We begin by importing all of the libraries that we need to run this notebook. If you have built your python using the environment file provided in this repository, then you should have everything you need. For more information on building environment, please see the repository README.

import earthaccess
import xarray as xr
import netCDF4 as nc

# ## `earthaccess` authentication

auth = earthaccess.login()
# are we authenticated?
if not auth.authenticated:
    # ask for credentials and persist them in a .netrc file
    auth.login(strategy="interactive", persist=True)

# <div class="alert alert-info" role="alert">
#
# ## <a id='section1'>1. Intro to xarray
# [Back to top](#TOC_TOP)
#
# </div>

# **<a href="https://xarray.dev/" target="_blank">`xarray`</a>** is a library that supports the use of multi-dimensional arrays in Python. It is widely used to handle Earth observation data, which often involves multiple dimensions — for instance, longitude, latitude, time, and channels/bands. <br>
#
# Let's open up a PACE L1B, L2, and L3 file from the same scene using `earthaccess`:

# +
date_range = ("2024-03-01", "2024-03-03")
bbox = (-76.75,36.97,-75.74,39.01)

results = earthaccess.search_data(
    short_name = "MODISA_L1",
    cloud_hosted = True,
    temporal = date_range,
    bounding_box = bbox
)
L1B_file = results[0]
L1B_file
#earthaccess.open(results[0])
# -

df = xr.open_dataset(earthaccess.open(results))
df

# Notice that the xarray.Dataset has missing data in some of the categories. `xarray` cannot be used to open multi-group hierarchies or to list groups within a netCDF file, but it can open a specific group if you know it’s path.
#
#
# Tip: The `netCDF4` library can access groups. You can use this function to view the groups that you want to specify with `xarray`
#

df_nc = nc.Dataset(file, "r")
df_nc.groups.keys()

# A PACE L1B file has 5 groups: 'sensor_band_parameters', 'scan_line_attributes', 'geophysical_data', 'navigation_data', 'processing_control.
#
# Now we can open each group in `xarray`:

df_bands = xr.open_dataset(file, group='sensor_band_parameters')
df_bands

# Now you can view the Dimensions, Coordinates, and Variables of this group. To show/hide attributes, press the paper icon on the right hand side of each variable. To show/hide data reprensetaton, press the cylinder icon. 

# Let's look at the geophysical_data group

df_geo = xr.open_dataset(file, group='geophysical_data')
df_geo


