# # Visualize Data from the Spectro-polarimeter for Planetary Exploration one (SPEXone)
#
# **Authors:** Sean Foley (NASA, MSU), Meng Gao (NASA, SSAI), Ian Carroll (NASA, UMBC)
#
# > **PREREQUISITES**
# >
# > This notebook has the following prerequisites:
# > - An **<a href="https://urs.earthdata.nasa.gov/" target="_blank">Earthdata Login</a>**
# >   account is required to access data from the NASA Earthdata system, including NASA ocean color data.
# > - Learn with OCI: <a href="https://oceancolor.gsfc.nasa.gov/resources/docs/tutorials/notebooks/oci_data_access/" target="_blank">Data Access</a>
#
# ## Summary
#
# PACE has two Multi-Angle Polarimeters (MAPs): [SPEXone](https://pace.oceansciences.org/spexone.htm) and [HARP2](https://pace.oceansciences.org/harp2.htm). These sensors offer unique data, which is useful for its own scientific purposes and also complements the data from OCI. Working with data from the MAPs requires you to understand both multi-angle data and some basic concepts about polarization. This notebook will walk you through some basic understanding and visualizations of multi-angle polarimetry, so that you feel comfortable incorporating this data into your future projects.
#
# ## Learning Objectives
#
# At the end of this notebook you will know:
#
# * How to acquire data from SPEXone
# * How to plot geolocated imagery
# * Some basic concepts about polarization
# * How to make animations of multi-angle data
#
# <a name="toc"></a>
# ## Contents
#
# 1. [Setup](#setup)
# 1. [Get Level-1C Data](#data)
# 1. [Understanding Multi-Angle Data](#multiangle)
# 1. [Understanding Polarimetry](#polarimetry)
# 1. [Radiance to Reflectance](#reflectance)
# 1. [Animating an Overpass](#animation)
#
# <a name="setup"></a>
# ## 1. Setup
#
# Begin by importing all of the packages used in this notebook. If your kernel uses an environment defined following the guidance on the [tutorials] page, then the imports will be successful.
#
# [tutorials]: https://oceancolor.gsfc.nasa.gov/resources/docs/tutorials/ 

# +
from pathlib import Path
from tempfile import TemporaryDirectory

from scipy.ndimage import gaussian_filter1d
from matplotlib import animation
import cartopy.crs as ccrs
import earthaccess
import matplotlib.pyplot as plt
import numpy as np
import xarray as xr


# -

# The radiances collected by SPEXone often need to be converted, using additional properties, to reflectances. Write a function for anything you'll repeat like this.


def rad_to_refl(rad, f0, sza, r):
    """Convert radiance to reflectance.
    
    Args:
        rad: Radiance.
        f0: Solar irradiance.
        sza: Solar zenith angle.
        r: Sun-Earth distance (in AU).

    Returns: Reflectance.
    """
    return (r**2) * np.pi * rad / np.cos(sza * np.pi / 180) / f0


# [Back to top](#toc)
# <a name="data"></a>
# ## 2. Get Level-1C Data
#
# Download some SPEXone Level-1C data using the `short_name` value "PACE_SPEXONE_L1C_SCI" in `earthaccess.search_data`. Level-1C corresponds to geolocated imagery. This means the imagery coming from the satellite has been calibrated and assigned to locations on the Earth's surface. Note that this might take a while, depending on the speed of your internet connection, and the progress bar will seem frozen because we're only downloading one file.

auth = earthaccess.login(persist=True)

tspan = ("2024-05-20", "2024-05-20")
results = earthaccess.search_data(
    short_name="PACE_SPEXONE_L1C_SCI",
    temporal=tspan,
    count=1,
)

paths = earthaccess.open(results)

prod = xr.open_dataset(paths[0])
obs = xr.open_dataset(paths[0], group="observation_data")
view = xr.open_dataset(paths[0], group="sensor_views_bands")
geo = xr.open_dataset(paths[0], group="geolocation_data")

# The `prod` dataset, as usual for OB.DAAC products, contains attributes but no variables. Merge it with the "observation_data" and "geolocation_data", setting latitude and longitude as auxiliary (e.e. non-index) coordinates, to get started.

dataset = xr.merge((prod, obs, geo))
dataset = dataset.set_coords(["longitude", "latitude"])
dataset

# [Back to top](#toc)
# <a name="multiangle"></a>
# ## 2. Understanding Multi-Angle Data
#
# SPEXone is a hyper-spectral sensor with 400 intensity bands (380-779nm) and 50 polarization bands (within 385-770nm).  SPEXone is also multi-angle, reading at five view angles for all its spectral bands. The "number_of_views" dimension in the Level-1C format is introduced for compatibility between HARP2 and SPEXone, providing a uniform way to handle "channels" that differ in  *either* angle *or* wavelength. A result is that we don't have a coordinate (with an index) for intensity or polarization wavelengths, but we can mark the releavant variables as auxiliary (i.e. non-indexed) coordinates. The "number_of_views" dimension can, however, be indexed by a "sensor_view_angles" coordinate. Embed these relationships in the `dataset` object by changing the "sensor_view_angle" variable to a coordinate and an index in `view`, setting the wavelength variables to coordinates without an index, and then merging the result with the existing `dataset`.

view = view.set_coords(
    (
        "sensor_view_angle",
        "intensity_wavelength",
        "polarization_wavelength",
    )
)
view = view.set_xindex("sensor_view_angle")
dataset = xr.merge((dataset, view))

# [Back to top](#toc)
# <a name="polarimetry"></a>
# ## 3. Understanding Polarimetry
#
# Both HARP2 and SPEXone conduct polarized measurements. Polarization describes the geometric orientation of the oscillation of light waves. Randomly polarized light (like light coming directly from the sun) has an approximately equal amount of waves in every orientation. When light reflects off certain surfaces or is scattered by small particles, it can become non-randomly polarized.
#
# Polarimetric data is typically represented using [Stokes vectors][stokes]. These have four components: I, Q, U, and V. Both HARP2 and SPEXone are only sensitive to linear polarization, and do not detect circular polarization. Since the V component corresponds to circular polarization, the data only includes the I, Q, and U elements of the Stokes vector.
#
# The I, Q, and U components of the Stokes vector are separate variables in `dataset`.
#
# [stokes]: https://en.wikipedia.org/wiki/Stokes_parameters

dataset[["i", "q", "u"]]

# Examine the dimensions of each Stokes component. The first three dimensions are the positions along track, the position in the cross track direction, and the view angles. Note that the fourth dimension for I is different from that for Q and U. The 400 wavelengths for intensity differ from the 50 wavelengths for polarization.
#
# Let's make a plot of the I, Q, and U components of our Stokes vector as well as the degree of linear polarization (DoLP), using RGB wavelengths to help our eyes make sense of the data. We'll use the sensor view angle that is closest to pointing straight down, which is nominally the "nadir" view. Since the SPEXone swath is relatively narrow (100km), the sensor zenith angle at the edges of the swath is only slightly higher, but the only true nadir view is still at the center of the swath.
#
# Once we've chosen a single sensor view angle, we can now also add an index for each wavelength coordinate.

nadir = dataset.sel({"sensor_view_angle": 0})
nadir = (
    nadir
    .set_xindex("intensity_wavelength")
    .set_xindex("polarization_wavelength")
)
nadir

# Narrow the two wavelength dimensions down by selecting RGB bands at around 665, 550, and 440nm.

nadir_rgb = nadir[["i", "dolp", "q", "u"]].sel(
    {
        "intensity_wavelength": [665, 550, 440],
        "polarization_wavelength": [665, 550, 440],
    },
    method="nearest",
)

# The dimensions of variables within the dataset are now suitable for visualization as images!

dict(nadir_rgb.sizes)

# A small adjustment makes the image easier to visualize. Normalize the data between 0 and 1, and then bring out some of the darker colors by raising the normalized data to a power a little smaller than one.

nadir_rgb = ((nadir_rgb - nadir_rgb.min()) / (nadir_rgb.max() - nadir_rgb.min())) ** (3 / 4)

# The figure will hav 2 rows and 2 columns, for the I, Q, U, and DoLP arrays, spanning a width suitable for many screens. The latitude and longitude coordinates, while not gridded, can be mapped using the "Plate Carree" coordinate reference system.

crs_data = ccrs.PlateCarree()

# +
fig, ax = plt.subplots(2, 2, figsize=(8, 10), subplot_kw={"projection": crs_data})
fig.suptitle(f'RGB: {prod.attrs["product_name"]}')

for i, item in enumerate(("i", "dolp", "q", "u")):
    array = nadir_rgb[item].dropna("bins_along_track", how="all")
    ax[i//2, i%2].pcolormesh(array["longitude"], array["latitude"], array)
    ax[i//2, i%2].gridlines(draw_labels={"bottom": "x", "left": "y"}, linestyle="--")
    ax[i//2, i%2].set_title(item.upper())

plt.show()
# -

# It's pretty plain to see that the I and DoLP plots make sense to the eye: we can see clouds over the Pacific Ocean (this scene is south of the Cook Islands and east of Australia). This is because the I component of the Stokes vector corresponds to the total intensity. In other words, this is roughly what your eyes would see.
#
# Take a look now at Q and U. Unlike the I component, the Q and U plots don't quite make as much sense to the eye. We can see that there is some sort of transition in the middle, which is the satellite track. This transition occurs in both plots, but is stronger in Q. This gives us a hint: the type of linear polarization we see in the scene depends on the angle with which we view the scene.
#
# [This Wikipedia plot](https://upload.wikimedia.org/wikipedia/commons/3/31/StokesParameters.png) is very helpful for understanding what exactly the Q and U components of the Stokes vector mean. Q describes how much the light is oriented in -90°/90° vs. 0°/180°, while U describes how much light is oriented in -135°/45°; vs. -45°/135°.

# DoLP line plot

dolp = dataset["dolp"].mean(["bins_along_track", "bins_across_track"])
dolp = (dolp - dolp.min()) / (dolp.max() - dolp.min())

fig, ax = plt.subplots(figsize=(14, 5))
dolp.plot.scatter(x="sensor_view_angle", hue="polarization_wavelength", cmap="rainbow", ax=ax)
ax.set_xlabel("Nominal View Angle (°)")
ax.set_ylabel("DoLP")
ax.set_title("Mean DoLP by View Angle")
plt.show()

# [Back to top](#toc)
# <a name='reflectance'></a>
# ## 4. Radiance to Reflectance
#
# We can convert radiance into reflectance. For a more in-depth explanation, see [here](https://seadas.gsfc.nasa.gov/help-9.0.0/rad2refl/Rad2ReflAlgorithmSpecification.html#:~:text=Radiance%20is%20the%20variable%20directly,it%2C%20and%20it%20is%20dimensionless). This conversion compensates for the differences in appearance due to the viewing angle and sun angle.
#
# The difference in appearance (after matplotlib automatically normalizes the data) is negligible, but the difference in the physical meaning of the array values is quite important.

refl = rad_to_refl(
    rad=dataset["i"],
    f0=dataset["intensity_f0"],
    sza=dataset["solar_zenith_angle"],
    r=float(dataset.attrs["sun_earth_distance"]),
)

nadir["refl"] = refl.sel({"sensor_view_angle": 0})
nadir_red = nadir.sel({"intensity_wavelength": 665})

# +
fig, ax = plt.subplots(1, 2, figsize=(10, 6), subplot_kw={"projection": crs_data})

for i, item in enumerate(("i", "refl")):
    array = nadir_red[item].dropna("bins_along_track", how="all")
    ax[i].pcolormesh(array["longitude"], array["latitude"], array, cmap="gray")
    ax[i].gridlines(draw_labels={"bottom": "x", "left": "y"}, linestyle="--")
    
ax[0].set_title("Radiance")
ax[1].set_title("Reflectance")
plt.show()
# -

# Create a line plot of the reflectance for each view angle and spectral channel on a selected pixel. The flatness of this plot serves as a sanity check that nothing has gone horribly wrong with our data processing.

refl_sub = refl[350, 12].sel({"intensity_bands_per_view": slice(None, None, 20)})

fig, ax = plt.subplots(figsize=(14, 5))
refl_sub.plot.scatter(x="sensor_view_angle", hue="intensity_wavelength", cmap="rainbow", ax=ax)
ax.set_xlabel("Nominal View Angle (°)")
ax.set_ylabel("Reflectance")
ax.set_title("Reflectance by View Angle")
plt.show()

# [Back to top](#toc)
# <a name='animation'>
# ## 5. A Simple Animation
#
# <div class="alert alert-info" role="alert">
#
# WARNING: there is some flickering in the animation displayed in this section.
#
# </div>
#
# All that is great for looking at a single angle at a time, but it doesn't capture the multi-angle nature of the instrument. Multi-angle data innately captures information about 3D structure. To get a sense of that, we'll make an animation of the scene with the 5 viewing angles available.

# Normalize the reflectance to lie between 0 and 1.

refl_pretty = (refl - refl.min()) / (refl.max() - refl.min())

# A very mild Gaussian filter over the angular axis will improve the animation's smoothness.

refl_pretty.data = gaussian_filter1d(refl_pretty, sigma=0.5, truncate=2, axis=2)

# Raising the image to the power 2/3 will brighten it a little bit. Cast it to an unsigned 8-bit integer so we can write it to a png later.

refl_pretty = refl_pretty ** (2 / 3)

# Append all but the first and last frame in reverse order, to get a 'bounce' effect.

frames = np.arange(refl_pretty.sizes["number_of_views"])
frames = np.concatenate((frames, frames[-2::-1]))
frames

# %matplotlib widget

# +
fig, ax = plt.subplots(subplot_kw={"projection": crs_data})
fig.canvas.header_visible = False

array = refl_pretty[{"number_of_views": 0}]
array = array.set_xindex("intensity_wavelength").sel({"intensity_wavelength": 400})
im = ax.pcolormesh(array["longitude"], array["latitude"], array, cmap="gray")
ax.gridlines(draw_labels={"bottom": "x", "left": "y"}, linestyle="--")

def update(i):
    array = refl_pretty[{"number_of_views": i}]
    array = array.set_xindex("intensity_wavelength").sel({"intensity_wavelength": 665})
    im.set_data(array)
    return im

an = animation.FuncAnimation(fig=fig, func=update, frames=frames, interval=300)
plt.show()
# -

# This scene is a great example of multi-layer clouds. You can use the parallax effect to distinguish between these layers.
#
# The [sunglint](https://en.wikipedia.org/wiki/Sunglint) is an obvious feature, but you can also make out the [opposition effect](https://en.wikipedia.org/wiki/Opposition_surge) on some of the clouds in the scene. These details would be far harder to identify without multiple angles! When it starts driving you crazy though, time to pause.

an.pause()

# But it's so mesmerizing!

an.resume()

# And once you've really had enough, call `plt.close()`.

# <div class="alert alert-info" role="alert">
#     
# You have completed the notebook giving a first look at SPEXone data. More notebooks are comming soon!
#
# </div>
