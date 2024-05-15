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

# TO DO LIST
# - [ ] outline
# - [ ] table of contents
# - [ ] SPEXOne stuff
# - [ ] add more inline comments to all code blocks
# - [ ] linting?

# <table><tr>
#
#
# <td> <img src="https://oceancolor.gsfc.nasa.gov/images/ob-logo-svg-2.svg" alt="Drawing" align='right', style="width: 240px;"/> </td>
#
# <td> <img src="https://upload.wikimedia.org/wikipedia/commons/thumb/e/e5/NASA_logo.svg/2449px-NASA_logo.svg.png" align='right', alt="Drawing" style="width: 70px;"/> </td>
#
# </tr></table>

# TO DO: update this once there are filenames for the other notebooks
# <a href="../Index.ipynb"><< PLACEHOLDER</a> | <a href="../Index.ipynb">PLACEHOLDER >></a>

# <font color="dodgerblue">**Ocean Biology Processing Group**</font> <br>
# **Copyright:** 2024 NASA OBPG <br>
# **License:** MIT <br>
# **Authors:** Sean Foley (NASA/MSU), Meng Gao (NASA/SSAI)

# <div class="alert alert-block alert-warning">
#     
# <b>PREREQUISITES</b> 
#     
# This notebook has the following prerequisites:
# - **<a href="https://urs.earthdata.nasa.gov/" target="_blank"> An Earthdata Login account</a>** is required to access data from the NASA Earthdata system, including NASA ocean color data.
# - Familiarity with notebook "1_PACE_data_access" is recommended before using this notebook
#
# </div>
# <hr>

# # 4. Visualize PACE's multi-angle polarimeter data
#
# ## Learning objectives
#
# At the end of this notebook you will know:
#
# * How to acquire data from both of the multi-angle polarimeters on PACE (HARP2 and SPEXone)
# * How to plot the geolocated imagery (Level 1C)
# * Some basic concepts about polarization
# * How to make animations of multi-angle data
#
# ### Outline
# TO DO: update before PR
#
# <div class="alert alert-info" role="alert">
#
# ## <a id='TOC_TOP'>Contents
#
# </div>
#     
#  1. TO DO: update before PR
#
# <hr>

# First, we import the libraries we will need:

# +
import os
from pathlib import Path
import shutil
import warnings

# TO DO: final check on dependencies, update environment.yml
from apng import APNG
import cartopy.crs as ccrs
import earthaccess
import imageio
import matplotlib.pyplot as plt
import matplotlib.ticker as mticker
from netCDF4 import Dataset
import numpy as np
from tqdm.notebook import tqdm
import xarray as xr
# -

# Next, we will download some HARP2 Level 1C data. Level 1C corresponds to geolocated imagery. This means the imagery coming from the satellite has been calibrated and assigned to locations on the Earth's surface. Note that this might take a while, depending on the speed of your internet connection, and the progress bar will seem frozen because we're only downloading one file.
#
# For more details on how to use earthaccess, see notebook [1_PACE_data_access](./1_PACE_data_access.ipynb).

# +
auth = earthaccess.login()
if not auth.authenticated:
    auth.login(strategy="interactive", persist=True)

date_range = ("2024-04-22", "2024-04-22")  # Earth Day :)
results = earthaccess.search_data(
    short_name = "PACE_HARP2_L1C_SCI",  # PACE HARP2 Level 1C science data
    cloud_hosted = True,
    temporal = date_range,
    count=10,
)
downloaded_files = earthaccess.download(
    results[0],
    local_path='storage/',
)
# harp_nc = Dataset(Path(downloaded_files[0]))
groups = [None, 'sensor_views_bands', 'bin_attributes', 'geolocation_data', 'observation_data']
harp_data = xr.merge([xr.open_dataset(downloaded_files[0], group=g) for g in groups])
# -

# ## HARP2 L1C: Understanding the Data
#
# HARP2 data has 4 spectral bands, which roughly correspond to green, red, near infrared (NIR), and blue (in that order). The red band has 60 angles, while the green, blue, and NIR bands each have 10.

# +
# TO DO: make these plots prettier and colorblind friendly
angles = harp_data["sensor_view_angle"]
wavelengths = harp_data["intensity_wavelength"]
arange = np.arange(angles.shape[0])

fig, axs = plt.subplots(2, 1, figsize=(16, 7))
axs[0].set_ylabel("View Angle (degrees)")
axs[0].set_xlabel("Index")
axs[1].set_ylabel("Wavelength (nm)")
axs[1].set_xlabel("Index")
for (start_idx, end_idx, color, label) in [(0, 10, 'green', 'green'), (10, 70, 'red', 'red'), (70, 80, 'black', 'NIR'), (80, 90, 'blue', 'blue')]:
    axs[0].plot(arange[start_idx:end_idx], angles[start_idx:end_idx], color=color, label=label)
    axs[1].plot(arange[start_idx:end_idx], wavelengths[start_idx:end_idx, 0], color=color, label=label)
axs[0].legend();
axs[1].legend();
# -

# Both of the multi-angle polarimeters are sensitive to the polarization of light. Polarization describes the geometric orientation of the oscillation of light waves. Randomly polarized light (like light coming directly from the sun) has an approximately equal amount of waves in every orientation. When light reflects of certain surfaces, it can become nonrandomly polarized.
#
# Polarimetric data is typically represented using [Stokes vectors](https://en.wikipedia.org/wiki/Stokes_parameters). These have four components: I, Q, U, and V. HARP2 and SPEXone are only sensitive to linear (and not circular) polarization. Since the V component corresponds to circular polarization, the data only includes the I, Q, and U elements of the Stokes vector.
#
# Let's make a plot of the I, Q, and U components of our Stokes vector, using the RGB channels, which will help our eyes make sense of the data. We'll use the view that is closest to pointing straight down, which is called the 'nadir' view in the code. It is important to understand that, because HARP2 is a pushbroom sensor with a wide swath, the sensor zenith angle at the edges of the swath will still be high. It's only really a 'nadir' view close to the center of the swath. Still, the average sensor zenith angle will be lowest in this view.)
#
# There's a lot going on in this code, so make sure to read the inline comments if you want a thorough understanding.

# +
# get the I, Q, and U components of the Stokes vector out of the netCDF data.
# The [..., 0] gets rid of the extra axis at the end. You can instead use [:] to pull out the array in its original shape.
i_stokes = harp_data["i"][..., 0].to_masked_array()
q_stokes = harp_data["q"][..., 0].to_masked_array()
u_stokes = harp_data["u"][..., 0].to_masked_array()

# The first 10 channels are green, the next 60 channels are red, and the final 10 channels are blue (we're skipping NIR)
# In each of those groups of channels, we get the index of the minimum absolute value of the camera angle, corresponding to our nadir view
green_nadir_idx = np.argmin(np.abs(angles[:10].values))
red_nadir_idx = 10 + np.argmin(np.abs(angles[10:70].values))
blue_nadir_idx = 80 + np.argmin(np.abs(angles[80:].values))

# Then, get the data at the nadir indices.
rgb_i, rgb_q, rgb_u = [arr[:, :, (red_nadir_idx, green_nadir_idx, blue_nadir_idx)] for arr in [i_stokes, q_stokes, u_stokes]]
# Apply some very simple adjustments to make the image easier to visualize.
rgb_i, rgb_q, rgb_u = [(arr - arr.min()) / (arr.max() - arr.min()) for arr in [rgb_i, rgb_q, rgb_u]]  # normalize the data between 0 and 1
rgb_i, rgb_q, rgb_u = [arr ** (3/4) for arr in [rgb_i, rgb_q, rgb_u]]  # bring out some of the darker colors

# Get latitude and longitude to use for the map projection.
lat = harp_data['latitude'].values
lon = harp_data['longitude'].values

# Get a mask of valid latitudes / longitudes to crop the plots later.
valid_lon = lon[~(rgb_i.mask.all(axis=-1))]
valid_lat = lat[~(rgb_i.mask.all(axis=-1))]

# Set up the figure and subplots using a plate carree projection.
projection = ccrs.PlateCarree(central_longitude=0)
# Creates a figure with 1 row and 3 columns, a fitting figsize for many screens, and uses the projection defined above.
fig, axs = plt.subplots(1, 3, figsize=(16,5),subplot_kw={'projection':projection})
# Iterate through the I, Q, and U arrays.
for i, (arr, title) in enumerate([(rgb_i, 'I'), (rgb_q, 'Q'), (rgb_u, 'U')]):
    # draw some latitude/longitude gridlines with increments of 10
    gl = axs[i].gridlines(draw_labels=True, linestyle='--',
                          xlocs=mticker.FixedLocator(np.arange(-180,180.1,10)),
                          ylocs=mticker.FixedLocator(np.arange(-90,90.1,10)))
    gl.top_labels, gl.right_labels = False, False
    with warnings.catch_warnings():
        warnings.filterwarnings("ignore", message="invalid value encountered in cast", category=RuntimeWarning, module='numpy')
        arr = (255 * arr).astype(np.uint8)
    # This line actually plots the data, but you have to convert the arrays to unsigned 8-bit integers first (0-255).
    axs[i].pcolormesh(lon, lat, arr, transform=projection);
    axs[i].coastlines(color='grey')  # draw coastlines
    # Crop the data using our valid latitude/longitude from earlier, with 1 degree of padding
    axs[i].set_xlim(max(-180, valid_lon.min() - 1), min(180, valid_lon.max() + 1))
    axs[i].set_ylim(max(-90, valid_lat.min() - 1), min(90, valid_lat.max() + 1))
    axs[i].set_title(title)

fig.suptitle(f"{harp_data.product_name} RGB");
# -

# It's pretty plain to see that the I plot makes sense to the eye: we can see clouds over the Pacific Ocean (this scene is south of the Cook Islands and east of Australia). This is because the I component of the Stokes vector corresponds to the total intensity. In other words, this is roughly what your eyes would see. However, the Q and U plots don't quite make as much sense to the eye. We can see that there is some sort of transition in the middle, which is the satellite track. This transition occurs in both plots, but is stronger in Q. This gives us a hint: the type of linear polarization we see in the scene depends on the angle with which we view the scene.
#
# [This Wikipedia plot](https://upload.wikimedia.org/wikipedia/commons/3/31/StokesParameters.png) is very helpful for understanding what exactly the Q and U components of the Stokes vector mean, exactly. Basically, Q describes how much the light is oriented in -90&deg;/90&deg; vs. 0&deg;/180&deg;, while U describes how it's oriented in -135&deg;/45&deg; vs. -45&deg;/135&deg;.
#
# Next, let's take a look at the degree of linear polarization (DoLP).
#
#
# TO DO: pick a better scene and explain it

# +
dolp = harp_data["dolp"][..., 0].to_masked_array()
rgb_dolp = dolp[:, :, (red_nadir_idx, green_nadir_idx, blue_nadir_idx)]

# Creates a figure with 1 row and 2 columns, a fitting figsize for many screens, and uses the projection defined above.
fig, axs = plt.subplots(1, 2, figsize=(16,8),subplot_kw={'projection':projection})

# Iterate through the I and DoLP arrays.
for i, (arr, title) in enumerate([(rgb_i, 'I'), (rgb_dolp, 'DoLP')]):
    # draw some latitude/longitude gridlines with increments of 10
    gl = axs[i].gridlines(draw_labels=True, linestyle='--',
                          xlocs=mticker.FixedLocator(np.arange(-180,180.1,10)),
                          ylocs=mticker.FixedLocator(np.arange(-90,90.1,10)))
    gl.top_labels, gl.right_labels = False, False
    # This line actually plots the data, but you have to convert the arrays to unsigned 8-bit integers first (0-255).
    with warnings.catch_warnings():
        warnings.filterwarnings("ignore", message="invalid value encountered in cast", category=RuntimeWarning, module='numpy')
        arr = (255 * arr).astype(np.uint8)
    axs[i].pcolormesh(lon, lat, arr, transform=projection);
    axs[i].coastlines(color='grey')  # draw coastlines
    # Crop the data using our valid latitude/longitude from earlier, with 1 degree of padding
    axs[i].set_xlim(max(-180, valid_lon.min() - 1), min(180, valid_lon.max() + 1))
    axs[i].set_ylim(max(-90, valid_lat.min() - 1), min(90, valid_lat.max() + 1))
    axs[i].set_title(title)

fig, ax = plt.subplots(figsize=(16, 6))
wv_uq = np.unique(wavelengths.values[..., 0])
colors = ['b', 'g', 'r', 'black']
for wv_idx in range(4):
    wv = wv_uq[wv_idx]
    wv_mask = wavelengths.values[..., 0] == wv
    dolp_mean = np.reshape(dolp, (-1, dolp.shape[-1])).mean(axis=0)
    ax.plot(angles.values[wv_mask], dolp_mean[wv_mask], '.-', label=str(wv), color=colors[wv_idx])
ax.legend()
ax.set_xlabel("Nominal view angle ($\\circ$)")
ax.set_ylabel("DoLP")
ax.set_title("Mean DoLP by view angle");
# -

# ## Radiance to Reflectance
#
# We can convert radiance into reflectance. TO DO

# +
f0 = harp_data['intensity_f0'].to_masked_array()[:, 0]
sza = harp_data['solar_zenith_angle'].to_masked_array()
r_sun_earth = np.float32(harp_data.sun_earth_distance)

def rad_to_refl(rad, f0, sza, r):
    """Convert radiance to reflectance.
    Args:
        rad: Radiance.
        f0: Solar irradiance.
        sza: Solar zenith angle.
        r: Sun-Earth distance (in AU).

    Returns: Reflectance.
    """
    return (r**2) * np.pi * rad / np.cos(sza * np.pi / 180) * f0[None, None]

refl = rad_to_refl(i_stokes, f0, sza, r_sun_earth)

fig, axs = plt.subplots(1, 2, figsize=(16, 8))
axs[0].imshow(i_stokes[..., red_nadir_idx], cmap='gray')
axs[0].set_title("Radiance")
axs[1].imshow(refl[..., red_nadir_idx], cmap='gray')
axs[1].set_title("Reflectance");

fig, ax = plt.subplots(figsize=(16, 6))
wv_uq = np.unique(wavelengths.values[..., 0])
colors = ['b', 'g', 'r', 'black']
for wv_idx in range(4):
    wv = wv_uq[wv_idx]
    wv_mask = wavelengths.values[..., 0] == wv
    refl_mean = np.reshape(refl, (-1, refl.shape[-1])).mean(axis=0)
    ax.plot(angles.values[wv_mask], refl_mean[wv_mask], '.-', label=str(wv), color=colors[wv_idx])
ax.legend()
ax.set_xlabel("Nominal view angle ($\\circ$)")
ax.set_ylabel("Reflectance")
ax.set_title("Mean reflectance by view angle");
# -

# ## HARP2: Animating the Multi-angle Data

# All that is great for looking at a single angle at a time, but it doesn't capture the multi-angle nature of the instrument. Multi-angle data innately captures information about 3D structure. To get a sense of that, we'll make an animation of the scene with the 60 viewing angles available for the red band.
#
# WARNING: there is some mild flickering in the animation generated by the next code block.

anim = APNG()
with warnings.catch_warnings():
    warnings.filterwarnings("ignore", message="invalid value encountered in cast", category=RuntimeWarning, module='numpy')
    refl_int = (255 * refl).astype(np.uint8)
frames = [refl_int[..., idx] for idx in range(10, 70)]
frames += frames[1:][::-1]
os.makedirs('temp_frames', exist_ok=True)
for idx, frame in enumerate(frames):
    frame_filename = f'temp_frames/{idx:04d}.png'
    imageio.imwrite(frame_filename, frame)
    anim.append_file(frame_filename, delay=idx)
anim.save(f"images/harp2_red_anim_{harp_data.product_name.split('.')[1]}.png")
shutil.rmtree('temp_frames');

# Check it out!
#
# ![alt text](images/harp2_red_anim_20240421T235519.png "Title")










