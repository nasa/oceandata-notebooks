---
jupytext:
  text_representation:
    extension: .md
    format_name: myst
    format_version: 0.13
    jupytext_version: 1.17.2
kernelspec:
  display_name: Python 3 (ipykernel)
  language: python
  name: python3
---

# Run OCSSW Level-2 Generator (l2gen) for PACE/OCI

**Author(s):** Anna Windle (NASA, SSAI), Jeremy Werdell (NASA)

Last updated: August 1, 2025

<div class="alert alert-success" role="alert">

The following notebooks are **prerequisites** for this tutorial.

- Learn with OCI: [Data Access][oci-data-access]
- Learn with OCI: [Installing and Running OCSSW Command-line Tools][ocssw_install]

</div>

<div class="alert alert-info" role="alert">

An [Earthdata Login][edl] account is required to access data from the NASA Earthdata system, including NASA ocean color data.

</div>

<div class="alert alert-info" role="alert">

This notebook was desgined to use cloud-enabled OCSSW programs, which are available in OCSSW tag V2025.2 or higher. Cloud-enabled OCSSW programs can only be run on an AWS EC2 instance, such as CryoCloud.

</div>

[edl]: https://urs.earthdata.nasa.gov/
[oci-data-access]: https://oceancolor.gsfc.nasa.gov/resources/docs/tutorials/notebooks/oci_data_access/
[ocssw_install]: https://oceancolor.gsfc.nasa.gov/resources/docs/tutorials/notebooks/oci_ocssw_install/

## Summary

The [OceanColor Science SoftWare][ocssw] (OCSSW) repository is the operational data processing software package of NASA's Ocean Biology Distributed Active Archive Center (OB.DAAC). OCSSW is publically available through the OB.DAAC's [Sea, earth, and atmosphere Data Analysis System][seadas] (SeaDAS) application, which provides a complete suite of tools to process, display and analyze ocean color data. SeaDAS provides a graphical user interface (GUI) for OCSSW, but command line interfaces (CLI) also exist, which we can use to write processing scripts and notebooks without the desktop application.

The Level-2 Generator (`l2gen`) program included in OCSSW is used to generate aquatic Level-2 (L2) data products from calibrated top-of-atmosphere (TOA) radiances. Specifically, `l2gen` atmospherically corrects spectral TOA Level-1B (L1B) radiances to obtain geophysical products, such as spectral remote-sensing reflectances (Rrs) and near-surface concentrations of the photosynthetic pigment chlorophyll-a. More information on `l2gen` methods can be found in the [Rrs Algorithm Theoretrical Basis Document].

This tutorial will demonstrate how to process PACE OCI L1B data through the `l2gen` default settings to retrieve the standard L2 ocean color (OC) data suite. Done right, this data should be *exactly* what you would download from the NASA Earthdata Cloud. This tutorial will also demonstrate how to modify the operation of `l2gen` configurations based on your research needs.

[seadas]: https://seadas.gsfc.nasa.gov/
[ocssw]: https://oceandata.sci.gsfc.nasa.gov/ocssw
[Rrs Algorithm Theoretrical Basis Document]: https://www.earthdata.nasa.gov/apt/documents/rrs/v1.1

## Learning Objectives

At the end of this notebook you will know:

- How to navigate and open files within the OCSSW directory
- How to process L1B data to L2 using `l2gen` with geographical boundaries
- How to extract geographic regions from a L2 file and create a new file
- How to make modifications to `l2gen` based on your research needs

+++

## 1. Setup

Begin by importing all of the packages used in this notebook. If your kernel uses an environment defined following the guidance on the [tutorials] page, then the imports will be successful.

[tutorials]: https://oceancolor.gsfc.nasa.gov/resources/docs/tutorials/

```{code-cell} ipython3
import csv
import os
from pathlib import Path

import cartopy.crs as ccrs
import cartopy.feature as cfeature
import earthaccess
import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
import xarray as xr
from matplotlib.colors import LogNorm
```

Next, we'll set up the OCSSW programs.

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

Our first OCSSW program is `install_ocssw`, which we use to print which version (tag) of OCSSW is installed. As just explained, we have to evaluate (or `source`) the environment configuration file first. To pass its location, we use `{}` variable expansion that is available with the `!` prefix.

```{code-cell} ipython3
!source {env}; install_ocssw --installed_tag
```

The `installedTag` is our OCSSW version. Tags beginning with "V" are operational tags, while "T" tags are equivalent to a "beta" release and meant for testing by advanced users.

+++

### Setting up AWS S3 credentials

Accessing data from NASA's Earthdata Cloud, regardless of the tool, requires authentication.
The `earthaccess` package works behind-the-scenes using the Earthdata Login credentials you provide to generate temporary AWS credentials for direct access to the Earthdata Cloud.

```{code-cell} ipython3
earthaccess.login(persist=True)
credentials = earthaccess.get_s3_credentials(provider="OB_CLOUD")
```

The OCSSW software accepts AWS credentials in all the usual methods, including via environment variables that we set in the next cell.

```{code-cell} ipython3
os.environ.update(
    {
        "AWS_ACCESS_KEY_ID": credentials["accessKeyId"],
        "AWS_SECRET_ACCESS_KEY": credentials["secretAccessKey"],
        "AWS_SESSION_TOKEN": credentials["sessionToken"],
    }
)
```

<div class="alert alert-warning">

Earthdata Cloud sets a one-hour lifespan on your temporary AWS credentials. If you get an `access denied` error, re-run the cell above to generate new AWS credentials.

<div>

+++

### Navigating OCSSW

+++

Within the OCSSW directory, there are sub-directories that contain files that control OCSSW processing and set default parameterizations of the various codes. Let's look at the files in the `share/common` sub-directory, which includes the files available to all satellite instruments considered in the OCSSW ecosystem:

```{code-cell} ipython3
:scrolled: true

!ls $OCSSWROOT/share/common
```

<div class="alert alert-info">

You can click within the area to the left side of an output cell to expand or collapse it.

</div>

Clearly, there are an intimidatingly large number of files required to process satellite ocean color data!  The most valuable to the scientific end user are those ending in ".par". These "par files" are plain text files that configure, or parameterize, OCSSW programs. They typically define the inputs, outputs, and the different options one can modify for each program.

<div class="alert alert-warning">

Fun fact: `l2gen` used to be named "Multi Sensor Level 1 to 2", or MSL12. That is why many par files start with 'msl12'. The OB.DAAC renamed most programs with names like 'l2gen', or 'l3mapgen' to more clearly identify their purpose. But, the par files for use with l2gen still have names that begin with 'msl12'. Just remember msl12 = l2gen.

</div>

Now, let's look at the PACE OCI-specific files within the `share/oci` directory:

```{code-cell} ipython3
:scrolled: true

!ls $OCSSWROOT/share/oci
```

Let's print "msl12_defaults.par", where the `l2gen` default parameters for OCI are defined:

```{code-cell} ipython3
:scrolled: true

!cat $OCSSWROOT/share/oci/msl12_defaults.par
```

This par file lists the default configuration for standard `l2gen` processing. If nothing is modified from this par file, `l2gen` will process a L1B file to L2 containing the OC suite of data products, and it will be *exactly* the same as the L2 data file that OBPG processes and ingests into NASA Earthdata.

<div class="alert alert-warning">

<b>Here are some examples of other aquatic data suites that may be of interest:
* AOP: Apparent Optical Properties
* BGC: Biogeochemical Propeties
* IOP: Inherent Optical Properties
* PAR: Photosynthetic available radiation

</b>

</div>

<div class="alert alert-info">

You can also see OCSSW parameter options by running 'l2gen --help'.

</div>

```{code-cell} ipython3
:scrolled: true

!source {env}; l2gen --help
```

### Writing OCSSW parameter files

+++

User-generated parameter files provide a convenient way to control `l2gen` processing.

Without a par file, providing `l2gen` the names of the input L1B and output L2 files from the Terminal looks like this:

```bash
l2gen ifile=data/PACE_OCI.20250507T170659.L1B.V3.nc ofile=data/PACE_OCI.20250507T170659.L2.V3.nc
```

Alternatively, a user-defined par file, say "l2gen.par", can be created with the following two lines of content:

    ifile=data/PACE_OCI.20250507T170659.L1B.V3.nc
    ofile=data/PACE_OCI.20250507T170659.L2.V3.nc

Now `l2gen` can now be called using the single argument `par` while generating the same result:

```bash
l2gen par=l2gen.par
```

You can imagine that the par file option becomes far more convenient when many changes from default are desired.

So let's define a function to help write OCSSW parameter files, which is needed several times in this tutorial. To write the results in the format understood by OCSSW, this function uses the `csv.writer` from the Python Standard Library. Instead of writing comma-separated values, however, we specify a non-default delimiter to get equals-separated values. Not something you usually see in a data file, but it's better than writing our own utility from scratch!

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

## 2. Search and access L1B data

Let's use the `earthaccess` Python package to access a L1B and a corresponding L2 file.

```{code-cell} ipython3
tspan = ("2025-05-07", "2025-05-07")
bbox = (-76.75, 36.97, -74.74, 39.01)
results = earthaccess.search_data(
    short_name="PACE_OCI_L1B_SCI",
    temporal=tspan,
    bounding_box=bbox,
)
results[0]
```

```{code-cell} ipython3
l1b_paths = earthaccess.open(results)
```

Now let's do the same for the corresponding L2 file, which we'll use later.

```{code-cell} ipython3
results = earthaccess.search_data(
    short_name="PACE_OCI_L2_AOP_NRT",
    temporal=tspan,
    bounding_box=bbox,
)
results[0]
```

Next, let's define variables with the path of the input file to process using `l2gen`and a corresponding L2 output file that we'll create.

```{code-cell} ipython3
l2_paths = earthaccess.open(results)
```

And let's plot a `rhot_red` wavelength to see what the data looks like:

```{code-cell} ipython3
dataset = xr.open_datatree(l1b_paths[0])
dataset = xr.merge(dataset.to_dict().values())
dataset = dataset.set_coords(("longitude", "latitude"))
plot = dataset["rhot_red"].sel({"red_bands": 100}).plot()
```

## 3. Run `l2gen` with default configurations

+++

Let's now run `l2gen` using its default configuration.

Before we do this, however, there is one additional step required to <i>exactly</i> replicate an L2 file from the OB.DAAC. The algorithms within `l2gen` require ancillary data such as meterological information, ozone concentrations, and sea surface temperatures. To use the corresponding ancillary data for the given date and region, we need to run the `getanc` OCSSW function. If `getanc` is not used, `l2gen` uses climatological data found in `share/common`.

We can run `getanc -h` to see options for the program:

```{code-cell} ipython3
:scrolled: true

!source {env}; getanc -h
```

Let's run it on our L1B file, using the `--use_filename` parameter to parse only the filename for datetime information.
We can parse the filename from `l1b_paths` to use with `{}` variable expansion after the `!` prefix like have done with `{env}` above.

```{code-cell} ipython3
l1b_path = l1b_paths[0].full_name
l1b_name = Path(l1b_path).name
l1b_name
```

```{code-cell} ipython3
!source {env}; getanc --use_filename {l1b_name} --ofile l2gen.anc --noprint
```

You'll notice that a file named "l2gen.anc" now appears in your working directory. Reading this file, you can see that ancillary files are saved in the `var/anc/` directory.  Note that this file also provides text in the correct format for use in a par file.

```{code-cell} ipython3
!cat l2gen.anc
```

Now, we'll make a par file that has an ifile, ofile, and latitude and longitude boundaries. Trust us ... subsetting the L1B file to a smaller region makes processing time faster for this demo!

We will output the Rrs variable by listing l2prod to "Rrs". And we wil also set proc_uncertainity to 0, which means we are not calculating uncertainites for Rrs. This makes `l2gen` process faster.

Let's first make a folder called 'data' to store the outputs:

```{code-cell} ipython3
data = Path("data")
data.mkdir(exist_ok=True)
```

Use the `write_par` function to create the following "l2gen.par" file in your current working directory.

```{code-cell} ipython3
par = {
    "ifile": l1b_path,
    "ofile": data / l1b_name.replace("L1B", "L2"),
    "north": 39,
    "south": 35,
    "west": -76,
    "east": -74.5,
    "l2prod": "Rrs",
    "proc_uncertainty": 0,
}
write_par("l2gen.par", par)
```

Now, let's run l2gen using this new par file AND the ancillary information in the second par file generated by `getanc`. This can take several minutes.

```{code-cell} ipython3
:scrolled: true

!source {env}; l2gen par=l2gen.par par=l2gen.anc
```

You'll know `l2gen` processing is finished successfully when you see "Processing Completed" at the end of the cell output.

Let's open up this new L2 data using XArray's open_datatree function:

```{code-cell} ipython3
dat = xr.open_datatree(par["ofile"])
dat = xr.merge(dat.to_dict().values())
dat = dat.set_coords(("longitude", "latitude"))
dat
```

Let's do a quick plot of Rrs at 550 nm:

```{code-cell} ipython3
plot = dat["Rrs"].sel({"wavelength_3d": 550}).plot(vmin=0, vmax=0.008)
```

## 4. Compare the newly generated file with a standard OB.DAAC file

+++

Remember the OB.DAAC L2 file we previously downloaded?  Let's see how it compares with the L2 file we generated ourselves.

Note, however, that the L2 file we downloaded includes the full granule, whereas our homegrown L2 file only includes the geographic bounding box of 35 to 39 N and -76 to -74.5 W. So, let's pause briefly to learn how to extract a geographic region from a L2 file. OCSSW provides the tools to do so and the process includes two steps.

First, we'll use the program `lonlat2pixline` to identify the scan line and pixel boundaries that correspond to our latitude and longitude coordinates within the full L2 granule.  Recall that you can see all the options for OCSSW programs by calling them without any arguments.

We need the full path to the input file (this will become the `$1` argument).

```{code-cell} ipython3
l2_path = l2_paths[0].full_name
l2_name = Path(l2_path).name
l2_sub_path = data / l2_name.replace("L2", "L2_sub")
l2_sub_path
```

And we need to specify the bounding box in the standard order: west, south, east, north

```{code-cell} ipython3
pixline = !source {env}; lonlat2pixline {l2_path} -76.0 35.0 -74.5 39.0
pixline
```

```{code-cell} ipython3
_, spix, epix, sline, eline = pixline[0].split()
```

This output gets fed into `l2extract` to create a new, smaller file that only includes our defined geographic boundaries. The arguments are input file, start pixel, end pixel, start line, end line, sampling substep for pixels and lines (where 1 = every pixel), and output file.

```{code-cell} ipython3
:scrolled: true

!source {env}; l2extract
```

```{code-cell} ipython3
!source {env}; l2extract {l2_path} {spix} {epix} {sline} {eline} 1 1 {l2_sub_path}
```

This should have created a new file including "L2_sub" in the data subdirectory.

Let's open it and see how it compares with the L2 file we generated.

```{code-cell} ipython3
dat_sub = xr.open_datatree(l2_sub_path)
dat_sub = xr.merge(dat_sub.to_dict().values())
dat_sub = dat_sub.set_coords(("longitude", "latitude"))
dat_sub
```

```{code-cell} ipython3
plot = dat_sub["Rrs"].sel({"wavelength_3d": 550}).plot(vmin=0, vmax=0.008)
```

The two maps of Rrs(550) look extremely similar.  But, let's compare the data in a scatter plot to be sure.

```{code-cell} ipython3
fig, ax = plt.subplots()

x = dat["Rrs"].sel({"wavelength_3d": 550})
y = dat_sub["Rrs"].sel({"wavelength_3d": 550})

ax.scatter(x, y, s=20)
ax.set_xlabel("OB.DAAC Rrs(550)")
ax.set_ylabel("User produced Rrs(550)")
ax.plot([0, 1], [0, 1], transform=ax.transAxes, color="black")
ax.set_ylim(bottom=0)
ax.set_xlim(left=0)

plt.show()
```

Other than a negligible number of oddball points, the data are identical. This shows that an end-user can exactly reproduce the data distributed by the OB.DAAC!

+++

## 5. Run l2gen with modifications to configurations

+++

### Selecting biogeochemical data products

+++

Let's say you want to run `l2gen` to retrieve biogeochemical data products, such as chlorophyll a concentrations. There are two ways to do so. First, you can assign a specific product suite.  For chlorophyll, this is done by adding "suite=BGC" to your .par file.  Second, you can explicitly define your output products in a list using the "l2prod" keyword. Consider this example:

<pre>l2prod=Rrs,chlor_a,poc,l2flags</pre>

"Rrs" includes all Rrs wavelengths, "chlor_a" is chlorophyll-a, "poc" is particulate organic carbon, and "[l2flags][l2flags]" is the bitwise operator that identifies processing flags assigned to each pixel (you <b>always</b> want to include [l2flags][l2flags] as an output product!).

Tip: You can run `get_product_info l sensor=oci` to see the many many products l2gen can produce.


Let's write a new .par file named "l2gen_mod.par" to define the L2 products listed above and rerun `l2gen`.

[l2flags]: https://oceancolor.gsfc.nasa.gov/resources/atbd/ocl2flags/

```{code-cell} ipython3
par = {
    "ifile": l1b_path,
    "ofile": data / l1b_name.replace("L1B", "L2_mod"),
    "l2prod": "Rrs,chlor_a,poc,l2_flags",
    "north": 39,
    "south": 35,
    "west": -76,
    "east": -74.5,
}
write_par("l2gen_mod.par", par)
```

```{code-cell} ipython3
:scrolled: true

!source {env}; l2gen par=l2gen_mod.par par=l2gen.anc
```

A new L2 file should have appeared in your data folder.  Let's open it using XArray again and plot the chlorophyll-a product:

```{code-cell} ipython3
dat_mod = xr.open_datatree(par["ofile"])
dat_mod = xr.merge(dat_mod.to_dict().values())
dat_mod = dat_mod.set_coords(("longitude", "latitude"))
plot = dat_mod["chlor_a"].plot(norm=LogNorm(vmin=0.01, vmax=2))
```

For fun, let's plot chlor_a again, but with some additional plotting functions.

```{code-cell} ipython3
fig, ax = plt.subplots(figsize=(8, 6), subplot_kw={"projection": ccrs.PlateCarree()})

dat_mod["chlor_a"].plot(
    ax=ax,
    x="longitude",
    y="latitude",
    transform=ccrs.PlateCarree(),
    cmap="ocean_r",
    norm=LogNorm(vmin=0.01, vmax=1.5),
    cbar_kwargs={"label": "Log Chlorophyll-a (mg m⁻³)"},
)

ax.coastlines(resolution="10m")
ax.add_feature(cfeature.BORDERS, linewidth=0.5)
ax.gridlines(draw_labels=True)

plt.show()
```

### Disabling BRDF correction

+++

As a final example of the far-reaching utility that `l2gen` provides an end user, let's exercise one more example where we disable the standard bidirectional reflectance distribution function (BRDF) correction and see how it changes the retrieved Rrs values. The default BRDF is 'brdf_opt=7', which is Morel f/Q + Fresnel solar + Fresnel sensor.

While a rather simple case-study, we hope it will introduce the practioner to an improved understanding of `l2gen` and the sensitivity of derived reflectances (and, therefore, biogeochemical variables) to choices made within the standard processing scheme.

```{code-cell} ipython3
par = {
    "ifile": l1b_path,
    "ofile": data / l1b_name.replace("L1B", "L2_brdf"),
    "l2prod": "Rrs,chlor_a,poc,l2_flags",
    "brdf_opt": 0,
    "north": 39,
    "south": 35,
    "west": -76,
    "east": -74.5,
}
write_par("l2gen_brdf.par", par)
```

```{code-cell} ipython3
:scrolled: true

!source {env}; l2gen par=l2gen_brdf.par par=l2gen.anc
```

A new L2 file should have appeared in your data folder.  Let's open it using XArray again and plot Rrs(550):

```{code-cell} ipython3
dat_brdf = xr.open_datatree(par["ofile"])
dat_brdf = xr.merge(dat_brdf.to_dict().values())
dat_brdf = dat_brdf.set_coords(("longitude", "latitude"))
dat_brdf
```

```{code-cell} ipython3
dat_brdf["Rrs"].sel({"wavelength_3d": 550}).plot(vmin=0, vmax=0.008)
```

This figure looks similar to what we produced in Section 3, but let's make a scatter plot to be sure ...

```{code-cell} ipython3
fig, ax = plt.subplots()

x = dat_mod["Rrs"].sel({"wavelength_3d": 550})
y = dat_brdf["Rrs"].sel({"wavelength_3d": 550})


ax.scatter(x, y, s=20)
ax.set_xlabel("default Rrs(550)")
ax.set_ylabel("disabled BRDF Rrs(550)")
ax.plot([0, 1], [0, 1], transform=ax.transAxes, color="black")

plt.tight_layout()
plt.show()
```

You can see that disabling the BRDF does in fact change Rrs values.

+++

<div class="alert alert-info" role="alert">

You have completed the notebook on "Running the Level-2 Generator (l2gen) OCSSW program on OCI data". We suggest looking at the notebook on "Running l2gen's Generalized Inherent Optical Property (GIOP) model on OCI data" tutorial to learn more about deriving IOP products from PACE OCI data.

</div>
