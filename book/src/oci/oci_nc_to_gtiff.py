# ---
# jupyter:
#   jupytext:
#     cell_metadata_filter: all,-trusted
#     notebook_metadata_filter: -all,jupytext,language_info.name
#     text_representation:
#       extension: .py
#       format_name: light
#       format_version: '1.5'
#       jupytext_version: 1.16.7
#   language_info:
#     name: python
# ---

# # Title of the Tutorial
#
# **Authors:** Skye Caplan (NASA, SSAI)
#
# <div class="alert alert-success" role="alert">
#
# The following notebooks are **prerequisites** for this tutorial.
#
# - Learn with OCI: [Data Access][oci-data-access]
#
# </div>
#
# <div class="alert alert-info" role="alert">
#
# An [Earthdata Login][edl] account is required to access data from the NASA Earthdata system, including NASA ocean color data.
#
# </div>
#
# [edl]: https://urs.earthdata.nasa.gov/
# [oci-data-access]: https://oceancolor.gsfc.nasa.gov/resources/docs/tutorials/notebooks/oci_data_access/
#
# ## Summary
#
# This notebook will use `rasterio` to reproject PACE OCI data from the instrument swath into a projected coordinate system and save the file as a GeoTIFF, a common data format used in GIS applications. 
#
# ## Learning Objectives
#
# At the end of this notebook you will know:
#
# - Open PACE OCI surface reflectance and vegetation index products
# - Reproject those data into defined coordinate reference systems
# - Export those reprojected data as GeoTIFFs
#
# ## Contents
#
# 1. [Setup](#1.-Setup)
# 2. [Section Title](#2.-Section-Title)
# 3. [Style Notes](#3.-Style-Notes)

# ## 1. Setup
#
# Begin by importing all of the packages used in this notebook. If your kernel uses an environment defined following the guidance on the [tutorials] page, then the imports will be successful.
#
# [tutorials]: https://oceancolor.gsfc.nasa.gov/resources/docs/tutorials/

# +
import os
import numpy as np 
import xarray as xr
import cartopy.crs as ccrs 
import matplotlib.pyplot as plt 
import earthaccess
import cf_xarray
from xarray.backends.api import open_datatree
from pathlib import Path

def open_and_merge(filepath):
    """
    Open a PACE OCI netcdf file and merge the geophysical data
        with the geolocation data.
    Args:
        filepath: path to the OCI file
    Returns:
        ds: merged dataset containing data variables and lat/lon 
            information as coordinates
    """
    datatree = open_datatree(filepath)
    data = datatree.geophysical_data.to_dict()
    data.update(datatree.navigation_data.to_dict())
    ds = xr.merge(data.values())
    ds = ds.set_coords(("latitude", "longitude"))
    return ds


# -

# Consider describing anything about the above imports, especially if a package must be installed [conda forge][conda] rather than from [PyPI][pypi].
#
# Also define any functions or classes used in the notebook.
#
# [conda]: https://anaconda.org/conda-forge/earthaccess
# [pypi]: https://pypi.org/project/earthaccess/
#
# [back to top](#Contents)

# ## 2. Search for and Open OCI data
#
# Set and persist your Earthdata login credentials

auth = earthaccess.login(persist=True)

# We'll use 'earthaccess' to search for and open two types of OCI data: surface reflectances from the SFREFL suite, and vegetation indices from the LANDVI suite.

# Using the same file as the terrestrial analysis tutorial for now
srf_results = earthaccess.search_data(
    short_name="PACE_OCI_L2_SFREFL",
    granule_name = "*20240701T175112*"
)
srf_results[0]

vi_results = earthaccess.search_data(
    short_name="PACE_OCI_L2_LANDVI",
    granule_name = "*20240701T175112*"
)
vi_results[0]

srf_paths = earthaccess.download(srf_results, local_path="data")
vi_paths = earthaccess.download(vi_results, local_path="data")
vi_paths

# The main difference in these two files, other than the data they contain, is the number of dimensions inherent to each variable. Let's open each file and look at what that means:

rhos = open_and_merge(srf_paths[0])
rhos
#dt = open_datatree(srf_paths[0])
#dt.geophysical_data.to_dict()

vi = open_and_merge(vi_paths[0])
vi

# You can see that `rhos` is a 3-dimensional variable with dimensions (`number_of_lines`, `pixels_per_line`, `wavelength_3d`) which corresponds to (rows, columns, wavelength), while each vegetation index is 2-dimensional with (rows, columns). This is important because it means each file has to be treated differently when converting their format. We'll start with the simpler case, the VIs.
#
# Since each VI is a separate variable in our dataset `vi`, we'll have to convert each one into a separate GeoTIFF. Let's take CIRE as an example. First, we define the coordinate reference systems (CRS) for both the source dataset and our destination GeoTIFF, and calculate the necessary parameters for the projection. 
#
# Because we're using unprojected latitude and longitude values based on WGS 84, the CRS of our source data is EPSG 4326. The destination CRS is user's choice; we'll use EPSG 4326 again for simplicity. 

# +
datatree = open_datatree(vi_paths[0])
src = datatree["cire"]
lon = datatree["longitude"]
lat = datatree["latitude"]

src_crs = rasterio.crs.CRS.from_epsg(4326)
dst_crs = rasterio.crs.CRS.from_epsg(4326)

transform, width, height = rasterio.warp.calculate_default_transform(
    src_crs,
    dst_crs,
    src.sizes["pixels_per_line"],
    src.sizes["number_of_lines"],
    src_geoloc_array=(lon, lat),
)
# -



# [back to top](#Contents)

# ## 3. Style Notes
#
# Some recomendations for consistency between notebooks, and a good user experience:
#
# - avoid code cells much longer than twenty lines
# - avoid code cells with blank lines (except where preferred by PEP 8)
# - prefer a whole markdown cell, with full descriptions, over inline code comments
# - avoid splitting markdown cells that are adjacent
# - remove any empty cell at the end of the notebook
# - enable output scrolling for long outputs
#
# Here are the two additional "alert" boxes used in some notebooks to help you choose between "success", "danger", "warning", and "info".
#
# <div class="alert alert-warning" role="alert">
#
# Anywhere in any of [these notebooks][tutorials] where `paths = earthaccess.open(...)` is used to read data directly from the NASA Earthdata Cloud, you need to substitute `paths = earthaccess.download(..., local_path)` before running the notebook on a local host or a remote host that does not have direct access to the NASA Earthdata Cloud.
#
# </div>
#
# <div class="alert alert-danger" role="alert">
#
# Conda uses a lot of memory while configuring your environment. Choose an option with more than about 5GB of RAM from the JupyterHub Control Panel, or your install will fail.
#
# </div>

# Use everything imported.

Path()

# Toggle on scrolling for long outputs **AND** add the cell tag "scroll-output".

# + scrolled=true tags=["scroll-output"]
for i in range(42):
    print(i)
# -

# [back to top](#Contents)
#
# <div class="alert alert-info" role="alert">
#
# You have completed the notebook on ... suggest what's next. And don't add an emptyr cell after this one.
#
# </div>
