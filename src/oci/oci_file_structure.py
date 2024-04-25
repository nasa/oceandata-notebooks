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

# # Understanding PACE file structure

# **Authors:** Anna Windle (NASA/SSAI), Ian Carroll (NASA/UMBC)

# <div class="alert alert-block alert-warning">
#     
# <b>PREREQUISITES 
#     
# This notebook has the following prerequisites:
#   - **<a href="./oci_data_access.ipynb" target="_blank">oci_data_access.ipynb</a>**
#     <br><br>
# </div>

# ## Learning objectives
#
# At the end of this notebok you will know:
# * What a netCDF format is
# * How to use `xarray` library to open PACE data
# * What variables are present in each group for PACE data files (L1B, L2, and L3)
#
# ## Summary
# In this example we will use the `earthaccess` library to access a Level-1B, Level-2, and Level-3 PACE netcdf files and open them using `xarray`.
#
#
# **`netCDF`** (network Common Data Form) is a file format for storing multidimensional scientific data (variables). It is optimized for array-oriented data access and support a machine-independent format for representing scientific data. Files ending in `.nc` are netCDF files.
#
# **<a href="https://xarray.dev/" target="_blank">`xarray`</a>** is a library that supports the use of multi-dimensional arrays in Python. It is widely used to handle Earth observation data, which often involves multiple dimensions — for instance, longitude, latitude, time, and channels/bands. <br>
#
# <div class="alert alert-info" role="alert">
#
# ## <a id='TOC_TOP'>Contents
#
# </div>
#     
#  1. [Inspecting PACE L1B file structure](#section2)
#  2. [Inspecting PACE L2 file structure](#section3)
#  3. [Inspecting PACE L3 file structure](#section4)
#
# <hr>

# <div class="alert alert-info" role="alert">
#
# ## Imports
# [Back to top](#contents)
#
# </div>

# We begin by importing all of the libraries that we need to run this notebook. If you have built your python using the environment file provided in this repository, then you should have everything you need. For more information on building environment, please see the repository README.

# !pip install data-tree

import earthaccess
import xarray as xr
#import datatree as dt
import matplotlib.pyplot as plt
import cartopy.crs as ccrs
import hvplot.xarray 


# TODO: figure out datatree annd add it to .yml?

# ## `earthaccess` authentication

auth = earthaccess.login(persist=True)

# <div class="alert alert-info" role="alert">
#
# ## <a id='section1'>1. Inspecting PACE L1B file structure
# [Back to top](#TOC_TOP)
#
# </div>

# Let's use `xarray` to open up a PACE L1B netCDF files using `earthaccess`. We will use the same search method used in <a href="./oci_data_access.ipynb">oci_data_access.ipynb </a> to access the data:

# TODO : must raise error if not in region (i.e. uses HTTPS)

# +
date_range = ("2024-04-01", "2024-04-16")
bbox = (-76.75,36.97,-75.74,39.01)

results = earthaccess.search_data(
    short_name = "PACE_OCI_L1B_SCI",
    cloud_hosted = True,
    temporal = date_range,
    bounding_box = bbox,
)

L1B_files = earthaccess.open(results)
L1B_files
# -

# Let's open the first file of the L1B_files list:

dfs = xr.open_dataset(L1B_files[0])
dfs

# Notice that the xarray.Dataset has missing data in some of the categories. `xarray` cannot be used to open multi-group hierarchies or list groups within a netCDF file, but it can open a specific group if you know it’s path.
#
# Tip: The `datatree` python library can be used to show group names.

# +
datatree = dt.open_datatree(L1B_files[0], engine='h5netcdf') 
list(datatree)

# TODO: include with just the list(datatree)
# -

# The PACE L1B dataset groups are `sensor_band_parameters`, `scan_line_attributes`, `geolocation_data`, `navigation_data`, and `observation_data`. Let's open the `observation_data` group:

df_obs = xr.open_dataset(L1B_files[0], group='observation_data')
df_obs

# Now you can view the Dimensions, Coordinates, and Variables of this group. To show/hide attributes, press the paper icon on the right hand side of each variable. To show/hide data reprensetaton, press the cylinder icon. 

# The dimensions of the `rhot_blue` variable are: (blue_bands, number_of_scans, ccd_pixels) and has the shape (119, 1709, 1272). 

df_obs['rhot_blue'].shape

# Let's plot the 100th blue band:

df_obs['rhot_blue'][100,:,:].plot()

# <div class="alert alert-info" role="alert">
#
# ## <a id='section2'>2. Inspecting PACE L2 file structure
# [Back to top](#TOC_TOP)
#
# </div>

# Now, let's open a PACE L2 Apparent Optical Data (AOP) file. We'll use the same `earthaccess` search to find the data:

# +
date_range = ("2024-04-01", "2024-04-23")
bbox = (-76.75, 36.97, -75.74, 39.01)

results = earthaccess.search_data(
    short_name = "PACE_OCI_L2_AOP_NRT",
    cloud_hosted = True,
    temporal = date_range,
    bounding_box = bbox,
    cloud_cover = (0,50) #can include a cloud threshold with L2 data
)

L2_files = earthaccess.open(results)
L2_files
# -

datatree = dt.open_datatree(L2_files[0], engine='h5netcdf') 
list(datatree)

# The PACE L2 dataset groups are `sensor_band_parameters`, `scan_line_attributes`, `geophysical_data`, `navigation_data`. <br>
# Let's look at the geophysical_data group

df_geo = xr.open_dataset(L2_files[0], group='geophysical_data')
df_geo

# The Rrs data variable has a shape of (1710, 1272, 184). Let's map the 100th Rrs wavelength:

df_geo['Rrs'][:,:,100].plot()

# Right now, the scene is being plotted using number_of_lines and pixels_per_line (x,y). Let's add some lat and lon values to map it in a real coordinate space. To do this, we will create a new xarrray dataset (rrs_xds) and pull in information from the `navigational_data` group (df_nav).

df_nav = xr.open_dataset(L2_files[0], group='navigation_data')
df_nav

rrs_xds = df_nav.rename({"pixel_control_points": "pixels_per_line"})
rrs_xds = xr.merge((df_geo, rrs_xds))
rrs_xds = rrs_xds.set_coords(("longitude", "latitude"))
rrs_xds

# Although we now have coordinates, they won't help much because the data are not "gridded" by latitude and longitude.
# The Level 2 data are the original instument swath, and have not been resampled to a regular grid. Therefore latitude
# and longitude are known, but cannot be used to "look-up" values like you can along the dataset's dimensions. <br>
#
# Let's plot a scatter plot of the pixel locations so we can see the irregular spacing. 

rrs_xds.sel({"number_of_lines": slice(None, None, 1720//20),
        "pixels_per_line": slice(None, None, 1272//20),}).plot.scatter(x="longitude", y="latitude")

# Let's plot this new xarray dataset the same way as before, but add lat, lon

rrs_xds.Rrs[:,:,100].plot(x='longitude', y='latitude', cmap='viridis', vmin=0)


# Now you can see a lat, lon grid associated with the data. If you wanna get fancy, add a coastline.

# +
fig = plt.figure()
ax = plt.axes(projection=ccrs.PlateCarree())
ax.coastlines()
ax.gridlines(draw_labels={"left": "y", "bottom": "x"})

rrs_xds.Rrs[:,:,100].plot(x='longitude', y='latitude', cmap='viridis', vmin=0)
# -

# TODO: This didn't open a map for me

# Let's plot a Rrs spectrum from one pixel. To do that, we need to select the pixel using _____. 

# +
# TODO make this where thingy work, with point, and more general geometry if possible

# + jupyter={"outputs_hidden": true}
rrs_xds.where((rrs_xds.latitude == 37) & (rrs_xds.longitude == -75), drop=True)

# +
#rrs_xds_point["Rrs"].plot.line()
#plt.ylabel('Remote sensing reflectance (sr^-1)')
#plt.xlabel('Wavelength (nm)')
# -

# <div class="alert alert-info" role="alert">
#
# ## <a id='section3'>3. Inspecting PACE L3 file structure
# [Back to top](#TOC_TOP)
#
# </div>

# Now, let's open a PACE L3M Remote sensing reflectance (RRS) file. We'll use the same `earthaccess` search to find the data:

# +
date_range = ("2024-04-16", "2024-04-20")
bbox = (-76.75,36.97,-75.74,39.01)

results = earthaccess.search_data(
    short_name = "PACE_OCI_L3M_RRS_NRT",
    cloud_hosted = True,
    temporal = date_range,
    bounding_box = bbox
) 

L3_files = earthaccess.open(results)
L3_files
# -

# PACE L3 data do not have any groups so we can open the dataset without specifying a group. Let's take a look at the first file:

df = xr.open_dataset(L3_files[0])
df

# Notice that PACE L3M data has lat,lon coordinates. Let's map the Rrs_442 variable:

# +
fig = plt.figure()
ax = plt.axes(projection=ccrs.PlateCarree())
ax.coastlines()
ax.gridlines(draw_labels={"left": "y", "bottom": "x"})

df.Rrs_442[:,:].plot(cmap='viridis', vmin=0)

# -
# TODO: This doesn't print the map for me


# # Combining data 

# `xr.open_mfdataset` allows you to open multiple files as a single dataset. Let's open all the L2_files that we quered above. 

# TODO: explain what combine, concat_dim does. Is number_of_scans a new variable you assigned? 

dfs = xr.open_mfdataset(L2_files, group="geophysical_data", combine="nested", 
                        concat_dim="number_of_scans", engine="h5netcdf")
dfs

# And now let's plot each file in a subplot:

# +
fig, axs = plt.subplots(nrows=1, ncols=4, sharex=True, sharey=True, figsize=(6,4))

axs = axs.ravel()

g = dfs.Rrs[0,:,:,100].plot(ax=axs[0], add_colorbar=False, cmap='viridis')
dfs.Rrs[1,:,:,100].plot(ax=axs[1], add_colorbar=False, cmap='viridis')
dfs.Rrs[2,:,:,100].plot(ax=axs[2], add_colorbar=False, cmap='viridis')
dfs.Rrs[3,:,:,100].plot(ax=axs[3], add_colorbar=False, cmap='viridis')

cbar_ax = fig.add_axes([0.85, 0.15, 0.05, 0.7])
fig.colorbar(g,  cax=cbar_ax)

for ax in axs:
    ax.set(xlabel=None, ylabel=None)
    ax.set_aspect('equal')

# -
# TODO: this didn't open a map

# <div class="alert alert-info" role="alert">
# <p>You have completed the notebook on OCI file structure. Now try the ____ notebook. </p>
# </div>



