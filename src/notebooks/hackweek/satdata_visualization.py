# ---
# jupyter:
#   kernelspec:
#     display_name: Python 3 (ipykernel)
#     language: python
#     name: python3
# ---

# # Satellite Data Visualization
#
# **Tutorial Lead:** Carina Poulin (NASA, SSAI)
#
# <div class="alert alert-success" role="alert">
#
# The following notebooks are **prerequisites** for this tutorial:
#
# - [Earthdata Cloud Access](../earthdata_cloud_access)
#
# </div>
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
# 3. [Complete Scene in True Color](#3.-Complete-Scene-in-True-Color)
# 4. [False Color for Ice Clouds](#4.-False-Color-for-Ice-Clouds)
# 5. [Phytoplankton in False Color](#5.-Phytoplankton-in-False-Color)
# 6. [Full Spectra from Global Oceans](#6.-Full-Spectra-from-Global-Oceans)
# 7. [Animation from Multiple Angles](#7.-Animation-from-Multiple-Angles)

# ## 1. Setup
#
# Begin by importing all of the packages used in this notebook. If your kernel uses an environment defined following the guidance on the [tutorials] page, then the imports will be successful.
#
# [tutorials]: https://oceancolor.gsfc.nasa.gov/resources/docs/tutorials/

# +
import os

from holoviews.streams import Tap
from PIL import Image, ImageEnhance
from xarray.backends.api import open_datatree
from matplotlib.colors import ListedColormap
import cartopy.crs as ccrs
import earthaccess
import holoviews as hv
import matplotlib.pyplot as plt
import matplotlib.pylab as pl
import numpy as np
import panel.widgets as pnw
import xarray as xr
# -

options = xr.set_options(display_expand_attrs=False)


# In this tutorial, we suppress runtime warnings that show up when calculating log for negative values, which is common with our datasets. 

# Define a function to apply enhancements, our own plus generic image enhancements from the Pillow package.

# +
def enhance(rgb, scale = 0.01, vmin = 0.01, vmax = 1.04, gamma=0.95, contrast=1.2, brightness=1.02, sharpness=2, saturation=1.1):
    """The SeaDAS recipe for RGB images from Ocean Color missions.

    Args:
        rgb: a data array with three dimensions, having 3 or 4 bands in the third dimension
        scale:
        vmin:
        vmax:
        gamma:
        contrast:
        brightness:
        sharpness:
        saturation:

    Returns:
       a transformed data array better for RGB display
    """
    rgb = rgb.where(rgb > 0)
    rgb = np.log(rgb / scale) / np.log(1 / scale)
    rgb = rgb.where(rgb >= vmin, vmin)
    rgb = rgb.where(rgb <= vmax, vmax)    
    rgb_min = rgb.min(("number_of_lines", "pixels_per_line"))
    rgb_max = rgb.max(("number_of_lines", "pixels_per_line"))
    rgb = (rgb - rgb_min) / (rgb_max - rgb_min)
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


def pcolormesh(rgb):
    fig = plt.figure()
    axes = plt.subplot()
    artist = axes.pcolormesh(
        rgb["longitude"],
        rgb["latitude"],
        rgb,
        shading="nearest",
        rasterized=True,
    )
    axes.set_aspect("equal")


# -

# [back to top](#Contents)

# ## 2. Global Oceans in True Color

# The L3M files are the nicest files, use them to introduce the "dimensions" and "coordinates" parts of an XArray dataset.

results = earthaccess.search_data(
    short_name="PACE_OCI_L3M_RRS_NRT",
    granule_name="*.MO.*.0p1deg.*",
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

# It is always a good practice to build meaningful labels into the dataset, and we'll see next
# that it can be very useful as we learn to use metadata while creating visuzalizations.
#
# For this case, we can attach another variable called "channel" and then swap it with
# "wavelength" to become the third dimension of the data array. We'll actually use these
# values for a choice of `cmap` below, just for fun.

rrs_rgb["channel"] = ("wavelength", ["Reds", "Greens", "Blues"])
rrs_rgb = rrs_rgb.swap_dims({"wavelength": "channel"})
rrs_rgb

# A complicated figure can be assembled fairly easily using the `xarray.Dataset.plot` method,
# which draws on the matplotlib package. For Level-3 data, we can specifically use `imshow`
# to visualize the RGB image on the `lat` and `lon` coordinates.

fig, axs = plt.subplots(3, 1, figsize=(8, 7), sharex=True)
for i, item in enumerate(rrs_rgb["channel"]):
    array = rrs_rgb.sel({"channel": item})
    array.plot.imshow(x="lon", y="lat", cmap=item.item(), ax=axs[i], robust=True)
    axs[i].set_aspect("equal")
fig.tight_layout()
plt.show()

rrs_rgb_enhanced = enhance(rrs_rgb)

artist = rrs_rgb_enhanced.plot.imshow(x="lon", y="lat")
plt.gca().set_aspect("equal")

# [back to top](#Contents)

# ## 3. Complete Scene in True Color

# The best product to create a high-quality true-color image from PACE is the Surface Reflectance (rhos). Cloud-masked rhos are distributed in the SFREFL product suite. If you want to create an image that includes clouds, however, you need to process a Level-1B file to Level-2 using l2gen, like we will show in the OCSSW data processing exercise.
#
# All files created by a PACE Hackweek tutorial can be found in the `/shared/pace-hackweek-2024/` folder accessible from the JupyterLab file browser. In this tutorial, we'll use a Level-2 file created in advance. Note that the JupyterLab file browser treats `/home/jovyan` (that's your home directory, Jovyan) as the root of the browsable file system.

path = "/home/jovyan/shared/pace-hackweek-2024/PACE_OCI.20240605T092137.L2_SFREFL.V2.nc"
datatree = open_datatree(path)
dataset = xr.merge(datatree.to_dict().values())
dataset

# The longitude and latitude variables are geolocation arrays, and while they are spatial
# coordinates they cannot be set as an index on the dataset because each array is itself
# two-dimensional. The rhos are not on a rectangular grid, but it is still useful to tell
# XArray what will become axis labels.

dataset = dataset.set_coords(("longitude", "latitude"))
dataset

rhos_rgb = dataset["rhos"].sel({"wavelength_3d": [645, 555, 368]})
rhos_rgb

# The most simple adjustment is normalization of the range across the three RGB channels.

rhos_rgb_max = rhos_rgb.max()
rhos_rgb_min = rhos_rgb.min()
rhos_rgb_enhanced = (rhos_rgb - rhos_rgb_min) / (rhos_rgb_max - rhos_rgb_min)

# To visualize these data, we have to use the fairly smart `pcolormesh` artists, which interprets
# the geolocation arrays as pixel centers. TODO: why the warning, though?

pcolormesh(rhos_rgb_enhanced)

# Another type of enhancement involves a logarithmic transform of the data before normalizing to the unit range.

rhos_rgb_enhanced = rhos_rgb.where(rhos_rgb > 0, np.nan)
rhos_rgb_enhanced = np.log(rhos_rgb_enhanced / 0.01) / np.log(1 / 0.01)
rhos_rgb_max = rhos_rgb_enhanced.max()
rhos_rgb_min = rhos_rgb_enhanced.min()
rhos_rgb_enhanced = (rhos_rgb_enhanced - rhos_rgb_min) / (rhos_rgb_max - rhos_rgb_min)

pcolormesh(rhos_rgb_enhanced)

# Perhaps it is better to do the unit normalization independently for each channel? We can use
# XArray's ability to use and align labelled dimensions for the calculation.

rhos_rgb_max = rhos_rgb.max(("number_of_lines", "pixels_per_line"))
rhos_rgb_min = rhos_rgb.min(("number_of_lines", "pixels_per_line"))
rhos_rgb_enhanced = (rhos_rgb - rhos_rgb_min) / (rhos_rgb_max - rhos_rgb_min)

pcolormesh(rhos_rgb_enhanced)

rhos_rgb_enhanced = rhos_rgb.where(rhos_rgb > 0, np.nan)
rhos_rgb_enhanced = np.log(rhos_rgb_enhanced / 0.01) / np.log(1 / 0.01)

# +
vmin = 0.01
vmax = 1.04

rhos_rgb_enhanced = rhos_rgb_enhanced.where(rhos_rgb_enhanced <= vmax, vmax)
rhos_rgb_enhanced = rhos_rgb_enhanced.where(rhos_rgb_enhanced >= vmin, vmin)
# -

rhos_rgb_max = rhos_rgb.max(("number_of_lines", "pixels_per_line"))
rhos_rgb_min = rhos_rgb.min(("number_of_lines", "pixels_per_line"))
rhos_rgb_enhanced = (rhos_rgb_enhanced - rhos_rgb_min) / (rhos_rgb_max - rhos_rgb_min)

pcolormesh(rhos_rgb_enhanced)

# Everything we've been trying is already built into the `enhance` function, including extra goodies from the Pillow package of generic image processing filters.

rhos_rgb_enhanced = enhance(rhos_rgb)
pcolormesh(rhos_rgb_enhanced)

rhos_rgb_enhanced = enhance(rhos_rgb, contrast=1.2, brightness=1.1, saturation=0.8)
pcolormesh(rhos_rgb_enhanced)

# [back to top](#Contents)

# ## 4. False Color for Ice Clouds

rhos_ice = dataset["rhos"].sel({"wavelength_3d": [1618, 2131, 2258]})

rhos_ice_enhanced = enhance(rhos_ice, vmin=0, vmax=0.68)

pcolormesh(rhos_ice_enhanced)

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

# [back to top](#Contents)

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
# [back to top](#Contents)

# ## 5. Full Spectra from Global Oceans


hv.extension("bokeh")

results = earthaccess.search_data(
    short_name="PACE_OCI_L3M_RRS_NRT",
    granule_name="*.MO.*.1deg.*",
)
paths = earthaccess.open(results)

dataset = xr.open_dataset(paths[-1])
def single_band(w):
    array = dataset.sel({"wavelength": w})
    return hv.Image(array, kdims=["lon", "lat"], vdims=["Rrs"]).opts(aspect="equal")


single_band(368)


def spectrum(x, y):
    array = dataset.sel({"lon": x, "lat": y}, method="nearest")
    return hv.Curve(array, kdims=["wavelength"]).redim.range(Rrs=(-0.01, 0.04))


spectrum(0, 0)

slider = pnw.DiscreteSlider(name="wavelength", options=list(dataset["wavelength"].data))
band_dmap = hv.DynamicMap(single_band, streams={"w": slider.param.value})

points = hv.Points([])
tap = Tap(source=points, x=0, y=0)
spectrum_dmap = hv.DynamicMap(spectrum, streams=[tap])

slider

(band_dmap * points + spectrum_dmap).opts(shared_axes=False)

# [back to top](#Contents)
