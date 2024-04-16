# ---
# jupyter:
#   jupytext:
#     text_representation:
#       extension: .py
#       format_name: light
#       format_version: '1.5'
#       jupytext_version: 1.16.0
#   kernelspec:
#     display_name: custom
#     language: python
#     name: custom
# ---

# <table><tr>
#
#
# <td> <img src="https://oceancolor.gsfc.nasa.gov/images/ob-logo-svg-2.svg" alt="Drawing" align='right', style="width: 240px;"/> </td>
#
# <td> <img src="https://www.nasa.gov/wp-content/uploads/2023/04/nasa-logo-web-rgb.png" align='right', alt="Drawing" style="width: 70px;"/> </td>
#
# </tr></table>
#
#

# <a href="../Index.ipynb"><< Index</a>
# <br>
# <a href="./1_2_OLCI_file_structure.ipynb">Understanding PACE file structure >></a>

# <font color="dodgerblue">**Ocean Biology Processing Group**</font> <br>
# **Copyright:** 2024 NASA OBPG <br>
# **License:** MIT <br>
# **Authors:** Anna Windle (NASA/SSAI), Guoqing Wang (NASA/SSAI), Ian Carroll (NASA/UMBC), Carina Poulin (NASA/SSAI)

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

# ## Learning objectives
#
# At the end of this notebok you will know:
# * What a netCDF format is
# * How to use `xarray` library to open PACE data
# * What variables are present in each group for PACE data files (L1B, L2, and L3)
#
# ## Outline
# In this example we will use the 'earthaccess' library to access a Level-1B, Level-2, and Level-3 PACE netcdf files and open them using `xarray`.
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
#  1. [Querying PACE L1B file structure](#section2)
#  2. [Querying PACE L2 file structure](#section3)
#  3. [Querying PACE L3 file structure](#section4)
#
# <hr>

# We begin by importing all of the libraries that we need to run this notebook. If you have built your python using the environment file provided in this repository, then you should have everything you need. For more information on building environment, please see the repository README.

import earthaccess
import xarray as xr
import netCDF4 as nc
import matplotlib.pyplot as plt
import cartopy.crs as ccrs

# ## `earthaccess` authentication

auth = earthaccess.login()
# are we authenticated?
if not auth.authenticated:
    # ask for credentials and persist them in a .netrc file
    auth.login(strategy="interactive", persist=True)

# <div class="alert alert-info" role="alert">
#
# ## <a id='section1'>1. Querying PACE L1B file structure
# [Back to top](#TOC_TOP)
#
# </div>

# Let's use `xarray` to open up a PACE L1B netCDF files of the same scene using `earthaccess`. We will use the same search method used in <a href="./2_PACE_data_access.ipynb">2_PACE_data_access.ipynb </a> to access the data:

# +
date_range = ("2024-04-01", "2024-04-16")
bbox = (-76.75,36.97,-75.74,39.01)

results = earthaccess.search_data(
    short_name = "PACE_OCI_L1B_SCI",
    cloud_hosted = True,
    temporal = date_range,
    bounding_box = bbox,
    #cloud_cover = (0,100) #TODO: figure out why cloud_cover isn't working
)

L1B_files = earthaccess.open(results)
L1B_files
# -

# Let's open the first file of the L1B_files list:

dfs = xr.open_dataset(L1B_files[1])
dfs

# Notice that the xarray.Dataset has missing data in some of the categories. `xarray` cannot be used to open multi-group hierarchies or to list groups within a netCDF file, but it can open a specific group if you know it’s path.
#
# Tip: The `datatree` python library can be used to show group names. Uncomment below to run:

# +
#from datatree import open_datatree

#datatree = open_datatree(L1B_files[0], engine='h5netcdf') 
#datatree
# -

# The PACE L1B dataset groups are `sensor_band_parameters`, `scan_line_attributes`, `geolocation_data`, `navigation_data`, and `observation_data`. Let's open the `observation_data` group:

df_obs = xr.open_dataset(L1B_files[1], group='observation_data')
df_obs

# Now you can view the Dimensions, Coordinates, and Variables of this group. To show/hide attributes, press the paper icon on the right hand side of each variable. To show/hide data reprensetaton, press the cylinder icon. 

# The dimensions of the `rhot_blue` variable is (blue_bands, number_of_scans, ccd_pixels) and has the shape (119, 1709, 1272). 

df_obs['rhot_blue'].shape

# Let's quickly plot one blue band:

df_obs['rhot_blue'][100,:,:].plot()

# <div class="alert alert-info" role="alert">
#
# ## <a id='section1'>2. Querying PACE L2 file structure
# [Back to top](#TOC_TOP)
#
# </div>

# Now, let's open a PACE L2 Apparent Optical Data (AOP) file. We'll use the same `earthaccess` search to find the data:

# +
date_range = ("2024-04-01", "2024-04-16")
bbox = (-76.75,36.97,-75.74,39.01)

results = earthaccess.search_data(
    short_name = "PACE_OCI_L2_AOP_NRT",
    cloud_hosted = True,
    temporal = date_range,
    bounding_box = bbox
)

L2_files = earthaccess.open(results)
L2_files

# +
#from datatree import open_datatree

#datatree = open_datatree(L2_files[0], engine='h5netcdf') 
#datatree
# -

# The PACE L2 dataset groups are `sensor_band_parameters`, `scan_line_attributes`, `geophysical_data`, `navigation_data`. <br>
# Let's look at the geophysical_data group

df_geo = xr.open_dataset(L2_files[1], group='geophysical_data')
df_geo

# The Rrs data variable has a shape of (1710, 1272, 184). Let's map a random Rrs wavelength:

df_geo['Rrs'][:,:,100].plot()

# Right now, the scene is being plotted using number_of_lines and pixels_per_line (x,y). Let's add some lat and lon values to map it in a real coordinate space. To do this, we need to create a new xarrray dataset (rrs_xds) and pull in information from the `navigational_data` group (df_nav).

df_nav = xr.open_dataset(L2_files[1], group='navigation_data')
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


# If you wanna get fancy, add a coastline

# +
fig = plt.figure()
ax = plt.axes(projection=ccrs.PlateCarree())
ax.coastlines()
ax.gridlines(draw_labels={"left": "y", "bottom": "x"})

rrs_xds.Rrs[:,:,100].plot(x='longitude', y='latitude', cmap='viridis', vmin=0)

# +
ax.plot(-60, 43, marker='o', color='red')

fig
# -

rrs_xds.Rrs

rrs_xds_point = rrs_xds.sel({
    "number_of_lines": 1650, 
    "pixels_per_line": 1270,
})
rrs_xds_point.coords

rrs_xds_point["Rrs"].plot.line()

# # Combining data 

dfs = xr.open_mfdataset(L1B_files, group="observation_data", combine="nested", 
                        concat_dim="number_of_scans", engine="h5netcdf")
dfs


