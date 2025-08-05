---
kernelspec:
  display_name: Python 3 (ipykernel)
  language: python
  name: python3
---

# Processing with OCSSW Command Line Interface (CLI)

**Authors:** Carina Poulin (NASA, SSAI), Ian Carroll (NASA, UMBC), Anna Windle (NASA, SSAI)

<div class="alert alert-success" role="alert">

The following notebooks are **prerequisites** for this tutorial.

- Learn with OCI: [Data Access][oci-data-access]
- Learn with OCI: [Installing and Running OCSSW Command-line Tools][ocssw_install]

</div>

<div class="alert alert-info" role="alert">

An [Earthdata Login][edl] account is required to access data from the NASA Earthdata system, including NASA ocean color data.

</div>

[edl]: https://urs.earthdata.nasa.gov/
[oci-data-access]: https://oceancolor.gsfc.nasa.gov/resources/docs/tutorials/notebooks/oci_data_access/
[ocssw_install]: https://oceancolor.gsfc.nasa.gov/resources/docs/tutorials/notebooks/oci_ocssw_install/

## Summary

[SeaDAS][seadas] is the official data analysis sofware of NASA's Ocean Biology Distributed Active Archive Center (OB.DAAC); used to process, display and analyse ocean color data. SeaDAS is a dektop application that includes the Ocean Color Science Software (OCSSW) libraries. There is also a command line interface (CLI) for the OCSSW libraries, which we can use to write processing scripts and notebooks without SeaDAS.

This tutorial will show you how to process PACE OCI data using the sequence of OCSSW programs `l2gen`, `l2bin`, and `l3mapgen`.

[seadas]: https://seadas.gsfc.nasa.gov/

## Learning Objectives

At the end of this notebok you will know:
* How to process Level-1B (L1B) data to Level-2 (L2) with `l2gen`
* How to merge two images with `l2bin`
* How to create a map with `l3mapgen`

## Contents

1. [Setup](#1.-Setup)
2. [Get L1B Data](#2.-Get-L1B-Data)
3. [Process L1B Data with `l2gen`](#3.-Process-L1B-Data-with-l2gen)
4. [Composite L2 Data with `l2bin`](#4.-Composite-L2-Data-with-l2bin)
5. [Make a Map from Binned Data with `l3mapgen`](#5.-Make-a-Map-from-Binned-Data-with-l3mapgen)

+++

## 1. Setup

Begin by importing all of the packages used in this notebook. If your kernel uses an environment defined following the guidance on the [tutorials] page, then the imports will be successful.

[tutorials]: https://oceancolor.gsfc.nasa.gov/resources/docs/tutorials/

```{code-cell} ipython3
import csv
import os
from pathlib import Path

import cartopy.crs as ccrs
import earthaccess
import matplotlib.pyplot as plt
import xarray as xr
```

+++ {"lines_to_next_cell": 2}

We are also going to define a function to help write OCSSW parameter files, which
is needed several times in this tutorial. To write the results in the format understood
by OCSSW, this function uses the `csv.writer` from the Python Standard Library. Instead of
writing comma-separated values, however, we specify a non-default delimiter to get
equals-separated values. Not something you usually see in a data file, but it's better than
writing our own utility from scratch!

```{code-cell} ipython3
def write_par(path, par):
    """Prepare a parameter file to be read by one of the OCSSW tools.

    Using a parameter file (a.k.a. "par file") is equivalent to specifying
    parameters on the command line.

    Parameters
    ----------
    path
        where to write the parameter file
    par
        the parameter names and values included in the file
    """
    with open(path, "w") as file:
        writer = csv.writer(file, delimiter="=")
        writer.writerows(par.items())
```

The Python docstring (fenced by triple quotation marks in the function definition) is not
essential, but it helps describe what the function does.
This docstring follows the NumPy [style guide], which is one of a few common conventions.

[style guide]: https://numpydoc.readthedocs.io/

```{code-cell} ipython3
help(write_par)
```

[back to top](#Contents)

+++

## 2. Get L1B Data


Set (and persist to your user profile on the host, if needed) your Earthdata Login credentials.

```{code-cell} ipython3
auth = earthaccess.login(persist=True)
```

To use OCSSW cloud processing, we also need to set our temporary S3 credentials.

```{code-cell} ipython3
credentials = earthaccess.get_s3_credentials(provider="OB_CLOUD")
```

We will use the `earthaccess` search method used in the OCI Data Access notebook. Note that Level-1B (L1B) files
do not include cloud coverage metadata, so we cannot use that filter. In this search, the spatial filter is
performed on a location given as a point represented by a tuple of latitude and longitude in decimal degrees.

```{code-cell} ipython3
tspan = ("2024-04-27", "2024-04-27")
location = (-56.5, 49.8)
```

The `search_data` method accepts a `point` argument for this type of location.

```{code-cell} ipython3
results = earthaccess.search_data(
    short_name="PACE_OCI_L1B_SCI",
    temporal=tspan,
    point=location,
)
results[0]
```

Store the link to the data in a variable for future use.

```{code-cell} ipython3
ifile = results[0].data_links(access="direct")[0]
ifile
```

The L1B files contain top-of-atmosphere reflectances, typically denoted as $\rho_t$.
On OCI, the reflectances are grouped into blue, red, and short-wave infrared (SWIR) wavelengths. Open
the dataset's "observation_data" group in the netCDF file using `xarray` to plot a "rhot_red"
wavelength.

```{code-cell} ipython3
f = earthaccess.open([ifile], provider="OB_CLOUD")
```

```{code-cell} ipython3
dataset = xr.open_dataset(f[0], group="observation_data")
plot = dataset["rhot_red"][dict(red_bands=100)].plot()
```

[back to top](#Contents)

+++

## 3. Process L1B Data with `l2gen`

At Level-1, we neither have geophysical variables nor are the data projected for easy map making. We will need to process the L1B file to L2 and then to Level-3-Mapped (L3M) to get both of those. Note that L2 data for many geophysical variables are available for download from the OB.DAAC, so you often don't need the first step. However, the L3M data distributed by the OB.DAAC are global composites, which may cover more L2 scenes than you want. You'll learn more about compositing below. This section shows how to use `l2gen` for processing the L1B data to L2 using customizable parameters.

<div class="alert alert-warning">

OCSSW programs are system commands, typically called in a Bash shell. We will employ [system shell access][ipython] available in the IPython kernel to launch system commands as a subprocess using the `!` prefix. In the specific case of OCSSW programs, a suite of required environment variables must be set by first executing `source $OCSSWROOT/OCSSW_bash.env` in the same subprocess.

</div>

Every time we use `!` to invoke an OCSSW program, we must also evaluate the `OCSSW_bash.env` environment file shipped with OCSSW. Each `!` initiated subprocess is distinct, and the environment configuration is discarded after the command is finished. Let's get prepared by reading the path to the OCSSW installation from the `OCSSWROOT` environment variable (assuming it's `/tmp/ocssw` as a fallback).

[ipython]: https://ipython.readthedocs.io/en/stable/interactive/reference.html#system-shell-access

```{code-cell} ipython3
ocsswroot = os.environ.setdefault("OCSSWROOT", "/tmp/ocssw")
env = Path(ocsswroot, "OCSSW_bash.env")
env.exists()
```

We then neet to set up the AWS cloud processing credentials in our environment.

```{code-cell} ipython3
os.environ.update(
    {
        "AWS_ACCESS_KEY_ID": credentials["accessKeyId"],
        "AWS_SECRET_ACCESS_KEY": credentials["secretAccessKey"],
        "AWS_SESSION_TOKEN": credentials["sessionToken"],
    }
)
```

Then we need a couple lines, which will appear in multiple cells below, to begin a Bash cell initiated with the `OCSSW_bash.env` file.

Using this pattern, run the `l2gen` command with the single argument `help` to view the extensive list of options available. You can find more information about `l2gen` and other OCSSW functions on the [seadas website](https://seadas.gsfc.nasa.gov/help-8.3.0/processors/ProcessL2gen.html)

```{code-cell} ipython3
:scrolled: true
:tags: [scroll-output]

!source {env}; l2gen help
```

To process a L1B file using `l2gen`, at a minimum, you need to set an infile name (`ifile`) and an outfile name (`ofile`). You can also indicate a data suite or L2 products; in this example, we will proceed with chlorophyll *a* estimates.

Parameters can be passed to OCSSW programs through a text file. They can also be passed as arguments, but writing to a text file leaves a clear processing record. Define the parameters in a dictionary, then send it to the `write_par` function
defined in the [Setup](#1.-Setup) section.

We can limit the geographical boundaries of the processing. Here we use the `location` variable to set Northwestern and Southeastern boundaries.

```{code-cell} ipython3
location = [(-62, 49), (-60, 47)]
par = {
    "ifile": ifile,
    "ofile": os.path.basename(ifile).replace("L1B", "L2"),
    "l2prod": "chlor_a",
    "proc_uncertainty": 0,
    "north": location[0][1],
    "south": location[1][1],
    "east": location[1][0],
    "west": location[0][0],
}
write_par("l2gen.par", par)
```

With the parameter file ready, it's time to call `l2gen` from a `%%bash` cell.

```{code-cell} ipython3
:scrolled: true
:tags: [scroll-output]

!source {env}; l2gen par=l2gen.par
```

If successful, the `l2gen` program created a netCDF file at the `ofile` path.
The contents should include the `rhos` product from the `SFREFL` suite of products and be cropped to a small bounding box.
Once this process is done, you are ready to visualize your "custom" L2 data.
Use the `robust=True` option to ignore outlier values.

```{code-cell} ipython3
dataset = xr.open_dataset(par["ofile"], group="geophysical_data")
plot = dataset["chlor_a"].plot(cmap="viridis", robust=True)
```

Feel free to explore `l2gen` options to produce the L2 dataset you need! The documentation
for `l2gen` is kind of interactive, because so much depends on the data product being processed.
For example, try `l2gen dump_options=true` with an `ifile` argument to get
a lot of information about the specifics of what the `l2gen` program generates for that `ifile`.

The next step for this tutorial is to merge multiple L2 granules together.

[back to top](#Contents)

+++

## 4. Composite L2 Data with `l2bin`

It can be useful to merge adjacent scenes to create a single, larger image. The OCSSW program that performs merging, also known as "compositing" of remote sensing images, is called `l2bin`. Take a look at the program's options.

```{code-cell} ipython3
:scrolled: true
:tags: [scroll-output]

!source {env}; l2bin help
```

Let's search for granules to bin.

```{code-cell} ipython3
location = [(-56.5, 49.8), (-53.3, 48.4)]
```

Searching on a location defined as a line, rather than a point, is a good way to get granules that are
adjacent to eachother. Pass a list of latitude and longitude tuples to the `line` argument of `search_data`.

```{code-cell} ipython3
results = earthaccess.search_data(
    short_name="PACE_OCI_L2_BGC",
    temporal=tspan,
    line=location,
)
for item in results:
    display(item)
```

Get the S3 links for the files.

```{code-cell} ipython3
paths = [i.data_links(access="direct")[0] for i in results]
paths
```

While we have the downloaded location stored in the list `paths`, write the list to a text file for future use.

```{code-cell} ipython3
paths = [f"{i}\n" for i in paths]
with open("l2bin_ifile.txt", "w") as file:
    file.writelines(paths)
```

Then we use that text file as an `ifile` parameter in the `l2bin` par file.

```{code-cell} ipython3
ofile = "granules/PACE_OCI.L3B.nc"
os.makedirs("granules", exist_ok=True)
par = {
    "ifile": "l2bin_ifile.txt",
    "ofile": ofile,
    "prodtype": "regional",
    "resolution": 9,
    "rowgroup": 2000,
}
write_par("l2bin.par", par)
```

Now run `l2bin` using your chosen parameters:

```{code-cell} ipython3
:scrolled: true
:tags: [scroll-output]

!source {env}; l2bin par=l2bin.par
```

[back to top](#Contents)

+++

## 5. Make a Map from Binned Data with `l3mapgen`

The `l3mapgen` function of OCSSW allows you to create maps with a wide array of options you can see below:

```{code-cell} ipython3
:scrolled: true
:tags: [scroll-output]

!source {env}; l3mapgen help
```

Run `l3mapgen` to make a 9km map with a Plate Carree projection.

```{code-cell} ipython3
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
```

```{code-cell} ipython3
:scrolled: true
:tags: [scroll-output]

!source {env}; l3mapgen par=l3mapgen.par
```

Open the output with XArray, note that there is no group anymore.

```{code-cell} ipython3
dataset = xr.open_dataset(par["ofile"])
dataset
```

Now that we have projected data, we can make a map with coastines and gridlines.

```{code-cell} ipython3
fig, ax = plt.subplots(figsize=(10, 3), subplot_kw={"projection": ccrs.PlateCarree()})
plot = dataset["chlor_a"].plot(x="lon", y="lat", cmap="viridis", robust=True, ax=ax)
ax.gridlines(draw_labels={"left": "y", "bottom": "x"}, linewidth=0.3)
ax.coastlines(linewidth=0.5)
plt.show()
```

[back to top](#Contents)

<div class="alert alert-info" role="alert">

You have completed the notebook on using OCCSW to process PACE data! You can now explore more notebooks to learn more about OCSSW usage. 

</div>
