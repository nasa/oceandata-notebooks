# ---
# jupyter:
#   jupytext:
#     cell_metadata_filter: all,-trusted
#     notebook_metadata_filter: -all,jupytext,language_info.name
#     text_representation:
#       extension: .py
#       format_name: light
#       format_version: '1.5'
#       jupytext_version: 1.16.0
#   language_info:
#     name: python
# ---

# # Reprojecting and Formatting PACE OCI Data
#
# **Authors:** Skye Caplan (NASA, SSAI)
#
# <div class="alert alert-info" role="alert">
#
# An [Earthdata Login][edl] account is required to access data from the NASA Earthdata system, including NASA PACE data.
#
# </div>
#
# [edl]: https://urs.earthdata.nasa.gov/
# [oci-data-access]: https://oceancolor.gsfc.nasa.gov/resources/docs/tutorials/notebooks/oci_data_access/
#
# ## Summary
#
# This notebook will use `rioxarray` to reproject PACE OCI data from the instrument swath into a projected coordinate system and save the file as a GeoTIFF (.tif), a common data format used in GIS applications.
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
# 2. [Reprojecting Level 2 PACE Data](#2.-Reprojecting-L2-PACE-Data)
# 3. [Exporting to GeoTIFF](#3.-Exporting-to-GeoTIFF)
# 4. [About Converting Level 3 Data to GeoTIFF](#4.-A-Note-Converting-About-Level-3-Data)

# ## 1. Setup
#
# Begin by importing all of the packages used in this notebook. Please ensure your environment has the most recent versions of `rioxarray` and `rasterio`, as the functionality allowing us to correctly convert PACE Level 2 (L2) files to GeoTIFF is relatively new.

# +
from pathlib import Path

import earthaccess
#import rasterio
import xarray as xr
import numpy as np
import rioxarray as rio
import cartopy
import cartopy.crs as ccrs
import matplotlib.pyplot as plt
import cf_xarray  # noqa: F401
from xarray.backends.api import open_datatree

import rasterio
# -

# The goal of this tutorial is to reproject and convert L2 PACE data between formats, but L2 PACE data comes in many forms. We'll cover two examples here - one with 3-dimensional surface reflectance (SFREFL) data, and one with 2-dimensional vegetation index (VI) data - to illustrate how these datasets need to be handled.
#
# The following cells use `earthaccess` to set and persist your Earthdata login credentials, then search for and download the relevant datasets for a scene covering eastern North America. 

# +
auth = earthaccess.login(persist=True)

results = earthaccess.search_data(
    short_name=["PACE_OCI_L2_SFREFL","PACE_OCI_L2_LANDVI"],
    granule_name="*20240701T175112*",
)
results[0]
# -

results[1]

paths = earthaccess.download(results, local_path="data")

# [back to top](#Contents)

# ## 2. Reprojecting L2 PACE Data
# ### 2.1. 2D Variables - Vegetation Indices
#
# All of PACE's L2 data are still in the instrument swath - in other words, they are not projected to any sort of regular grid, which makes comparing between satellites, or even between two PACE granules in the same location, difficult. However, each pixel is geolocated (i.e., has an associated latitude and longitude), meaning we can reproject our data onto a grid to make working with the data go much more smoothly. 
#
# As mentioned above, we're working with two data products in this tutorial. We'll open both as `xarray` datatrees and display their different dimensional architecture:

# +
vi_path, sr_path = paths[0], paths[1]

sr_dt = open_datatree(sr_path)
vi_dt = open_datatree(vi_path)

print("Surface reflectance dimensions: ", sr_dt.geophysical_data.rhos.dims)
print("Vegetation index dimensions: ", vi_dt.geophysical_data.cire.dims)
# -

# As we can see, the dimensions between the variables in both datasets differ. The surface reflectances contained in the `rhos` variable have 3 dimensions corresponding to (rows, columns, wavelengths), while each VI variable (e.g., `ndvi` or `cire`) is a 2D variable with (row, column) dimensions. 
#
# If we plot one of these variables, we'll see that they aren't on any sort of regular grid, and will instead be plotted by their row (`number_of_lines`) and column (`pixels_per_line`) indices as any non-geospatial array would be.

vi_dt.geophysical_data.cire.plot(cmap="magma", vmin=0)
plt.show()

# This is fine for a quick look into the data, but any analysis would be better served with a mapped dataset. Let's start with VIs to illustrate the projection process. We'll take the whole `geophysical_data` group as the source dataset for reprojection since each VI is contained in this group as a separate variable in the dataset.
#
# The basic steps for reprojection are:
#   1. Set the coordinates to the latitudes and longitudes from the `navigation_data` group
#   2. Assign the spatial dimensions as the columns (or the x coordinate, `pixels_per_line`) and rows (or the y coordinate, `number_of_lines`), and assign the source Coordinate Reference System (CRS). Since we are working with unprojected PACE lat/lons based on the WGS84 datum, we'll use EPSG 4326 as our source CRS.
#   4. Use `rio.reproject` to project our source dataset.
#
# The first two steps are covered in the next cell.

# +
vi_src = vi_dt["geophysical_data"].to_dataset()
vi_src.coords["longitude"] = vi_dt["navigation_data"]["longitude"]
vi_src.coords["latitude"] = vi_dt["navigation_data"]["latitude"]

vi_src = vi_src.rio.set_spatial_dims("pixels_per_line", "number_of_lines").rio.write_crs("epsg:4326")
vi_src
# -

# If we compare `vi_src` before and after those first two steps, it will look like nothing much has changed. However, you can see that under `Coordinates` we now have `longitude` and `latitude`, as well as the `spatial_ref` varibale, which contains the spatial reference information necessary to reproject the data.
#
# In the next cell, we create a destination dataset, `vi_dst`, the projected version of the source dataset. The key parameter in this step is the `src_geoloc_array`, which is how we're able to feed the function our coordinate arrays and get out a projected dataset. In this example, we project into EPSG 4326, but any defined CRS can be used for the `dst_crs`. 

vi_dst = vi_src.rio.reproject(
    dst_crs=vi_src.rio.crs,
    src_geoloc_array=(
        vi_src.coords["longitude"],
        vi_src.coords["latitude"],
    ),
)

# We can plot the data with a basemap to see that it was correctly georeferenced and reprojected.

fig, ax = plt.subplots(
    1, 1, figsize=(9, 5), subplot_kw={"projection": ccrs.PlateCarree()}
)
ax.gridlines(draw_labels={"left": "y", "bottom": "x"}, linewidth=0.25)
ax.coastlines(linewidth=0.5)
ax.add_feature(cartopy.feature.OCEAN, edgecolor="w", linewidth=0.01)
ax.add_feature(cartopy.feature.LAND, edgecolor="w", linewidth=0.01)
ax.add_feature(cartopy.feature.LAKES, edgecolor="w", linewidth=0.01)
vi_dst.cire.plot(cmap="magma", vmin=0)
plt.title("")
plt.show()

# We can see this dataset is already masked for water, but not clouds. We can use the `cf_xarray` package to handle cloud masking before we export this dataset.

# +
if vi_dst.l2_flags.cf.is_flag_variable:
    cloud_mask = ~(vi_dst.l2_flags.cf =="CLDICE")
    vi_dst = vi_dst.where(cloud_mask)

fig, ax = plt.subplots(
    1, 1, figsize=(9, 5), subplot_kw={"projection": ccrs.PlateCarree()}
)
ax.gridlines(draw_labels={"left": "y", "bottom": "x"}, linewidth=0.25)
ax.coastlines(linewidth=0.5)
ax.add_feature(cartopy.feature.OCEAN, edgecolor="w", linewidth=0.01)
ax.add_feature(cartopy.feature.LAND, edgecolor="w", linewidth=0.01)
ax.add_feature(cartopy.feature.LAKES, edgecolor="w", linewidth=0.01)
vi_dst.cire.plot(cmap="magma", vmin=0)
plt.title("")
plt.show()
# -

# The VI data is now masked and reprojected! Now let's start with our 3D surface reflectances.
#
# ### 2.2. 3D Variables - Surface Reflectance 
#
# Typically, you'd be able to repeat the process we completed for the VIs above for most 3D data, and if you tried it with PACE surface reflectances, it would work. However, in addition to reprojecting PACE data, another goal of this tutorial is to export the data into GeoTIFF format for use in a GIS software. Many of these programs, and specifically the popular [QGIS](https://qgis.org/) software, require that the data dimension order use the rule (Z, Y, X), where Y and X are positional coordinates like latitude and longitude. 
#
# Recalling from above, the surface reflectance variable `rhos` has dimensions (rows, columns, wavelengths) - in other words, (Y, X, Z). Without resolving this issue, trying to load PACE surface reflectance data in QGIS will result in what looks like nonsensical lines and squares instead of a rich reflectance data cube! 
#
# To put PACE reflectances in the correct dimensional order, all we have to do is transpose the data so that the wavelength dimension, `wavelength_3d`, is first. 
#
# Before this, we include code that renames the wavelength_3d variable to the center wavelength of each band. This makes it easier to select bands based on wavelength values versus just 1-122 numerical ordering. 

sr_dt['geophysical_data'] = sr_dt['geophysical_data'].to_dataset().assign_coords(sr_dt["sensor_band_parameters"].coords)
sr_dt["geophysical_data"]

# +
# Export rhos with l2_flags or just rhos dataarray?
#sr_src = sr_dt["geophysical_data"].to_dataset()
sr_src = sr_dt["geophysical_data"]["rhos"]
sr_src = sr_src.transpose("wavelength_3d", ...)

sr_src
# -

# The `rhos` variable is now in dimension order (Z, Y, X), which will allow QGIS and other software with the same requirement to properly handle the surface reflectance data. We can now complete the rest of the steps above to reproject the data.

# +
# Leaving this in for now as a possible way to investigate the black box issue since setting nodata properly 
# fixed the issue in the pure rasterio method, but haven't been able to figure it out yet w/ rioxarray
#sr_src.rio.write_nodata(-32767.0, inplace=True)
#sr_src.rio.write_nodata(np.nan, encoded=True, inplace=True) # will this fix the problem...
#sr_src

# +
sr_src.coords["longitude"] = sr_dt["navigation_data"]["longitude"]
sr_src.coords["latitude"] = sr_dt["navigation_data"]["latitude"]

sr_src = sr_src.rio.set_spatial_dims("pixels_per_line", "number_of_lines").rio.write_crs("epsg:4326")

# When I set the dst nodata to 0 and checked it afterward, didn't seem to work? was still
# mirroring the src nodata, so maybe this is part of the black box issue
sr_dst = sr_src.rio.reproject(
    dst_crs=sr_src.rio.crs,
    src_geoloc_array=(
        sr_src.coords["longitude"],
        sr_src.coords["latitude"],
    ),
    nodata=np.nan
)
# -

# Note that the boxes of 0 data still show up for now :(
fig, ax = plt.subplots(
    1, 1, figsize=(9, 5), subplot_kw={"projection": ccrs.PlateCarree()}
)
ax.gridlines(draw_labels={"left": "y", "bottom": "x"}, linewidth=0.25)
ax.coastlines(linewidth=0.5)
ax.add_feature(cartopy.feature.OCEAN, edgecolor="w", linewidth=0.01)
ax.add_feature(cartopy.feature.LAND, edgecolor="w", linewidth=0.01)
ax.add_feature(cartopy.feature.LAKES, edgecolor="w", linewidth=0.01)
#ax.set_extent([-110, -50, 20, 60], crs=ccrs.PlateCarree())
sr_dst.sel({'wavelength_3d':510}).plot(cmap="Greys_r", vmin=0, vmax=1, zorder=101)
plt.title("")
plt.show()

# ## 3. Exporting to GeoTIFF
#
# Now that we have two georeferenced, projected datasets of surface reflectances and VIs, you can export them to your preferred format. Here, we export to GeoTIFF using the "GTiff" driver and applicable profile options. 
#
# We do this by creating a profile from the destination datasets (`sr_dst` or `vi_dst`) and using the `rio.to_raster()` method. Each of the profile options is necessary for the format conversion, but can be changed to user preference as necessary. For example, if you prefer a different `nodata` value or have a specific Affine `transform` for the dataset that would better serve your needs, substitute those values in the dictionaries below.

# +
# NOTE: Either duplicate for each or make a function and call it twice?
#AW: I think having duplicate calls here is fine since it's only two.. 
#espcially since you have a function below that does everything

sr_dst_name = Path(sr_path).with_suffix(".tif") 

profile = {
    "driver": "GTiff",
    "width": sr_dst.shape[2],
    "height": sr_dst.shape[1],
    "count": sr_dst.shape[0],
    "crs": sr_dst.rio.crs,
    "dtype": sr_dst.dtype,
    "transform": sr_dst.rio.transform(),
    "compress": "lzw",
    "nodata": np.nan,
    "tiled": True                           
    }
sr_dst.rio.to_raster(sr_dst_name, **profile)

vi_dst_name = Path(vi_path).with_suffix(".tif")
profile = {
    "driver": "GTiff",
    "width": vi_dst.cire.shape[1],
    "height": vi_dst.cire.shape[0],
    "count": 11,
    "crs": vi_dst.rio.crs,
    "dtype": vi_dst.cire.dtype,
    "transform": vi_dst.rio.transform(),
    "compress": "lzw",
    "nodata": np.nan,
    "tiled": True                           
    }
vi_dst.rio.to_raster(vi_dst_name, **profile)

# -

# The files should be successfully converted, and able to be analyzed properly in QGIS and other software!

# To do this in one step with a function, see the cell below:

# Would welcome a better way to do this!
def nc_to_gtiff(fpath):
    """
    Convert a PACE NetCDF file to GeoTIFF format
    Masks LANDVI dataset for clouds automatically
    Args:
        fpath - Path to NetCDF file to convert
    """
    dt = xr.open_datatree(fpath)
    
    if "SFREFL" in fpath:
        src = dt["geophysical_data"]["rhos"].transpose("wavelength_3d", ...)
    elif "LANDVI" in fpath:
        src = dt["geophysical_data"].to_dataset()
        if src.l2_flags.cf.is_flag_variable:
            cloud_mask = ~(src.l2_flags.cf =="CLDICE")
            src = src.where(cloud_mask)
    else:
        print("File is neither SFREFL nor LANDVI PACE suite, you'll have to adapt these methods yourself!")
        return
        
    src.coords["longitude"] = dt["navigation_data"]["longitude"]
    src.coords["latitude"] = dt["navigation_data"]["latitude"]
    src = (
        src.rio.set_spatial_dims("pixels_per_line", "number_of_lines").rio.write_crs("epsg:4326")
    )

    dst = src.rio.reproject(
        dst_crs=src.rio.crs, 
        src_geoloc_array=(
            src.coords["longitude"], 
            src.coords["latitude"]),
        )

    if "SFREFL" in fpath:
        width, height, count = dst.shape[2], dst.shape[1], dst.shape[0]
        dtype = dst.dtype
    elif "LANDVI" in fpath:
        width, height, count = dst.cire.shape[1], dst.cire.shape[0], 11
        dtype = dst.cire.dtype
        
    dst_name = Path(fpath).with_suffix(".tif")
    profile = {
        "driver": "GTiff", 
        "width": width,
        "height": height,
        "count": count,
        "crs": dst.rio.crs,
        "dtype": dtype,
        "transform": dst.rio.transform(),
        "compress": "lzw",
        "nodata": np.nan,
        "tiled": True
    }
    
    dst.rio.to_raster(dst_name, **profile)


nc_to_gtiff(sr_path)

# ## 4. A Note About Converting Level 3 Data to GeoTIFF
#
# Level 3 PACE data is already mapped to a Plate Carrée projection - in other words, unless you want the data in another projection, you don't need to reproject as we did for the Level 2 data above. In order to convert these files from NetCDF to GeoTIFF, all you need is to assign transpose the datasets as necessary and assign a CRS.

# First, let's download a Level-3 Global Mapped Surface Reflectance file.

# +
results = earthaccess.search_data(
    short_name = 'PACE_OCI_L3M_SFREFL',
    granule_name = 'PACE_OCI.20240601_20240630.L3m.MO.SFREFL.V3_0.rhos.0p1deg.nc')

paths = earthaccess.download(results, local_path="data")

# +
# Would welcome better way to do this part as well - don't want to make folks download another file
# at the end of a tutorial, but this might be an important piece
l3_file = "data/PACE_OCI.20240601_20240630.L3m.MO.SFREFL.V3_0.rhos.0p1deg.nc"
#l3_file = "data/PACE_OCI.20240701_20240731.L3m.MO.LANDVI.V3_0.0p1deg.nc"
if "SFREFL" in l3_file:
    ds = xr.open_dataset(l3_file).rhos.transpose("wavelength", ...)
elif "LANDVI" in l3_file:
    ds = xr.open_dataset(l3_file).drop_vars("palette")
    
ds = ds.rio.write_crs("epsg:4326")
ds.rio.to_raster(Path(l3_file).with_suffix(".tif"))
# -

# [back to top](#Contents)
#
# <div class="alert alert-info" role="alert">
#
# You have completed the notebook on reprojecting and format conversion of PACE OCI L2 data. We suggest looking at the notebook on "Machine Learning with Satellite Data" to explore some more advanced analysis methods.
#
# </div>
