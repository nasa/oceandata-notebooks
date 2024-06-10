# # Processing with OCSSW Tools: l2gen, l2bin, and l3mapgen
#
# **Authors:** Carina Poulin (NASA, SSAI), Ian Carroll (NASA, UMBC), Anna Windle (NASA, SSAI)
#
# > **PREREQUISITES**
# >
# > This notebook has the following prerequisites:
# > - An **<a href="https://urs.earthdata.nasa.gov/" target="_blank">Earthdata Login</a>**
# >   account is required to access data from the NASA Earthdata system, including NASA ocean color data.
# > - Learn with OCI: <a href="https://oceancolor.gsfc.nasa.gov/resources/docs/tutorials/notebooks/oci_ocssw_processing_bash/" target="_blank">Installing and Running OCSSW Command-line Tools</a>
#
# ## Summary
#
# [SeaDAS][seadas] is the official data analysis sofware of NASA's Ocean Biology Distributed Active Archive Center (OB.DAAC); used to process, display and analyse ocean color data. SeaDAS is a dektop application that includes the Ocean Color Science Software (OCSSW) libraries. There are also command line programs for the OCSSW libraries, which we can use to write processing scripts or notebooks.
#
# This tutorial will show you how to process PACE OCI data using the sequence of OCSSW programs `l2gen`, `l2bin`, and `l3mapgen`.
#
# [seadas]: https://seadas.gsfc.nasa.gov/
#
# ## Learning Objectives
#
# <a name="toc"></a>
# At the end of this notebok you will know:
# * How to process Level-1B data to Level-2 with `l2gen`
# * How to merge two images with `l2bin`
# * How to create a map with `l3mapgen`
#
# ## Contents
#
# 1. [Setup](#setup)
# 1. [Get L1B Data](#data)
# 1. [Process L1B Data with `l2gen`](#l2gen)
# 1. [Composite L2 Data with `l2bin`](#l2bin)
# 1. [Make a Map from Binned Data with `l3mapgen`](#l3mapgen)
#      
# <a name="setup"></a> 
# ## 1. Setup
#
# We begin by importing all of the packages used in this notebook.

# +
import csv
import os
import pathlib

import cartopy.crs as ccrs
import earthaccess
import xarray as xr
import matplotlib.pyplot as plt
# -

# We are also going to define a function to help write OCSSW parameter files, which
# is needed several times in this tutorial. To write the results in the format understood
# by OCSSW, this function uses the `csv.writer` from the Python Standard Library. Instead of
# writing comma-separated values, however, we specify a non-default delimiter to get
# equals-separated values. Not something you usually see in a data file, but it's better than
# writing our own utility from scratch!

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


# The Python docstring (fenced by triple quotation marks in the function definition) is not
# essential, but it helps describe what the function does.

help(write_par)

# ## 2. Get OCI Data <a name="data"></a>
#
#
# Set (and persist to your user profile on the host, if needed) your Earthdata Login credentials.

auth = earthaccess.login(persist=True)

# We will use the `earthaccess` search method used in the OCI Data Access notebook. Note that Level-1B (L1B) files
# do not include cloud coverage metadata, so we cannot use that filter. In this search, the spatial filter is
# performed on a location given as a point represented by a tuple of latitude and longitude in decimal degrees.

tspan = ("2024-04-27", "2024-04-28")
location = (-56.5, 49.8)

# The `search_data` method accepts a `point` argument for this type of location.

results = earthaccess.search_data(
    short_name="PACE_OCI_L1B_SCI",
    temporal=tspan,
    point=location,
)

results[0]

# Create a directory where you will store downloaded granules (nb. this step is unnecessary with earthaccess >= 0.9.1).

parent = pathlib.Path("granules")
parent.mkdir(exist_ok=True)

# Download the granules found in the search.

paths = earthaccess.download(results, parent)

# While we have the downloaded location stored in the list `paths`, store one in a variable we won't overwrite for future use.

l2gen_ifile = paths[0]

# The Level-1B files contain top-of-atmosphere reflectances, typically denoted as $\rho_t$.
# On OCI, the reflectances are grouped into blue, red, and short-wave infrared (SWIR) wavelengths. Open
# the dataset's "observatin_data" group in the netCDF file using `xarray` to plot a "rhot_red"
# wavelength.

dataset = xr.open_dataset(paths[0], group="observation_data")
plot = dataset["rhot_red"].sel({"red_bands": 100}).plot()

# This tutorial will demonstrate processing this Level-1B granule into a Level-2 granule. Because that can
# take several minutes, we'll also download a couple of Level-2 granules to save time for the next step of compositing multiple Level-2 granules into a single granule.

location = [(-56.5, 49.8), (-55.0, 49.8)]

# Searching on a location defined as a line, rather than a point, is a good way to get granules that are
# adjacent to eachother. Pass a list of latitude and longitude tuples to the `line` argument of `search_data`.

results = earthaccess.search_data(
    short_name="PACE_OCI_L2_BGC_NRT",
    temporal=tspan,
    line=location,
)

for item in results:
    display(item)

paths = earthaccess.download(results, parent)
paths

# While we have the downloaded location stored in the list `paths`, write it to a text file for future use.

paths = [str(i) for i in paths]
with open("l2bin_ifile.txt", "w") as file:
    file.write("\n".join(paths))

# ## 3. Process L1B Data with `l2gen` <a name="l2gen"></a>
#

# At Level-1, we neither have geophysical variables nor are the data projected for easy map making. We will need to process the L1B file to Level-2 and then to Level-3 to get both of those. Note that Level-2 data for many geophysical variables are available for download from the OB.DAAC, so you often don't need the first step. However, the Level-3 data distributed by the OB.DAAC are global composites, which may cover more Level-2 scenes than you want. You'll learn more about compositing below. This section shows how to use `l2gen` for processing the L1B data to L2 using customizable parameters. 

# <div class="alert alert-warning">
# OCSSW programs are run from the command line in Bash, but we can have a Bash terminal-in-a-cell using the IPython <a href="https://ipython.readthedocs.io/en/stable/interactive/magics.html#built-in-magic-commands" target=_blank>magic</a> command <code>%%bash</code>. In the specific case of OCSSW programs, the Bash environment created for that cell must be set up by loading <code>$OCSSWROOT/OCSSW_bash.env</code>.
# </div>
#
# Every `%%bash` cell that calls an OCSSW program needs to `source` the environment
# definition file shipped with OCSSW, because its effects are not retained from one cell to the next.
# We can, however, define the `OCSSWROOT` environment variable in a way that effects every `%%bash` cell.

os.environ.setdefault("OCSSWROOT", "/tmp/ocssw")

# Then we need a couple lines, which will appear in multiple cells below, to begin a Bash cell initiated with the `OCSSW_bash.env` file.
#
# Using this pattern, run the `l2gen` command with the single argument `help` to view the extensive list of options available. You can find more information about `l2gen` and other OCSSW functions on the [seadas website](https://seadas.gsfc.nasa.gov/help-8.3.0/processors/ProcessL2gen.html)

# + scrolled=true language="bash"
# source $OCSSWROOT/OCSSW_bash.env
#
# l2gen help
# -

# To process a L1B file using `l2gen`, at a minimum, you need to set an infile name (`ifile`) and an outfile name (`ofile`). You can also indicate a data suite; in this example, we will proceed with the biogeochemical (BGC) suite that includes chlorophyll *a* estimates.
#
# Parameters can be passed to OCSSW programs through a text file. They can also be passed as arguments, but writing to a text file leaves a clear processing record. Define the parameters in a dictionary, then send it to the `write_par` function
# defined in the [Setup](#setup) section.

par = {
    "ifile": l2gen_ifile,
    "ofile": str(l2gen_ifile).replace("L1B", "L2"),
    "suite": "BGC",
    "l2prod": "chlor_a",
    "atmocor": 1,
}
write_par("l2gen.par", par)

# With the parameter file ready, it's time to call `l2gen` from a `%%bash` cell. 

# + scrolled=true language="bash"
# source $OCSSWROOT/OCSSW_bash.env
#
# l2gen par=l2gen.par
# -

# If successful, the `l2gen` program created a netCDF file at the `ofile` path. The contents should include the `chlor_a` product from the `BGC` suite of products. Once this process is done, you are ready to visualize your "custom" L2 data. Use the `robust=True` option to ignore outlier chl a values.

dataset = xr.open_dataset(par["ofile"], group="geophysical_data")
plot = dataset["chlor_a"].plot(cmap="viridis", robust=True)

# Feel free to explore `l2gen` options to produce the Level-2 dataset you need! The documentation
# for `l2gen` is kind of interactive, because so much depends on the data product being processed.
# For example, try `l2gen ifile=granules/PACE_OCI.20240427T161654.L1B.nc dump_options=true` to get
# a lot of information about the specifics of what the `l2gen` program generates.
#
# The next step for this tutorial is to merge multiple Level-2 granules together.

# [Back to top](#toc)
# <a name="l2bin"></a>
# ## 4. Composite L2 Data with `l2bin`
#
# It can be useful to merge adjacent scenes to create a single, larger image. The OCSSW program that performs merging, also known as "compositing" of remote sensing images, is called `l2bin`. Take a look at the program's options.

# + scrolled=true language="bash"
# source $OCSSWROOT/OCSSW_bash.env
#
# l2bin help
# -

# Write a parameter file with the previously saved list of Level-2 files standing in
# for the usual "ifile" value. We can leave the datetime out of the "ofile" name rather than extracing a
# time period from the granules chosen for binning.

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

# Now run `l2bin` using your chosen parameters:

# + scrolled=true language="bash"
# source $OCSSWROOT/OCSSW_bash.env
#
# l2bin par=l2bin.par
# -

# [Back to top](#toc)
# <a name="l3mapgen"></a>
# ## 5. Make a Map from Binned Data with `l3mapgen`

# The `l3mapgen` function of OCSSW allows you to create maps with a wide array of options you can see below:

# + scrolled=true language="bash"
# source $OCSSWROOT/OCSSW_bash.env
#
# l3mapgen help
# -

# Run `l3mapgen` to make a 9km map with a Plate Carree projection.

ifile = "granules/PACE_OCI.L3B.nc"
ofile = ifile.replace(".L3B.", ".L3M.")
par = {
    "ifile": ifile,
    "ofile": ofile,
    "projection": "platecarree",
    "resolution": "9km",
    "interp": "bin",
    "use_quality": 0,
    "apply_pal": 0,
}
write_par("l3mapgen.par", par)

# + scrolled=true language="bash"
# source $OCSSWROOT/OCSSW_bash.env
#
# l3mapgen par=l3mapgen.par
# -

# Open the output with XArray, note that there is no group anymore.

dataset = xr.open_dataset(par["ofile"])
dataset

# Now that we have projected data, we can make a map with coastines and gridlines.

fig = plt.figure()
ax = plt.axes(projection=ccrs.PlateCarree())
ax.coastlines(linewidth=0.5)
ax.gridlines(draw_labels={"left": "y", "bottom": "x"}, linewidth=0.3)
plot = dataset["chlor_a"].plot(x="lon", y="lat", cmap="viridis", robust=True, ax=ax)

# <div class="alert alert-info" role="alert">
# <p>You have completed the notebook on using OCCSW to process PACE data. More notebooks are comming soon!</p>
# </div>
