# ---
# jupyter:
#   kernelspec:
#     display_name: Python 3 (ipykernel)
#     language: python
#     name: python3
# ---

# # Parallel and Larger-than-Memory Processing
#
# **Authors:** Ian Carroll (NASA, UMBC)
#
# <div class="alert alert-success" role="alert">
#
# The following notebooks are **prerequisites** for this tutorial.
#
# - Learn with OCI: [Data Access][oci-data-access]
# - Learn with OCI: [Processing with Command-line Tools][oci-ocssw-processing]
#
# </div>
#
# <div class="alert alert-info" role="alert">
#
# An [Earthdata Login][edl] account is required to access data from the NASA Earthdata system, including NASA ocean color data.
#
# </div>
#
# ## Summary
#
# Processing the whole collection of Ocean Color Instrument (OCI) granules, or even big subsets of that collection,
# requires breaking up one big job into many small jobs. That and putting the pieces back together again. We put
# this type of pipeline in the "split-apply-combine" category. In this notebook, we are going to:
#
# 1. split a collection of Level-2 granules into groups by latitude and longitude
# 2. apply an interpolation method returning the Level-2 variables on a projected coordinate reference system
# 3. combine the gridded variables into one dataset with shared coordinates
#
# The "apply" step equates to a lot of small jobs that do not, or cannot for a large enough amount of data, be carried
# out on a computer simultaneously. Any computer has a limit on resources for processing and memory, but there are
# many tools designed to perform "split-apply-combine" pipelines that both maximize the use of these resources and can
# automatically scale the pipeline to computers, or even many computers, with a lot of resources.
#
# A tool tightly integrated with XArray that perfectly suits our needs is [Dask: a Python library for parallel and distributed computing][dask].
#
# ## Learning Objectives
#
# At the end of this notebook you will know:
#
# - How to start a `dask` client for parallel and larger-than-memory pipelines
# - One method for interpolating Level-2 "swath" data to a map projection
#
# ## Contents
#
# 1. [Setup](#1.-Setup)
# 2. [Compiled Functions](#2.-Compiled-Functions)
# 3. [Task Graphs](#3.-Task-Graphs)
# 4. [Dask Workers]
# 5. [Griddata]
#
# [edl]: https://urs.earthdata.nasa.gov
# [oci-data-access]: https://oceancolor.gsfc.nasa.gov/resources/docs/tutorials/notebooks/oci_data_access
# [oci-ocssw-processing]: https://oceancolor.gsfc.nasa.gov/resources/docs/tutorials/notebooks/oci-ocssw-processing
# [dask]: https://docs.dask.org

# ## 1. Setup
#
# Begin by importing all of the packages used in this notebook. If your kernel uses an environment defined following the guidance on the [tutorials] page, then the imports will be successful.
#
# [tutorials]: https://oceancolor.gsfc.nasa.gov/resources/docs/tutorials/

# +
import csv

from dask.distributed import Client
import dask.array as da
import earthaccess
import numba
import numpy as np
import xarray as xr


# -

def write_par(path, par):
    """
    Prepare a "par file" to be read by one of the OCSSW tools, as an
    alternative to specifying each parameter on the command line.

    Args:
        path (str): where to write the parameter file
        par (dict): the parameter names and values included in the file
    """
    with open(path, "w") as file:
        writer = csv.writer(file, delimiter="=")
        values = writer.writerows(par.items())


# Use a fixed but unique seed, such as the result of `secrets.randbits(64)`.

random = np.random.default_rng(seed=5179916885778238210)

# <div class="alert alert-info" role="alert">
#     
# The `persist=True` argument ensures any discovered credentials are
# stored in a `.netrc` file, so the argument is not necessary (but
# it's also harmless) for subsequent calls to `earthaccess.login`.
#
# </div>

auth = earthaccess.login(persist=True)

tspan = ("2024-06", "2024-06")
bbox = (-76.75, 37, -75.75, 39)
results = earthaccess.search_data(
    short_name="PACE_OCI_L2_BGC_NRT",
    temporal=tspan,
    bounding_box=bbox,
)

# - show a single chlor_a L2 example
# - show the L2 example processed with l2bin and l3mapgen

local_paths = earthaccess.download(results[:1], local_path="data")

ifile = str(local_paths[0])
ofile = ifile.replace("L2", "L3B")
par = {
    "ifile": ifile,
    "ofile": ofile,
    "prodtype": "regional",
    "l3bprod": "chlor_a",
    "flaguse": "NONE",
}
write_par("l2bin-chlor_a.par", par)

# + scrolled=true language="bash"
# source $OCSSWROOT/OCSSW_bash.env
#
# l2bin par=l2bin-chlor_a.par
# -

ifile = ofile
ofile = ifile.replace("L3B", "L3M")
par = {
    "ifile": ifile,
    "ofile": ofile,
}
common.write_par("l3mapgen-chlor_a.par", par)

# + scrolled=true language="bash"
# source $OCSSWROOT/OCSSW_bash.env
#
# l3mapgen par=l3mapgen-chlor_a.par
# -

dataset = xr.open_dataset(ofile)
dataset

# No need to use Cartopy to define axes, because the data are already projected.

artist = dataset["chlor_a"].plot.imshow(x="lon", y="lat", cmap="viridis", robust=True)

# [back to top](#contents) <a name="section-name"></a>

# ## 2. Compiled Functions
#
# Before diving in to OCI data, we should discuss two important considerations for when you are trying to improve performance (a.k.a. your processing is taking longer than you would like).
#
# 1. Am I using compiled functions?
# 2. Can I use the compiled functions in a split-apply-combine pipeline?
#
# Use the [IPython %%timeit magic][timeit] as a quick and easy way to keep track of relative performance. Begin any cell
# with `%%timeit` on a line by itself to trigger that cell to run multiple times with a timer and print a summary
# of how long it takes the cell to run.
#
# [timeit]: https://ipython.readthedocs.io/en/stable/interactive/magics.html#magic-timeit

# %%timeit
n = 10_000
x = 0
for i in range(n):
    x = x + i
x / n


# The for-loop in that example could be replaced with a compiled function that calculates the mean of a range.
# Python is an interpretted language; there is no step during evaluation that compiles code written in Python
# to a lower-level language for your operating system. However, we can call functions from packages that
# are already compiled, such as the `numpy.mean` function. In fact, we can even use the `numba` "just-in-time"
# compiler to make our own compiled functions.

# When you are interested in performance improvements for data processing, the first tool
# in your kit is compiled functions. If you use NumPy, you have already checked this box.
# However, since you may sometimes need `numba`, we're going to start with a comparison
# of functions written in and interpreted by Python with the use of compiled functions.

def mean_and_std(x):
    """Compute sample statistics with a for-loop.

    Args:
      x: One-dimensional array of numbers.

    Returns:
      A 2-tuple with the mean and standard deviation.
    """    
    # initialize sum (s) and sum-of-squares (ss)
    s = 0
    ss = 0
    # calculate s and ss by iterating over x
    for i in x:
        s += i
        ss += i**2
    # mean and std. dev. calculations
    n = x.size
    mean = s / n
    variance = (ss / n - mean ** 2) * n / (n - 1)
    return mean, variance ** (1/2)


# Confirm the function is working; it should return approximations to
# the mean and standard deviation parameters of a sample from a normal
# distribution.

array = random.normal(1, 2, size=100)
mean_and_std(array)

# The approximation isn't very good for a small sample! We are motivated
# to use a very big array, say $10^{4}$ numbers, and will compare performance
# using different tools.

array = random.normal(1, 2, size=10_000)

# %%timeit
mean_and_std(array)

# On this system, the baseline implementation takes between 2 and 3 milliseconds.

compiled_mean_and_std = numba.njit(mean_and_std)

compiled_mean_and_std(array)

# %%timeit
compiled_mean_and_std(array)

# Don't write your own though, if an existing compiled function can do what you
# need well enough!

# %%timeit
array.mean(), array.std(ddof=1)

# lessons learned
# - numpy is fast because it uses efficient, compiled code to do array operations
# - sure, you might be able to beat numpy with numba ... was it worth the coding time, and can you write a numerically stable algorithm (the one above is not).
# - numba is not going to help us with larger-than-memory computations

# ## 3. Task Graph
#
# A task graph is a collection of functions (nodes) linked through input and output data (edges).

# ```mermaid
# flowchart LR
#
# A(random.normal) -->|array| B(mean_and_std)
# ```

# The output of the `random.normal` function becomes the input to the `mean_and_std` function.
#
# When we think about performance, we have to consider
# 1. the amount of data
# 1. the resources available (typically memory and processing cores)

# We usually think about the amount of data in two categories, "small" means we can fit all the data in memory on the current system. "Big" means we cannot. Obviously this depends on the system in use, so you can't consider these two things separately!
#
# In this case, the amount of data is less than the available memory, so it's "small".

f"{array.nbytes / 2**20} MiB"

# The other resource we have to consider is how many calculations we can do concurrently, i.e. at the same time.
#
# Actually, this is all so interrelated, it's hard to describe.

# ```mermaid
# %%{ init: { 'flowchart': { 'curve': 'linear' } } }%%
#
# flowchart LR
#
# A(random.normal) -->|array| B(split)
# B -->|array_0| C0(apply-mean_and_std)
# B -->|array_1| C1(apply-mean_and_std)
# B -->|array_2| C2(apply-mean_and_std)
# subgraph SCHEDULER
# C0
# C1
# C2
# end
# C0 ---|result_0| X[ ]:::hide
# C1 ---|result_1| X
# C2 ---|result_2| X
# X --> D(combine-mean_and_std)
#
# classDef hide width:0px
# ```

# The split-apply-combine framework is everywhere in data processing; usually used for some form of group-wise calculation. Same idea here, but the split is just on slices and the apply and combine steps have to be capable of calculating results on a slice that can be combined to equal the result you would have gotten on the full array.
#
# If a computation can be put into a task graph with `spit`, `apply` and `combine`, then we can process "big" data using concurrency.
#
# If you start trying to logic through the trade-offs though, why would you do big data concurrently. That implies chopping up your big data into chunks small enough to fit in memory ... and then you can only do one chunk at a time.
#
# That's correct! But what if you had access to a distributed system?
#
# Or what if there is latency in getting the data? Ugh, I have to think more about this.

array = random.normal(1, 2, size=2**27)
print(f"{array.nbytes / 2**30} GiB")
del array

# Calculate the mean of a 4 GiB array, using 4 splits of 1 GiB arrays. Simultaneously calculating
# the standard deviation is left as an exercise for the reader.

# +
# %%timeit

n = 4
s = 0
for _ in range(n):
    array = random.normal(1, 2, size=2**27)
    s += array.mean()
    del array
mean = s / n
# -

client = Client(processes=False, memory_limit="1 GiB")
client

dask_random = da.random.default_rng(random)

# + scrolled=true
dask_array = dask_random.normal(1, 2, size=2**29, chunks="16 MiB")
dask_array
# -

dask_array.mean()

# %%timeit
mean = dask_array.mean().compute()

# We just demonstrated two ways of doing larger-than-memory calculations.
#
# Our synchronous implemenation (using a for loop) took the strategy of maximizing the use of available memory while processing one chunk: so we used 1 GiB chunks, requiring 4 chunks to get to a 4 GiB array.
#
# Our concurrent implementation (using `dask.array`), took the strategy of maximizing the use of available processors: so we used small chunks of 16 MiB, requiring 256 chunks to get to a 4 GiB array.
#
# The concurrent implementation was about twice as fast.

client.close()

# ## 4. Griddata
#
# Enough hokey examples, lets process some data ...

# ## Scratch

# ### ocssw tools projection

# +
import os

from pyproj import CRS, Transformer
from pyproj.aoi import AreaOfInterest
from scipy.interpolate import griddata
import earthaccess
import import_ipynb
import matplotlib.pyplot as plt
import numpy as np
import xarray as xr

import common
# -

??common.write_par

os.environ.setdefault("OCSSWROOT", "/tmp/ocssw")

tspan = ("2024-07-01", "2024-07-31")
bbox = (-76.75, 36.97, -75.74, 39.01)
clouds = (0, 50)
results = earthaccess.search_data(
    short_name="PACE_OCI_L2_BGC_NRT",
    temporal=tspan,
    bounding_box=bbox,
    cloud_cover=clouds,
)

results[1]

paths = earthaccess.open(results[1:2])

dataset = xr.open_dataset(paths[0])
dataset

tmp = axes.get_extent()

# ### using scipy griddata

# Do this with `griddata`, but note that the development release of rasterio includes
# reprojection using geolocation arrays. This is already in GDAL, but that's fairly low level.
# Possibly the way to go in the future once released in rasterio.

# +
from dask.distributed import Client

client = Client(processes=False)
client
# -

groups = (None, "geophysical_data", "navigation_data")
dataset = xr.merge(
    (xr.open_dataset(paths[0], group=i, chunks={}) for i in groups)
)
dataset

swath_pixels = dataset.stack({"pixels": ["number_of_lines", "pixels_per_line"]}, create_index=False)
swath_pixels

aoi = AreaOfInterest(
    west_lon_degree=dataset.attrs["westernmost_longitude"],
    south_lat_degree=dataset.attrs["southernmost_latitude"],
    east_lon_degree=dataset.attrs["easternmost_longitude"],
    north_lat_degree=dataset.attrs["northernmost_latitude"],
)

from pyproj.database import query_utm_crs_info

# + scrolled=true
crs_list = query_utm_crs_info(area_of_interest=aoi, contains=True)
for i in crs_list:
    print(i.auth_name, i.code, str(i))
    print()
# -

len(i)

CRS.from_epsg(4326)

CRS.from_epsg(3408)

t = Transformer.from_crs("EPSG:4326", "EPSG:3408") #, area_of_interest=aoi
t

x_min, y_min = t.transform(aoi.south_lat_degree, aoi.west_lon_degree)
x_min, y_min

x_max, y_max = t.transform(aoi.north_lat_degree, aoi.east_lon_degree)
x_max, y_max

# Create a dataset that has the coordinates we want, but no data (yet!).

x_size = 752 # TODO: how to choose
y_size = 468
grid_pixels = xr.Dataset({
    "x": ("x", np.linspace(x_min, x_max, x_size)),
    "y": ("y", np.linspace(y_min, y_max, y_size))
})
grid_pixels = grid_pixels.stack({"pixels": ["x", "y"]})
grid_pixels

lat, lon = t.transform(grid_pixels["x"], grid_pixels["y"], direction="INVERSE")

grid_pixels["lat"] = ("pixels", lat)
grid_pixels["lon"] = ("pixels", lon)
grid_pixels

grid_latlon = grid_pixels[["lat", "lon"]].to_dataarray().transpose()

swath_latlon = swath_pixels[["latitude", "longitude"]].to_dataarray().transpose()

values = swath_pixels["chlor_a"] # of course, we have a lot more variables, or higher dim ones

grid_values = griddata(swath_latlon, values, grid_latlon)

grid_pixels["chlor_a"] = ("pixels", grid_values)
grid_pixels

grid = grid_pixels.unstack()
grid

artist = grid["chlor_a"].plot.imshow(x="x", y="y", robust=True)

t.target_crs

fig = plt.figure()
data_proj = ccrs.UTM(17, southern_hemisphere=False)
axes = plt.axes(projection=data_proj)
artist = grid["chlor_a"].plot.imshow(x="x", y="y", robust=True, ax=axes)
axes.set_extent((x_min, x_max, y_min, y_max), crs=data_proj)
# axes.set_extent(tmp)
axes.gridlines(draw_labels={"left": "y", "bottom": "x"})
axes.coastlines()
plt.show()

grid

# gdalwarp using control point array, osgeo?

# ah, so the geoloc arrays for rasterio is unreleased, great

# but going all the way to gdal seems really hard. also, seems like it wants something on disk, so that's going to make dask hard.

# just try to use KDTree on my own? maybe go back to satPy? idea
# there was to do resampling on viirs_sdr, then replicate without satpy.



# To get a regular grid at "full resolution", we have to resample.

from scipy.spatial import KDTree

lonlat = (
    dataset[["latitude", "longitude"]]
    .reset_coords()
    .to_dataarray("coordinate")
    .stack({"pixel": ["number_of_lines", "pixels_per_line"]}, create_index=False)
    .transpose("pixel", ...)
)

index = KDTree(lonlat)

# need a grid
# need to get the lat lon of a point in the grid
# use the index on those lat lon points
# ... good lord this is tricky. and now there is 

from rasterio.warp import reproject

reproject(
    src,
    dst=None,
    src_geoloc_array, # the x and y arrays
    
    src_crs={"init": "EPSG:4326"}, # Geographic CRS
    dst_crs={"init": "EPSG:3857"}, # Projected CRS
)
# but how do I use this on 180 bands? only need to do the lookups once

# [back to top](#contents)
#
# <div class="alert alert-info" role="alert">
#
# You have completed the notebook on downloading and opening datasets. We now suggest starting the notebook on ...
#
# </div>
