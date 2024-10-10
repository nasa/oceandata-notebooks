# # Title of the Tutorial
#
# **Authors:** Ian Carroll (NASA, UMBC)
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
# Parallel and Out-of-core Processing
#
# ideas
# - looking up points, potentially for matchups
# - gridding L2 granules
# - flow #1
#   - read a seabass file with point information
#   - search for granules that contain points
#   - join pixel values with seabass data
# - flow #2
#   - get granules
#   - grid/interpolate them
#     - aggregation with rolling or groupby?
#     - do it with lots of granules?
#
# - questions
#   - what does cartopy do, when projecting, given swath data with transform=PlateCaree?
#   - and how does that differ from pyresample
#   - is a dask array cached? how can you tell?
#
# ## Learning Objectives
#
# At the end of this notebook you will know:
#
# - How to ...
# - What ...
#
# ## Contents
#
# 1. [Introduction](#intro)
# 1. [Setup](#setup)
#
# <a name="intro"></a>

# ## 1. Introduction
#
# **Compiled Functions**
#
# doing things in loops, and doing things with numba just-in-time compiled functions in loops, vs arrays
#
# introduces notion of compiled vs interpreted evaluation, and reason for doing everything in arrays (no need for numba)
#
# **Task Graph**
#
# Consider introducing this notion first, and using it to expalain parallel and larger-than memory in the same language.
#
#
#
# **Parallel**
#
# parallel can (and usually does in data processing) mean evaluating the same code on different inputs. our loop above (but not all loops) are a good example of "evaluating the same code on different inputs".
#
# parallel will obviously speed things up but you have to have the resources to do it
# - number of tasks
# - memory per task
#
# intrinsically this introduces the notion of a "queue" if you introduce more tasks than your system can run simultaneously, due to resource limitations
#
# just a long running computation, or maybe looping through some computation on granules without chunks
#
# could use as an opportunity to set up resampling without dask
#
# parallelize with dask bag, or njit? what's the problem here? you still have to manage memory carefully and not ask for more threads than your system can handle
#
# **Memory**
#
# parallel with queuing allows larger-than-memory computation
#
# numpy random
#
# dask.array random

# **get out of the way now**
# - `%%time` and `%%timeit`
# - `logging`

# ## 2. Setup
#
# Begin by importing all of the packages used in this notebook. If your kernel uses an environment defined following the guidance on the [tutorials] page, then the imports will be successful.
#
# [tutorials]: https://oceancolor.gsfc.nasa.gov/resources/docs/tutorials/

# +
import logging

from dask.distributed import Client
from numba import njit
import dask.array as da
import earthaccess
import numpy as np
import xarray as xr
# -

# Turn on informational alerts from `earthaccess`, because we are still learning what it's
# doing. There is no need for the cell below, or `import logging` above, if you do not want
# these alerts.

logging.basicConfig()
logging.getLogger("earthaccess").setLevel(logging.INFO)

# Use a fixed but unique seed, such as your social security number or `secrets.randbits(64)`.

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
bbox = (-76.75, 36.97, -75.74, 39.01)
results = earthaccess.search_data(
    short_name="PACE_OCI_L2_AOP_NRT",
    temporal=tspan,
    bounding_box=bbox,
)


# [back to top](#contents) <a name="section-name"></a>

# ## x. Compiled Functions
#
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

# +
# %%timeit

mean_and_std(array)
# -

# On this system, the baseline implementation takes between 2 and 3 milliseconds.

compiled_mean_and_std = njit(mean_and_std)

compiled_mean_and_std(array)

# +
# %%timeit

compiled_mean_and_std(array)

# +
# %%timeit

array.mean(), array.std(ddof=1)
# -

# lessons learned
# - numpy is fast because it uses efficient, compiled code to do array operations
# - sure, you might be able to beat numpy with numba ... was it worth the coding time, and can you write a numerically stable algorithm (the one above is not).
# - numba is not going to help us with larger-than-memory computations

# ## x. Task Graph
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

dask_array = dask_random.normal(1, 2, size=2**29, chunks="16 MiB")
dask_array

dask_array.mean()

# +
# %%timeit

mean = dask_array.mean().compute()
# -

# We just demonstrated two ways of doing larger-than-memory calculations.
#
# Our synchronous implemenation (using a for loop) took the strategy of maximizing the use of available memory while processing one chunk: so we used 1 GiB chunks, requiring 4 chunks to get to a 4 GiB array.
#
# Our concurrent implementation (using `dask.array`), took the strategy of maximizing the use of available processors: so we used small chunks of 16 MiB, requiring 256 chunks to get to a 4 GiB array.
#
# The concurrent implementation was about twice as fast.

client.close()

# ## x. Parallel Processing
#
# Enough hokey examples, lets process some data ...

client = Client(processes=False)
client



# ## Scratch

# ### ocssw tools projection

# +
import os

import earthaccess
import import_ipynb
# -

import common

??common.write_par

os.environ.setdefault("OCSSWROOT", "/Users/icarroll/Applications/SeaDAS/ocssw")

tspan = ("2024-07-01", "2024-07-31")
bbox = (-76.75, 36.97, -75.74, 39.01)
clouds = (0, 50)
results = earthaccess.search_data(
    short_name="PACE_OCI_L2_BGC_NRT",
    temporal=tspan,
    bounding_box=bbox,
    cloud_cover=clouds,
)
paths = earthaccess.download(results, local_path="L2_BGC")

results[2]

ifile = "L2_BGC/PACE_OCI.20240715T174440.L2.OC_BGC.V2_0.NRT.nc"
ofile = ifile.replace("L2", "L3b")
par = {
    "ifile": ifile,
    "ofile": ofile,
    "l3bprod": "chlor_a",
    "prodtype": "regional",
    "resolution": "QD",
}
common.write_par("l2bin-chlor_a.par", par)

# + language="bash"
# source $OCSSWROOT/OCSSW_bash.env
#
# l2bin par=l2bin-chlor_a.par
# -

ifile = ofile
ofile = ifile.replace("L3b", "L3m")
par = {
    "ifile": ifile,
    "ofile": ofile,
}
common.write_par("l3mapgen-chlor_a.par", par)

# + language="bash"
# source $OCSSWROOT/OCSSW_bash.env
#
# l2bin par=l2bin-chlor_a.par par=c-chlor_a.par
# -

ofile = "granules/PACE_OCI.L3B.nc"
par = {
    "ifile": "l2bin_ifile.txt",
    "ofile": ofile,
    "prodtype": "regional",
    "resolution": 9,
    "flaguse": "NONE",
    "rowgroup": 2000,
}
write_par("l2bin.par", par)

# gdalwarp using control point array, osgeo?

# +
import xarray as xr
import numpy as np
import rioxarray
from cartopy import crs

import geoviews as gv
gv.extension("bokeh")
# -

ds = xr.DataArray(
    data=np.linspace(0, 1, 90*180).reshape((90, 180)),
    coords={"lat": np.arange(90), "lon": np.arange(180)},
    name="demo",
)
ds = ds.rio.write_crs(4326)
ds = ds.rio.set_spatial_dims("lon", "lat")
ds = ds.rio.write_coordinate_system()
ds

import rasterio

# ah, so the geoloc arrays for rasterio is unreleased, great

from osgeo import gdal_array

from osgeo import gdal

gdal.WarpOptions(geoloc=True)

# but going all the way to gdal seems really hard. also, seems like it wants something on disk, so that's going to make dask hard.

# just try to use KDTree on my own? maybe go back to satPy? idea
# there was to do resampling on viirs_sdr, then replicate without satpy.

gds = gv.Dataset(ds, crs=ds_crs)

gv.Image(gds, ["lon", "lat"])

rds = (
    ds
    .rio.write_crs(ds_crs.to_wkt())
    .rio.set_spatial_dims("lon", "lat")
    .rio.write_coordinate_system()
)
rds

ds = xr.open_dataset("RGB.nc", decode_coords="all").load()
ds

ds.rio.crs

rds = xr.open_dataset("RGB.byte.tif", engine="rasterio").load()
rds

rds.rio.crs





results = results[:10] # DEBUG

paths = earthaccess.open(results)

dataset = xr.open_dataset(paths[0])
obs = xr.open_dataset(paths[0], group="geophysical_data")
sen = xr.open_dataset(paths[0], group="sensor_band_parameters")
geo = xr.open_dataset(paths[0], group="navigation_data").set_coords(("longitude", "latitude"))
dataset = xr.merge((dataset, obs, sen.coords, geo.coords))
dataset

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
