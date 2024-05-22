# # Using OCSSW functions (l2gen) using Jupyter notebooks
#
# **Authors:** Carina Poulin (NASA, SSAI), Ian Carroll (NASA, UMBC), Anna Windle (NASA, SSAI)
#
# > **PREREQUISITES**
# >
# > This notebook has the following prerequisites:
# > - An **<a href="https://urs.earthdata.nasa.gov/" target="_blank">Earthdata Login</a>**
# >   account is required to access data from the NASA Earthdata system, including NASA ocean color data.
# > - You must have OCSSW installed on your server, see the "Installing OCSSW on a Jupyter Hub" notebook
# > - "Learn with OCI"/"Data Access"
#
# ## Summary
#
# [SeaDAS][seadas] is the official data analysis sofware of NASA's Ocean Biology Distributed Active Archive Center (OB. DAAC); used to process, display and analyse ocean color data. SeaDAS is a dektop application that includes SeaDAS-OCSSW, the core libraries or data processing components. There is a CLI for the SeaDAS-OCSSW data processing components, known simply as OCSSW, which we can use on a remote host without a desktop.
#
# This tutorial will show you how to process PACE OCI data on a JupyterHub server using some of the OCSSW functions. 
#
# ## Learning Objectives
#
# <a name="toc"></a>
# At the end of this notebok you will know:
# * How to process L1B data to Level 2 with `l2gen`
# * How to merge two images with `L2bin`
# * How to create a map with `l3mapgen`
#
# ## Contents
#
# 1. [Initial Setup](#setup)
# 2. [Get L1B data](#data)
# 3. [Process data with `l2gen`](#l2gen)
# 4. [Merge images with `L2bin`](#l2bin)
# 5. [Make a map with `L3mapgen`](#l3mapgen)
#      
# ## 1. Setup <a name="setup"></a> 
#
# ### Imports
#
# We begin by importing all of the packages used in this notebook. If you have created an environment following the guidance provided with this tutorial, then the imports will be successful.
#
# [seadas]: https://seadas.gsfc.nasa.gov/

# +
# Python Standard Library
import os
import pathlib

# Python Packages
import cartopy.crs as ccrs
import earthaccess
import xarray as xr
# -

# ## 2. Get OCI Level 1B data <a name="data"></a>
#

# ### Search for data
#
# Set (and persist to your user profile on the host, if needed) your Earthdata Login credentials.

auth = earthaccess.login(persist=True)

# We will use the `earthaccess` search method used in the OCI Data Access notebook. Note that L1B files do not include cloud coverage metadata, so we cannot use that filter.

tspan = ("2024-04-27", "2024-04-28")
location = (-56.53125, 49.81134)

results = earthaccess.search_data(
    short_name="PACE_OCI_L1B_SCI",
    temporal=tspan,
    point=location,
)

# TODO simpler, but why iterate for one granule?
for item in results:
    display(item)

# ### Create a directory where you will store the granules

parent = pathlib.Path("granules")
parent.mkdir(exist_ok=True)

# ### Download the granules to the folder

#FIXME is this redownloading in cloud?
paths = earthaccess.download(results, parent)
paths

# ### Visualize L1B data 

# Open the dataset using `xarray`

dataset = xr.open_dataset(paths[0], group="observation_data")
dataset

# We can have a look at the L1B dataset. At this level, geographical coordinates and band wavelenths are not available. We will need to process the file to Level 2 or 3 to get those.

plot = dataset["rhot_red"].sel({"red_bands": 100}).plot()

# ## 3. Process L1B data with `l2gen` <a name="l2gen"></a>
#
# `L2gen` will process the L1B data to L2 using the parameters you will specify for it. 

# ### Run `l2gen`

# <div class="alert alert-warning">
# OCSSW programs are run from the command line in Bash, but we can have a Bash terminal-in-a-cell using the IPython <a href="https://ipython.readthedocs.io/en/stable/interactive/magics.html#built-in-magic-commands" target=_blank>magic</a> command `%%bash`. In the specific case of OCSSW programs, the Bash environment created for that cell must be set up by loading `$OCSSWROOT/OCSSW_bash.env`.
# </div>
#
# Every `%%bash` cell which calls an OCSSW program needs to `source` the environment
# definition file shipped with OCSSW, because its effects are not retained from one cell to the next.
# We can, however, define the `OCSSWROOT` environment variable in a way that effects every `%%bash` cell.

os.environ["OCSSWROOT"] = "/tmp/ocssw"

# Then we need a couple lines, which will appear in multiple cells below, to begin a Bash cell initiated with the `OCSSW_bash.env` file.
# ```
# # %%bash
# source $OCSSWROOT/OCSSW_bash.env
# ```
#
# Using this pattern, run the `l2gen` command by itself to view the extensive list of options available. You can find more information about `l2gen` and other OCSSW functions on the [seadas website](https://seadas.gsfc.nasa.gov/help-8.3.0/processors/ProcessL2gen.html)

# + scrolled=true language="bash"
# source $OCSSWROOT/OCSSW_bash.env
#
# l2gen
# -

# To process a L1B file using `l2gen`, at a minimum, you need to set an infile name (`ifile`) and an outfile name (`ofile`). You can indicate a data suite, in this example, we will proceed with the surface reflectance suite used to make true color images (`SFREFL`).
#
# Feel free to explore `l2gen` options to produce the level 2 dataset you need. 

ifile = str(paths[0])
ofile = ifile.replace("L1B", "L2")

# + scrolled=true magic_args="-s {ifile} {ofile}" language="bash"
# source $OCSSWROOT/OCSSW_bash.env
#
# l2gen ifile=$1 ofile=$2 suite=SFREFL atmocor=1
# -

# Once this process is done, you are ready to visualize your L2 data!

# ### Visualize L2 data
#

# Open your L2 netcdf file and look at the contents

# TODO why only 50 bands?
dataset = xr.open_dataset(ofile, group="geophysical_data")
rhos = dataset["rhos"]
dataset

# Plot one wavelength from the dataset

plot = rhos.sel({"wavelength_3d": 25}).plot(cmap="viridis")

# ## 4. Merge two images with `l2bin` <a name="l2bin"></a>
#
# It can be useful to merge two images along a swath to create a single, larger image. `l2bin` is a OCSSW function that can help us do that. 
#
# ### Find and dowload L2 data
# First, let's find L2 data using the `earthaccess` library:

# +
# TODO why not keep going with the same products?
# -

tspan = ("2024-04-27", "2024-04-28")
location = (-56.95313,55.57192)
clouds = (0, 100)

results = earthaccess.search_data(
    short_name="PACE_OCI_L2_BGC_NRT",
    temporal=tspan,
    point=location,
    cloud_cover=clouds,
)

for item in results[0:10]:
    display(item)

# In order to download netcdf files, we need to create a directory

parent = pathlib.Path("granules_l2bin")
parent.mkdir(exist_ok=True)

# Now let's download the granules to the directory

paths = earthaccess.download(results, parent)
paths

# ### `l2bin` processing
# `l2bin` requires an infile containing the paths and names of the files to be merged. Let's create one:

ifile = "l2bin-list.txt"
with open(ifile, mode='w', newline='') as fp:
    for file in parent.glob("*.nc"):
        f = os.path.join(file_path, file)
        fp.write(str(f) + os.linesep)

# We can have a look at the possible options from `l2bin`:

# + scrolled=true language="bash"
# source $OCSSWROOT/OCSSW_bash.env
#
# l2bin
# -

# Now run `l2bin` using your chosen parameters:

ofile = str(parent / "PACE_OCI.20240427T161654.L3b.DAY.nc")

# + scrolled=true magic_args="-s {ifile} {ofile}" language="bash"
# source $OCSSWROOT/OCSSW_bash.env
#
# l2bin ifile=$1 ofile=$2 prodtype=regional resolution=1 flaguse=NONE rowgroup=2000

# +
# FIXME why not just one?
# -

dataset = xr.open_dataset(ofile, group="level-3_binned_data")
dataset

dataset["rhos_2258"][34].data

# ### Visualize your L3 dataset
# Once the L3 file is created. You can open it with `xarray` to visualize it. 

# + scrolled=true
dataset = xr.open_dataset(parent / "PACE_OCI.20240427T161654.L3m.DAY.all.1km.nc")
dataset
# -

# Now we can plot the merged dataset and add map elements like coastlines and gridlines. The `robust` parameter of the plot removes the data outliers. 

# +
fig = plt.figure()
ax = plt.axes(projection=ccrs.PlateCarree())
ax.coastlines(linewidth=0.5)
ax.gridlines(draw_labels={"left": "y", "bottom": "x"}, linewidth=0.3)

plot = dataset['chlor_a'].plot(x="lon", y="lat", cmap="viridis", robust=True)

plt.ylim(35, 60);
plt.xlim(-75, -50);
# -

# ## 5. Make a map with `l3mapgen` <a name="l3mapgen"></a>
# ***

# ### Run `l3mapgen`
# The `l3mapgen` function of OCSSW allows you to create maps with a wide array of options you can see below:

# + scrolled=true language="bash"
# source $OCSSWROOT/OCSSW_bash.env
#
# l3mapgen
# -

# Run `l3mapgen` to make a 1km map with a plate carree projection. 

# + scrolled=true language="bash"
# source $OCSSWROOT/OCSSW_bash.env
#
# l3mapgen ifile=/home/jovyan/ocssw_test/granules_l2bin/PACE_OCI.20240427T161654.L3b.DAY.nc \
# ofile=/home/jovyan/ocssw_test/granules_l2bin/PACE_OCI.20240427T161654.L3m.DAY.all.1km.nc \
# projection=platecarree \
# resolution=1km \
# interp=bin \
# use_quality=0 \
# apply_pal=0
# -

# ### Visualize your map
#
# The level 3 map dataset can now be opened with the SeaDAS GUI application or using `xarray` in a jupyter notebook to produce a map. 
#
# Here is an example using `xarray`:

dataset = xr.open_dataset(parent / "PACE_OCI.20240427T161654.L3m.DAY.all.1km.nc")

# Make a quick plot with the data:

plot = dataset["chlor_a"].plot(x="lon", y="lat")

# Add coastines, gridlines, and remove the outliers:

# +
fig = plt.figure()
ax = plt.axes(projection=ccrs.PlateCarree())
ax.coastlines(linewidth=0.5)
ax.gridlines(draw_labels={"left": "y", "bottom": "x"}, linewidth=0)

plot = dataset["chlor_a"].plot(x="lon", y="lat", cmap="viridis", robust=True)

plt.ylim(35, 60);
plt.xlim(-75, -50);
# -
# <div class="alert alert-info" role="alert">
# <p>You have completed the notebook on using OCCSW to process PACE data. More notebooks are comming soon!</p>
# </div>

