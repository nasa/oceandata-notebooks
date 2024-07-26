# ---
# jupyter:
#   kernelspec:
#     display_name: Python 3 (ipykernel)
#     language: python
#     name: python3
# ---

# # Data visualization
#
# **Authors:** Carina Poulin (NASA, SSAI), Ian Carroll (NASA, UMBC), Anna Windle (NASA, SSAI)
#
# <div class="alert alert-success" role="alert">
#
# **PREREQUISITES**
#  This notebook has the following prerequisites:
#  - An **<a href="https://urs.earthdata.nasa.gov/" target="_blank">**
#    account is required to access data from the NASA Earthdata system, including NASA ocean color data.
#  - Learn with OCI: <a href="https://oceancolor.gsfc.nasa.gov/resources/docs/tutorials/notebooks/oci_ocssw_processing_bash/" target="_blank">Installing and Running OCSSW Command-line Tools
#
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
# Succinct description of the tutorial ...
#
# ## Learning Objectives
#
# At the end of this notebook you will know:
#
# - How to create a true-color image from OCI data from the cloud *WHOLE GLOBE L3!
# - How to create a true-color image from OCI data processed with OCSSW
# - How to make a false color image to look at clouds or smoke
# - How to make an interactive tool to explore OCI data
# - What ...
#
# ## Contents
#
# 1. [Setup](#setup)
# 1. [Section Title](#section-name)
# 1. [Style Notes](#other-name)
#
# <a name="setup"></a>

# ## 1. Setup
#
# Begin by importing all of the packages used in this notebook. If your kernel uses an environment defined following the guidance on the [tutorials] page, then the imports will be successful.
#
# [tutorials]: https://oceancolor.gsfc.nasa.gov/resources/docs/tutorials/

import os
#import earthaccess
#from pathlib import Path
import cartopy.crs as ccrs
import h5netcdf
import matplotlib.pyplot as plt
import numpy as np
import xarray as xr
from netCDF4 import Dataset
import pandas as pd
from PIL import Image, ImageEnhance # Pillow image enhancement library
import warnings

# In this tutorial, we suppress runtime warnings that show up when calculating log for negative values, which is common with our datasets. 

warnings.simplefilter(action='ignore', category=RuntimeWarning)

# [back to top](#contents) <a name="other-name"></a>

# ## Make image from L2 file processed with OCSSW
#
# The best product to create a high-quality RGB image from PACE is the Surface Reflectance (rhos). Cloud-masked rhos are distributed in the SFREFL product suite. If you want to create an image that includes clouds, however, you need to process a L1B file to L2 using l2gen, like we showed in the OCSSW data processing exercise. We will use the L2 file that was created for this exercise. 
#
# Open the L2 netcdf file you created in the previous exercise in read-mode with netCDF4 and look at the information in the file. 
#
# If you do not have the file, download it with the following code:
#
# ```
# # %%bash
# wget https://oceancolor.gsfc.nasa.gov/fileshare/carina_poulin/PACE_OCI.20240501T165311.L2.SFREFL.nc
# ```

# +
nc_file = "/PACE_OCI.20240605T092137.L2.V2.nc"

import h5netcdf
with h5netcdf.File(nc_file, 'r') as nc:
    groups = list(nc)
groups
# -

# When exploring the dataset, we find that the rhos bands are not identified by their respective wavelength. 

dataset_geo = xr.open_dataset(nc_file, group="geophysical_data")
rhos = dataset_geo["rhos"]
rhos

bands = rhos["wavelength_3d"]
bands

# To find the wavelengths corresponding to the bands, we need to look in the sensor band parameters. 

# +
dataset_band_pars = xr.open_dataset(nc_file, group="sensor_band_parameters")

wavelength_3d = dataset_band_pars["wavelength_3d"]
wavelength_3d

# + scrolled=true
df = pd.DataFrame({"Wavelengths": wavelength_3d})
print(df)
# -

dataset = xr.open_dataset(nc_file, group="navigation_data")
dataset = dataset.set_coords(("longitude", "latitude"))
#dataset = dataset.rename({"pixel_control_points": "pixels_per_line"})
dataset = xr.merge((rhos, dataset.coords))
dataset

rhos = dataset["rhos"].sel({"wavelength_3d": 25})
rhos

plot = rhos.plot(x="longitude", y="latitude", cmap="viridis", vmin=0)

# +
# Natural colour single band
red = dataset["rhos"].sel({"wavelength_3d": 25}) # 645 nm
green = dataset["rhos"].sel({"wavelength_3d": 17}) # 555 nm
blue = dataset["rhos"].sel({"wavelength_3d": 2}) # 368 nm

rgb = np.dstack((red, green, blue))

# Normalize image
rgb = (rgb -  np.nanmin(rgb)) / (np.nanmax(rgb) - np.nanmin(rgb)) 

plt.figure(figsize=(6, 6))
plt.imshow(rgb)

# +
# Create a figure with a projection
fig = plt.figure(figsize=(7, 7))
ax = plt.subplot(projection=ccrs.PlateCarree())

# Plot each channel as an RGB image with geographical coordinates
ax.imshow(rgb,
          extent=(rhos.longitude.min(), rhos.longitude.max(), rhos.latitude.min(), rhos.latitude.max()),
          origin='lower', transform=ccrs.PlateCarree(), interpolation='none')
# -

# TALK ABOUT THE FACT YOU CAN DO IT EASY IN SEADAS

# +
# OCI True Color 1 band (SEADAS recipe for OCI RGB)
rhos_red = dataset["rhos"].sel({"wavelength_3d": 25})
rhos_green = dataset["rhos"].sel({"wavelength_3d": 17})
rhos_blue = dataset["rhos"].sel({"wavelength_3d": 2})

red = np.log(rhos_red/0.01)/np.log(1/0.01)
green = np.log(rhos_green/0.01)/np.log(1/0.01)
blue = np.log(rhos_blue/0.01)/np.log(1/0.01)

rgb = np.dstack((red, green, blue))
rgb = (rgb -  np.nanmin(rgb)) / (np.nanmax(rgb) - np.nanmin(rgb))

fig = plt.figure(figsize=(7, 7))
ax = fig.add_subplot(1, 1, 1, projection=ccrs.PlateCarree())
ax.imshow(rgb,
          extent=(rhos.longitude.min(), rhos.longitude.max(), rhos.latitude.min(), rhos.latitude.max()),
          origin='lower', transform=ccrs.PlateCarree(), interpolation='none')

# +
# OCI True Color 1 band -min/max adjusted
vmin = 0.01
vmax = 1.04 # Above 1 because whites can be higher than 1
#---- 

rhos_red = dataset["rhos"].sel({"wavelength_3d": 25})
rhos_green = dataset["rhos"].sel({"wavelength_3d": 17})
rhos_blue = dataset["rhos"].sel({"wavelength_3d": 2})

red = np.log(rhos_red/0.01)/np.log(1/0.01)
green = np.log(rhos_green/0.01)/np.log(1/0.01)
blue = np.log(rhos_blue/0.01)/np.log(1/0.01)

red = red.where((red >= vmin) & (red <= vmax), vmin, vmax)
green = green.where((green >= vmin) & (green <= vmax), vmin, vmax)
blue = blue.where((blue >= vmin) & (blue <= vmax), vmin, vmax)

rgb = np.dstack((red, green, blue))
rgb = (rgb -  np.nanmin(rgb)) / (np.nanmax(rgb) - np.nanmin(rgb)) #normalize

fig = plt.figure(figsize=(7, 7))
ax = fig.add_subplot(1, 1, 1, projection=ccrs.PlateCarree())
ax.imshow(rgb,
          extent=(rhos.longitude.min(), rhos.longitude.max(), rhos.latitude.min(), rhos.latitude.max()),
          origin='lower', transform=ccrs.PlateCarree(), interpolation='none')

# +
# Image adjustments: change values from 0 to 2, 1 being unchanged
contrast = 1.3 
brightness = 1.1 
sharpness = 2
saturation = .8
enhancement = .98
#----

normalized_image = (rgb - rgb.min()) / (rgb.max() - rgb.min())
normalized_image = normalized_image** enhancement

normalized_image = (normalized_image* 255).astype(np.uint8)
# Convert numpy array to Pillow Image
image_pil = Image.fromarray(normalized_image)

# Adjust contrast, brightness and sharpness using Pillow
enhancer = ImageEnhance.Contrast(image_pil)
image_enhanced = enhancer.enhance(contrast)  

enhancer = ImageEnhance.Brightness(image_enhanced)
image_enhanced = enhancer.enhance(brightness)  

enhancer = ImageEnhance.Sharpness(image_enhanced)
image_enhanced = enhancer.enhance(sharpness)

enhancer = ImageEnhance.Color(image_enhanced)
image_enhanced = enhancer.enhance(saturation)

# Convert enhanced image back to numpy array
enhanced_image_np = np.array(image_enhanced) / 255.0  # Normalize back to [0, 1] range

# Create a figure with a specific projection
fig = plt.figure(figsize=(7, 7))
ax = plt.subplot(projection=ccrs.PlateCarree())
ax.imshow(enhanced_image_np, extent=(rhos.longitude.min(), rhos.longitude.max(), rhos.latitude.min(), rhos.latitude.max()),
          origin='lower', transform=ccrs.PlateCarree(), alpha=1)

# +
# OCI True Color 1 band - Normalized by channel
rhos_red = dataset["rhos"].sel({"wavelength_3d": 25})
rhos_green = dataset["rhos"].sel({"wavelength_3d": 17})
rhos_blue = dataset["rhos"].sel({"wavelength_3d": 2})

red = np.log(rhos_red/0.01)/np.log(1/0.01)
green = np.log(rhos_green/0.01)/np.log(1/0.01)
blue = np.log(rhos_blue/0.01)/np.log(1/0.01)

vmin = 0.0
vmax = 1.03 #because whites are higher than 1
red = red.where((red >= vmin) & (red <= vmax), vmin, vmax)
green = green.where((green >= vmin) & (green <= vmax), vmin, vmax)
blue = blue.where((blue >= vmin) & (blue <= vmax), vmin, vmax)

#normaling by channel
red = (red - red.min()) / (red.max() - red.min())
green = (green - green.min()) / (green.max() - green.min())
blue = (blue - blue.min()) / (blue.max() - blue.min())

rgb = np.dstack((red, green, blue))
rgb = (rgb -  np.nanmin(rgb)) / (np.nanmax(rgb) - np.nanmin(rgb)) #normalize

fig = plt.figure(figsize=(7, 7))
ax = plt.subplot(projection=ccrs.PlateCarree())
ax.imshow(rgb, extent=(rhos.longitude.min(), rhos.longitude.max(), rhos.latitude.min(), rhos.latitude.max()),
          origin='lower', transform=ccrs.PlateCarree(), alpha=1)


# +
# OCI True Color 1 band -min/max adjusted
vmin = 0.01
vmax = 1.04 # Above 1 because whites can be higher than 1
#---- 

rhos_red = dataset["rhos"].sel({"wavelength_3d": 25})
rhos_green = dataset["rhos"].sel({"wavelength_3d": 17})
rhos_blue = dataset["rhos"].sel({"wavelength_3d": 2})

red = np.log(rhos_red/0.01)/np.log(1/0.01)
green = np.log(rhos_green/0.01)/np.log(1/0.01)
blue = np.log(rhos_blue/0.01)/np.log(1/0.01)

red = red.where((red >= vmin) & (red <= vmax), vmin, vmax)
green = green.where((green >= vmin) & (green <= vmax), vmin, vmax)
blue = blue.where((blue >= vmin) & (blue <= vmax), vmin, vmax)

rgb = np.dstack((red, green, blue))
rgb = (rgb -  np.nanmin(rgb)) / (np.nanmax(rgb) - np.nanmin(rgb)) #normalize

fig = plt.figure(figsize=(7, 7))
ax = plt.subplot(projection=ccrs.PlateCarree())

ax.imshow(rgb,
          extent=(rhos.longitude.min(), rhos.longitude.max(), rhos.latitude.min(), rhos.latitude.max()),
          origin='lower', transform=ccrs.PlateCarree(), interpolation='none')

# +
# OCI False-color for ice clouds
vmin = 0.0
vmax = 0.7

# IR Bands to create false-color image that highlights ice clouds
rhos_red = dataset["rhos"].sel({"wavelength_3d": 47})
rhos_green = dataset["rhos"].sel({"wavelength_3d": 48})
rhos_blue = dataset["rhos"].sel({"wavelength_3d": 49})

red = rhos_red.where((rhos_red >= vmin) & (rhos_red <= vmax), vmin, vmax)
green = rhos_green.where((rhos_green >= vmin) & (rhos_green <= vmax), vmin, vmax)
blue = rhos_blue.where((rhos_blue >= vmin) & (rhos_blue <= vmax), vmin, vmax)

red = red[:,5:1264] # Cutting edge pixels to get same-size bands
green = green[:,1:1260]

rgb = np.dstack((red, green, blue))
rgb = (rgb -  np.nanmin(rgb)) / (np.nanmax(rgb) - np.nanmin(rgb)) #normalize

fig = plt.figure(figsize=(7, 7))
ax = plt.subplot(projection=ccrs.PlateCarree())

ax.imshow(rgb,
          extent=(rhos.longitude.min(), rhos.longitude.max(), rhos.latitude.min(), rhos.latitude.max()),
          origin='lower', transform=ccrs.PlateCarree(), interpolation='none')
# -

# ## Make image from L2 file processed with OCSSW
#
# The best product to create a high-quality RGB image from PACE is the Surface Reflectance (rhos). Cloud-masked rhos are distributed in the SFREFL product suite. If you want to create an image that includes clouds, however, you need to process a L1B file to L2 using l2gen, like we showed in the OCSSW data processing exercise. We will use the L2 file that was created for this exercise. 
#
# Open the L2 netcdf file you created in the previous exercise in read-mode with netCDF4 and look at the information in the file. 

# auth = earthaccess.login(persist=True)

# tspan = ("2024-07-15", "2024-07-15")
# bbox = (-76.75, 36.97, -75.74, 39.01)
#
# results = earthaccess.search_data(
#     short_name="PACE_OCI_L3M_SFREFL_NRT",
#     temporal=tspan,
#     bounding_box=bbox,
# )

# paths = earthaccess.open(results)

# dataset = xr.open_dataset(paths[0])
# dataset

# nc_file = "/home/jovyan/ocssw_test/granules/PACE_OCI.20240715.L3m.DAY.SFREFL.V2_0.rhos.0p1deg.NRT.nc"
#
# import h5netcdf
# with h5netcdf.File(nc_file, 'r') as nc:
#     groups = list(nc)
# groups

# When exploring the dataset, we find that the rhos bands are not identified by their respective wavelength. 

dataset_rhos = xr.open_dataset(nc_file)
rhos = dataset_rhos["rhos"]
rhos

wavelength = rhos["wavelength"]
wavelength

df = pd.DataFrame({"Wavelengths": wavelength})
print(df)

# To find the wavelengths corresponding to the bands, we need to look in the sensor band parameters. 

dataset = xr.open_dataset(nc_file)

rhos555 = dataset["rhos"].sel({"wavelength": 555})
plot = rhos555.plot(x="lon", y="lat", cmap="viridis", vmin=0)

# +
# Natural colour single band
red_rhos = dataset["rhos"].sel({"wavelength": 645}) # 645 nm
green_rhos = dataset["rhos"].sel({"wavelength": 555}) # 555 nm
blue_rhos = dataset["rhos"].sel({"wavelength": 465}) # 368 nm

rgb = np.dstack((red_rhos, green_rhos, blue_rhos))

# Normalize image
rgb = (rgb -  np.nanmin(rgb)) / (np.nanmax(rgb) - np.nanmin(rgb)) 

plt.figure(figsize=(15,15))
plt.imshow(rgb)
plt.axis('off')

# +
# OCI True Color 1 band (SEADAS recipe for OCI RGB)
rhos_red = dataset["rhos"].sel({"wavelength": 645}) # 645 nm
rhos_green = dataset["rhos"].sel({"wavelength": 555}) # 555 nm
rhos_blue = dataset["rhos"].sel({"wavelength": 465}) # 368 nm

red = np.log(rhos_red/0.01)/np.log(1/0.01)
green = np.log(rhos_green/0.01)/np.log(1/0.01)
blue = np.log(rhos_blue/0.01)/np.log(1/0.01)

rgb = np.dstack((red, green, blue))
rgb = (rgb -  np.nanmin(rgb)) / (np.nanmax(rgb) - np.nanmin(rgb))

plt.figure(figsize=(15, 15))
plt.imshow(rgb)
plt.axis('off')
plt.axis("image")  # gets rid of white border

# +
# OCI True Color 1 band -min/max adjusted
vmin = 0.01
vmax = 1.02 # Above 1 because whites can be higher than 1
#---- 

rhos_red = dataset["rhos"].sel({"wavelength": 645}) # 645 nm
rhos_green = dataset["rhos"].sel({"wavelength": 555}) # 555 nm
rhos_blue = dataset["rhos"].sel({"wavelength": 465}) # 368 nm

red = np.log(rhos_red/0.01)/np.log(1/0.01)
green = np.log(rhos_green/0.01)/np.log(1/0.01)
blue = np.log(rhos_blue/0.01)/np.log(1/0.01)

red = red.where((red >= vmin) & (red <= vmax), vmin, vmax)
green = green.where((green >= vmin) & (green <= vmax), vmin, vmax)
blue = blue.where((blue >= vmin) & (blue <= vmax), vmin, vmax)

rgb = np.dstack((red, green, blue))
rgb = (rgb -  np.nanmin(rgb)) / (np.nanmax(rgb) - np.nanmin(rgb))

plt.figure(figsize=(15, 15))
plt.imshow(rgb)
plt.axis('off')
plt.axis("image")

# +
# Image adjustments: change values from 0 to 2, 1 being unchanged
contrast = 1.5 
brightness = 1.02 
sharpness = 2
saturation = 1.1
enhancement = .95
#----

normalized_image = (rgb - rgb.min()) / (rgb.max() - rgb.min())
normalized_image = normalized_image** enhancement

normalized_image = (normalized_image* 255).astype(np.uint8)
# Convert numpy array to Pillow Image
image_pil = Image.fromarray(normalized_image)

# Adjust contrast, brightness and sharpness using Pillow
enhancer = ImageEnhance.Contrast(image_pil)
image_enhanced = enhancer.enhance(contrast)  

enhancer = ImageEnhance.Brightness(image_enhanced)
image_enhanced = enhancer.enhance(brightness)  

enhancer = ImageEnhance.Sharpness(image_enhanced)
image_enhanced = enhancer.enhance(sharpness)

enhancer = ImageEnhance.Color(image_enhanced)
image_enhanced = enhancer.enhance(saturation)

# Convert enhanced image back to numpy array
enhanced_image_np = np.array(image_enhanced) / 255.0  # Normalize back to [0, 1] range

# Create a figure
plt.figure(figsize=(10, 10))
plt.imshow(enhanced_image_np)
plt.axis('off')
plt.axis("image")
# -

# Create a large figure and export to png
plt.figure(figsize=(25, 25))
plt.imshow(enhanced_image_np)
plt.axis('off')
plt.axis("image")
plt.savefig('mapJuly152024.png')

# ## 3. Style Notes
#
# Some recomendations for consistency between notebooks, and a good user experience:
#
# - avoid code cells much longer than twenty lines
# - avoid code cells with blank lines (except where preferred by PEP 8)
# - prefer a whole markdown cell, with full descriptions, over inline code comments
# - avoid splitting markdown cells that are adjacent
# - remove any empty cell at the end of the notebook
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

# [back to top](#contents)
#
# <div class="alert alert-info" role="alert">
#
# You have completed the notebook on downloading and opening datasets. We now suggest starting the notebook on ...
#
# </div>
