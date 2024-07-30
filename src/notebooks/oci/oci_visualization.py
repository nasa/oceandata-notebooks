# ---
# jupyter:
#   kernelspec:
#     display_name: Python 3 (ipykernel)
#     language: python
#     name: python3
# ---

# # Title of the Tutorial
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
# - What goes into an animation of multi-angular HARP2 data
# - What ...
#
# ## Contents
#
# 1. [Setup](#1.-Setup)
# 2. [Global Oceans in True Color](#2.-Global-Oceans-in-True-Color)
# 3. [Complete Scene in True Color](#3.-Full-Scene-in-True-Color)
# 4. [Phytoplankton in False Color](4.-Phytoplankton-in-False-Color)
# 5. [Full Spectra from Global Oceans](5.-Full-Spectra-from-Global-Oceans)
# 6. [Animation from Multiple Angles](6.-Animation-from-Multiple-Angles)

# ## 1. Setup
#
# Begin by importing all of the packages used in this notebook. If your kernel uses an environment defined following the guidance on the [tutorials] page, then the imports will be successful.
#
# [tutorials]: https://oceancolor.gsfc.nasa.gov/resources/docs/tutorials/

# +
import os

from PIL import Image, ImageEnhance
from xarray.backends.api import open_datatree
from matplotlib.colors import ListedColormap
import cartopy.crs as ccrs
import earthaccess
import matplotlib.pyplot as plt
import matplotlib.pylab as pl
import numpy as np
import pandas as pd
import xarray as xr
# -

options = xr.set_options(display_expand_attrs=False)

# In this tutorial, we suppress runtime warnings that show up when calculating log for negative values, which is common with our datasets. 

# +
#warnings.simplefilter(action='ignore', category=RuntimeWarning)
# -

# [back to top](#contents) <a name="other-name"></a>

# ## 2. Global True Color

# The L3M files are the nicest files, use them to introduce the "dimensions" and "coordinates" parts of an XArray dataset.

results = earthaccess.search_data(
    short_name="PACE_OCI_L3M_RRS_NRT",
    granule_name="*.MO.*.1deg.*",
)
paths = earthaccess.open(results)

# The Level-3 Mapped files have no groups and have variables that XArray recognizes as "coordinates":
# variables that are named after their only dimension.

dataset = xr.open_dataset(paths[-1])
dataset

# For a true color image, choose three wavelengths to represent the "Red", "Green", and "Blue"
# channels used to make true color images.

rrs_rgb = dataset["Rrs"].sel({"wavelength": [645, 555, 368]})
rrs_rgb

# It is always a good practice to build your labels into the dataset, and we'll see next
# that it can be very useful as we learn to use metadata while creating visuzalizations.
#
# For this case, we can attach another variable called "channel" and then swap it with
# "wavelength" to become the third dimension of the data array.

rrs_rgb["channel"] = ("wavelength", ["Reds", "Greens", "Blues"])
rrs_rgb = rrs_rgb.swap_dims({"wavelength": "channel"})
rrs_rgb

# Without worrying about matplotlib's terrible defaults for annotation, let's see what we have.

fig, axs = plt.subplots(3, 1)
for i, item in enumerate(rrs_rgb["channel"]):
    array = rrs_rgb.sel({"channel": item})
    array.plot.imshow(x="lon", y="lat", cmap=item.item(), ax=axs[i], robust=True)


# Define a function to apply enhancements, our own plus generic image enhancements from the Pillow package.

def enhance(rgb, scale = 0.01, vmin = 0.01, vmax = 1.02, gamma=0.95, contrast=1.5, brightness=1.02, sharpness=2, saturation=1.1):
    rgb = rgb.where(rgb > 0)
    rgb = np.log(rgb/scale)/np.log(1/scale)
    # TODO don't understand using of vmin and vmax (i.e. doing it wrong)
    # rgb = rgb.where(rgb > vmin, vmin)
    # rgb = rgb.where(rgb < vmax, vmax)
    rgb = (rgb -  rgb.min()) / (rgb.max() - rgb.min())
    rgb = rgb * gamma
    img = rgb * 255
    img = img.where(img.notnull(), 0).astype("uint8")
    img = Image.fromarray(img.data)
    enhancer = ImageEnhance.Contrast(img)
    img = enhancer.enhance(contrast)
    enhancer = ImageEnhance.Brightness(img)
    img = enhancer.enhance(brightness)
    enhancer = ImageEnhance.Sharpness(img)
    img = enhancer.enhance(sharpness)
    enhancer = ImageEnhance.Color(img)
    img = enhancer.enhance(saturation)
    rgb[:] = np.array(img) / 255
    return rgb


rrs_rgb_enhanced = enhance(rrs_rgb)

artist = rrs_rgb_enhanced.plot.imshow(x="lon", y="lat")

# ## 3. Complete Scene in True Color

# ### Make image from L2 file processed with OCSSW
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
nc_file = "/home/jovyan/ocssw_test/granules/PACE_OCI.20240605T092137.L2.V2.nc"

groups = list(open_datatree(nc_file))
groups
# -

# When exploring the dataset, we find that the rhos bands are not identified by their respective wavelength. 

dataset_geo = xr.open_dataset(nc_file, group="geophysical_data")
rhos = dataset_geo["rhos"]
rhos

bands = rhos["wavelength_3d"]
bands

# To find the wavelengths corresponding to the bands, we need to look in the sensor band parameters. 

dataset_band_pars = xr.open_dataset(nc_file, group="sensor_band_parameters")
wavelengths_bands = dataset_band_pars["wavelength_3d"]
wavelengths_bands

# + scrolled=true
df = pd.DataFrame({"Wavelength_bands": wavelengths_bands})
print(df)
# -

dataset = xr.open_dataset(nc_file, group="navigation_data")
dataset = dataset.set_coords(("longitude", "latitude"))
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
rgb = (rgb -  np.nanmin(rgb)) / (np.nanmax(rgb) - np.nanmin(rgb)) # Normalize image

plt.figure(figsize=(3, 3))
plt.imshow(rgb)
# -

# Create a figure with a projection
fig = plt.figure(figsize=(5, 5))
ax = plt.subplot(projection=ccrs.PlateCarree())
extent=(rhos.longitude.min(), rhos.longitude.max(), rhos.latitude.min(), rhos.latitude.max())
ax.imshow(rgb, extent=extent, origin='lower', transform=ccrs.PlateCarree(), interpolation='none')

# DO IT EASY IN SEADAS

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

fig = plt.figure(figsize=(5, 5))
ax = plt.subplot(projection=ccrs.PlateCarree())
extent=(rhos.longitude.min(), rhos.longitude.max(), rhos.latitude.min(), rhos.latitude.max())
ax.imshow(rgb, extent=extent, origin='lower', transform=ccrs.PlateCarree(), interpolation='none')

# +
# OCI True Color 1 band - Normalized by channel
rhos_red = dataset["rhos"].sel({"wavelength_3d": 25})
rhos_green = dataset["rhos"].sel({"wavelength_3d": 17})
rhos_blue = dataset["rhos"].sel({"wavelength_3d": 2})

red = (red - red.min()) / (red.max() - red.min()) # Normaling by channel
green = (green - green.min()) / (green.max() - green.min())
blue = (blue - blue.min()) / (blue.max() - blue.min())
rgb = np.dstack((red, green, blue))
rgb = (rgb -  np.nanmin(rgb)) / (np.nanmax(rgb) - np.nanmin(rgb)) #normalize

fig = plt.figure(figsize=(5, 5))
ax = plt.subplot(projection=ccrs.PlateCarree())
extent=(rhos.longitude.min(), rhos.longitude.max(), rhos.latitude.min(), rhos.latitude.max())
ax.imshow(rgb, extent=extent, origin='lower', transform=ccrs.PlateCarree(), alpha=1)


# +
# OCI True Color 1 band - log and min/max adjusted
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
extent = (rhos.longitude.min(), rhos.longitude.max(), rhos.latitude.min(), rhos.latitude.max())
ax.imshow(rgb, extent=extent, origin='lower', transform=ccrs.PlateCarree(), interpolation='none')

# +
# Image adjustments: change values from 0 to 2, 1 being unchanged
contrast = 1.2 
brightness = 1.1 
sharpness = 2
saturation = .8
gamma = .95
#----

normalized_image = (rgb - rgb.min()) / (rgb.max() - rgb.min())
normalized_image = normalized_image** gamma
normalized_image = (normalized_image* 255).astype(np.uint8)
image_pil = Image.fromarray(normalized_image) # Convert numpy array to Pillow Image

# Adjust contrast, brightness and sharpness using Pillow
enhancer = ImageEnhance.Contrast(image_pil)
image_enhanced = enhancer.enhance(contrast)  
enhancer = ImageEnhance.Brightness(image_enhanced)
image_enhanced = enhancer.enhance(brightness)  
enhancer = ImageEnhance.Sharpness(image_enhanced)
image_enhanced = enhancer.enhance(sharpness)
enhancer = ImageEnhance.Color(image_enhanced)
image_enhanced = enhancer.enhance(saturation)
enhanced_image_np = np.array(image_enhanced) / 255.0  # Normalize back to [0, 1] range

fig = plt.figure(figsize=(7, 7))
ax = plt.subplot(projection=ccrs.PlateCarree())
extent = (rhos.longitude.min(), rhos.longitude.max(), rhos.latitude.min(), rhos.latitude.max())
ax.imshow(enhanced_image_np, extent=extent, origin='lower', transform=ccrs.PlateCarree(), alpha=1)

# +
# OCI False-color for ice clouds
vmin = 0.0
vmax = 0.68

# IR Bands to create false-color image that highlights ice clouds
rhos_red = dataset["rhos"].sel({"wavelength_3d": 47}) # 1618.0 nm
rhos_green = dataset["rhos"].sel({"wavelength_3d": 48}) # 2131.0 nm
rhos_blue = dataset["rhos"].sel({"wavelength_3d": 49}) # 2258.0 nm

red = rhos_red.where((rhos_red >= vmin) & (rhos_red <= vmax), vmin, vmax)
green = rhos_green.where((rhos_green >= vmin) & (rhos_green <= vmax), vmin, vmax)
blue = rhos_blue.where((rhos_blue >= vmin) & (rhos_blue <= vmax), vmin, vmax)
red = red[:,8:1267] # Cutting edge pixels to get same-size bands
green = green[:,1:1260]
rgb = np.dstack((red, green, blue))
rgb = (rgb -  np.nanmin(rgb)) / (np.nanmax(rgb) - np.nanmin(rgb)) #normalize

fig = plt.figure(figsize=(7, 7))
ax = plt.subplot(projection=ccrs.PlateCarree())
extent=(rhos.longitude.min(), rhos.longitude.max(), rhos.latitude.min(), rhos.latitude.max())
ax.imshow(rgb, extent=extent, origin='lower', transform=ccrs.PlateCarree(), interpolation='none')
# -

# ### Make image from L3 file
#
# The best product to create a high-quality RGB image from PACE is the Surface Reflectance (rhos). Cloud-masked rhos are distributed in the SFREFL product suite. If you want to create an image that includes clouds, however, you need to process a L1B file to L2 using l2gen, like we showed in the OCSSW data processing exercise. We will use the L2 file that was created for this exercise. 
#
# Open the L2 netcdf file you created in the previous exercise in read-mode with netCDF4 and look at the information in the file. 

auth = earthaccess.login(persist=True)

# + scrolled=true
tspan = ("2024-07-15", "2024-07-15")
#bbox = (-76.75, 36.97, -75.74, 39.01)

results = earthaccess.search_data(
    short_name="PACE_OCI_L3M_SFREFL_NRT",
    temporal=tspan,
#    bounding_box=bbox,
)
# -

paths = earthaccess.open(results)

dataset = xr.open_dataset(paths[0])
dataset

# +
nc_file = "/home/jovyan/ocssw_test/granules/PACE_OCI.20240715.L3m.DAY.SFREFL.V2_0.rhos.0p1deg.NRT.nc"

groups = list(open_datatree(nc_file))
groups
# -

# When exploring the dataset, we find that the rhos bands are not identified by their respective wavelength. 

dataset = xr.open_dataset(nc_file)
rhos = dataset["rhos"]
rhos

# + scrolled=true
wavelength = rhos["wavelength"]
df = pd.DataFrame({"Wavelengths": wavelength})
print(df)

# -

# To find the wavelengths corresponding to the bands, we need to look in the sensor band parameters. 

rhos555 = dataset["rhos"].sel({"wavelength": 555})
plot = rhos555.plot(x="lon", y="lat", cmap="viridis", vmin=0)

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

# +
# Image adjustments: change values from 0 to 2, 1 being unchanged
contrast = 1.5 
brightness = 1.02 
sharpness = 2
saturation = 1.1
gamma = .95
#----

normalized_image = (rgb - rgb.min()) / (rgb.max() - rgb.min())
normalized_image = normalized_image** gamma
normalized_image = (normalized_image* 255).astype(np.uint8)
image_pil = Image.fromarray(normalized_image)
enhancer = ImageEnhance.Contrast(image_pil)
image_enhanced = enhancer.enhance(contrast)  
enhancer = ImageEnhance.Brightness(image_enhanced)
image_enhanced = enhancer.enhance(brightness)  
enhancer = ImageEnhance.Sharpness(image_enhanced)
image_enhanced = enhancer.enhance(sharpness)
enhancer = ImageEnhance.Color(image_enhanced)
image_enhanced = enhancer.enhance(saturation)
enhanced_image_np = np.array(image_enhanced) / 255.0

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

# ## 4. Phytoplankton in False Color

# +
nc_file = "/home/jovyan/PACE_OCI.20240309T115927.L2.BGC.nc"

groups = list(open_datatree(nc_file))
groups
# -

dataset_geo = xr.open_dataset(nc_file, group="geophysical_data")
dataset_geo

# +
rhos_465 = dataset_geo["rhos_465"]
rhos_555 = dataset_geo["rhos_555"]
rhos_645 = dataset_geo["rhos_645"]
syn = dataset_geo["syncoccus_moana"]
pro = dataset_geo["prococcus_moana"]
pico = dataset_geo["picoeuk_moana"]

dataset = xr.open_dataset(nc_file, group="navigation_data")
dataset = dataset.set_coords(("longitude", "latitude"))
dataset = xr.merge((rhos_465, rhos_555, rhos_645, syn, pro, pico, dataset.coords))
dataset
# -

plot = dataset["rhos_555"].plot(x="longitude", y="latitude", cmap="viridis", vmin=0)

# +
# OCI True Color 1 band -min/max adjusted
vmin = 0.01
vmax = 1.04 # Above 1 because whites can be higher than 1
#---- 

rhos_red = dataset["rhos_645"]
rhos_green = dataset["rhos_555"]
rhos_blue = dataset["rhos_465"]
red = np.log(rhos_red/0.01)/np.log(1/0.01)
green = np.log(rhos_green/0.01)/np.log(1/0.01)
blue = np.log(rhos_blue/0.01)/np.log(1/0.01)
red = red.where((red >= vmin) & (red <= vmax), vmin, vmax)
green = green.where((green >= vmin) & (green <= vmax), vmin, vmax)
blue = blue.where((blue >= vmin) & (blue <= vmax), vmin, vmax)
rgb = np.dstack((red, green, blue))
rgb = (rgb -  np.nanmin(rgb)) / (np.nanmax(rgb) - np.nanmin(rgb)) #normalize

fig = plt.figure(figsize=(5, 5))
ax = fig.add_subplot(projection=ccrs.PlateCarree())
ax.imshow(rgb,
          extent=(dataset.longitude.min(), dataset.longitude.max(), dataset.latitude.min(), dataset.latitude.max()),
          origin='lower', transform=ccrs.PlateCarree(), interpolation='none')

# +
# Image adjustments: change values from 0 to 2, 1 being unchanged
contrast = 1.72
brightness = 1 
sharpness = 2
saturation = 1.3
gamma = .43
#----

normalized_image = (rgb - rgb.min()) / (rgb.max() - rgb.min())
normalized_image = normalized_image** gamma
normalized_image = (normalized_image* 255).astype(np.uint8)
image_pil = Image.fromarray(normalized_image)
enhancer = ImageEnhance.Contrast(image_pil)
image_enhanced = enhancer.enhance(contrast)  
enhancer = ImageEnhance.Brightness(image_enhanced)
image_enhanced = enhancer.enhance(brightness)  
enhancer = ImageEnhance.Sharpness(image_enhanced)
image_enhanced = enhancer.enhance(sharpness)
enhancer = ImageEnhance.Color(image_enhanced)
image_enhanced = enhancer.enhance(saturation)
enhanced_image_np = np.array(image_enhanced) / 255.0  # Normalize back to [0, 1] range

fig = plt.figure(figsize=(5, 5))
ax = plt.subplot(projection=ccrs.PlateCarree())
extent=(dataset.longitude.min(), dataset.longitude.max(), dataset.latitude.min(), dataset.latitude.max())
ax.imshow(enhanced_image_np, extent=extent, origin='lower', transform=ccrs.PlateCarree(), alpha=1)
# -
fig = plt.figure(figsize=(5, 5))
ax = fig.add_subplot(projection=ccrs.PlateCarree())
extent=(dataset.longitude.min(), dataset.longitude.max(), dataset.latitude.min(), dataset.latitude.max())
ax.imshow(dataset["syncoccus_moana"], extent=extent, origin='lower', transform=ccrs.PlateCarree(), interpolation='none', cmap="Reds", vmin=0, vmax=35000, alpha = 1)

# Create transparent color maps for MOANA products

# +
cmap_greens = pl.cm.Greens # Get original color map
my_cmap_greens = cmap_greens(np.arange(cmap_greens.N)) 
my_cmap_greens[:,-1] = np.linspace(0, 1, cmap_greens.N) # Set alpha for transparency
my_cmap_greens = ListedColormap(my_cmap_greens) # Create new colormap
cmap_reds = pl.cm.Reds
my_cmap_reds = cmap_reds(np.arange(cmap_reds.N))
my_cmap_reds[:,-1] = np.linspace(0, 1, cmap_reds.N)
my_cmap_reds = ListedColormap(my_cmap_reds)
cmap_blues = pl.cm.Blues
my_cmap_blues = cmap_blues(np.arange(cmap_blues.N))
my_cmap_blues[:,-1] = np.linspace(0, 1, cmap_blues.N)
my_cmap_blues = ListedColormap(my_cmap_blues)

fig = plt.figure(figsize=(5, 5))
ax = fig.add_subplot(projection=ccrs.PlateCarree())
extent=(dataset.longitude.min(), dataset.longitude.max(), dataset.latitude.min(), dataset.latitude.max())
ax.imshow(dataset["syncoccus_moana"], extent=extent, origin='lower', transform=ccrs.PlateCarree(), interpolation='none', cmap=my_cmap_reds, vmin=0, vmax=35000, alpha = 1)

# +
# Image adjustments: change values from 0 to 2, 1 being unchanged
contrast = 1.9 
brightness = 1 
sharpness = 2
saturation = 1.4
gamma = .48
#----

normalized_image = (rgb - rgb.min()) / (rgb.max() - rgb.min())
normalized_image = normalized_image** gamma
normalized_image = (normalized_image* 255).astype(np.uint8)
image_pil = Image.fromarray(normalized_image)
enhancer = ImageEnhance.Contrast(image_pil)
image_enhanced = enhancer.enhance(contrast)  
enhancer = ImageEnhance.Brightness(image_enhanced)
image_enhanced = enhancer.enhance(brightness)  
enhancer = ImageEnhance.Sharpness(image_enhanced)
image_enhanced = enhancer.enhance(sharpness)
enhancer = ImageEnhance.Color(image_enhanced)
image_enhanced = enhancer.enhance(saturation)
enhanced_image_np = np.array(image_enhanced) / 255.0  # Normalize back to [0, 1] range

fig = plt.figure(figsize=(7, 7))
ax = plt.subplot(projection=ccrs.PlateCarree())
extent=(dataset.longitude.min(), dataset.longitude.max(), dataset.latitude.min(), dataset.latitude.max())
ax.imshow(enhanced_image_np, extent=extent, origin='lower', transform=ccrs.PlateCarree(), alpha=1)
ax.imshow(dataset["prococcus_moana"], extent=extent, origin='lower', transform=ccrs.PlateCarree(), interpolation='none', cmap=my_cmap_blues, vmin=0, vmax=300000, alpha = .5)
ax.imshow(dataset["syncoccus_moana"], extent=extent, origin='lower', transform=ccrs.PlateCarree(), interpolation='none', cmap=my_cmap_reds, vmin=0, vmax=20000, alpha = .5)
ax.imshow(dataset["picoeuk_moana"], extent=extent, origin='lower', transform=ccrs.PlateCarree(), interpolation='none', cmap=my_cmap_greens, vmin=0, vmax=50000, alpha = .5)
plt.show()
# -


