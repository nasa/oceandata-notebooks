---
kernelspec:
  display_name: Python 3 (ipykernel)
  language: python
  name: python3
---

# Run the Generalized Inherent Optical Property (GIOP) inversion model in the Level-2 Generator`l2gen` OCSSW program on OCI data

**Authors:** Anna Windle (NASA, SSAI), Jeremy Werdell (NASA) <br>
Last updated: July 31, 2025


<div class="alert alert-success" role="alert">

The following notebooks are **prerequisites** for this tutorial.

- Learn with OCI: [Data Access][oci-data-access]
- Learn with OCI: [Installing and Running OCSSW Command-line Tools][ocssw_install]
- Learn with OCI: [Run Level-2 Generator (l2gen) OCSSW program on OCI data][ocssw_l2gen]

</div>

<div class="alert alert-info" role="alert">

An [Earthdata Login][edl] account is required to access data from the NASA Earthdata system, including NASA ocean color data.

</div>

<di
    class="alert alert-info" role="alert">

This notebook was desgined to use cloud-enabled OCSSW programs, which are available in OCSSW tag V2025.2 or higher. Cloud-enabled OCSSW programs can only be run on an AWS EC2 instance, such as CryoCloud.

</div>

[edl]: https://urs.earthdata.nasa.gov/
[oci-data-access]: https://oceancolor.gsfc.nasa.gov/resources/docs/tutorials/notebooks/oci_data_access/
[ocssw_install]: https://oceancolor.gsfc.nasa.gov/resources/docs/tutorials/notebooks/oci_ocssw_install/
[ocssw_l2gen]: tbd

## Summary

The [OceanColor Science SoftWare][ocssw] (OCSSW) repository is the operational data processing software package of NASA's Ocean Biology Distributed Active Archive Center (OB.DAAC). OCSSW is publically available through the OB.DAAC's [Sea, earth, and atmosphere Data Analysis System][seadas] (SeaDAS), which provides a complete suite of tools to process, display and analyze ocean color data. SeaDAS is a desktop application that provides GUI access to OCSSW, but command line interfaces (CLI) also exist, which we can use to write processing scripts and notebooks without SeaDAS.

In a previous tutorial, we demonstrated how to run the Level-2 Generator (`l2gen`) program to generate aquatic Level-2 (L2) data products from calibrated top-of-atmosphere (TOA) radiances. Within `l2gen`, you can select options to produce inherent optical properties (IOPs) through an ocean color inversion model. IOP data products are derived using the default configuration of the GIOP algorithm framework model [(Werdell et al., 2013)]. The IOP products are distributed as part of the NASA standard L2 and the Level-3 IOP product suites.

This tutorial will demonstrate how to process PACE OCI L1B data through `l2gen` to retrieve the standard L2 IOP data suite. This tutorial wil also demonstrate how to modify the operation of `l2gen` confifurations based on your research needs. 

[seadas]: https://seadas.gsfc.nasa.gov/
[ocssw]: https://oceandata.sci.gsfc.nasa.gov/ocssw
[Werdell et al., 2013]: https://oceancolor.gsfc.nasa.gov/staff/jeremy/werdell_et_al_2013_ao.pdf

## Learning Objectives

At the end of this notebook you will know:

- How to navigate and open files related to the GIOP within OCSSW directory
- How to process L1B data to retreive L2 IOPs with `l2gen` 
- Modifications you can make to `l2gen` to obtain different IOP products

## Contents

1. [Setup](#1.-Setup)
2. [Search and Access L1B Data ](#2.-Search-and-Access-L1B-Data)
3. [Run `l2gen` with default GIOP configurations](#3.-Run-l2gen-with-default-GIOP-configurations)
4. [Plot L2 IOP data products](#4.-Plot-L2-IOP-data-products)

+++

# 1. Setup

Begin by importing all of the packages used in this notebook. If your kernel uses an environment defined following the guidance on the [tutorials] page, then the imports will be successful.

[tutorials]: https://oceancolor.gsfc.nasa.gov/resources/docs/tutorials/

```{code-cell} ipython3
import csv
import os
from pathlib import Path

import earthaccess
import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
import xarray as xr
```

Next, we'll set up the OCSSW programs. 

<div class="alert alert-warning">

OCSSW programs are typically run using the Bash shell. Here, we employ a Bash shell-in-a-cell using the [IPython magic][magic] command `%%bash` to launch an independent subprocess. In the specific case of OCSSW programs, a suite of required environment variables must be set by executing `source $OCSSWROOT/OCSSW_bash.env`.

</div>

Every `%%bash` cell that calls an OCSSW program needs to `source` this environment definition file shipped with OCSSW, as the environment variables it establishes are not retained from one cell to the next. We do, however, define the `OCSSWROOT` environmental variable in a way that effects every `%%bash` cell. This `OCSSWROOT` variable is just the path to where OCSSW is installed on your system.

[magic]: https://ipython.readthedocs.io/en/stable/interactive/magics.html#built-in-magic-commands

```{code-cell} ipython3
os.environ.setdefault("OCSSWROOT", "/tmp/ocssw")
```

In every cell where we wish to call an OCSSW command, several lines of code need to appear first to establish the required environment. These are shown below, followed by a call to the OCSSW program `install_ocssw` to see which version (tag) of OCSSW is installed.

```{code-cell} ipython3
%%bash
source $OCSSWROOT/OCSSW_bash.env

install_ocssw --installed_tag
```

Tags beginning with "V" are operational tags, while "T" tags are equivalent to a "beta" release for testing by advanced users. This notebook uses OCSSW's new S3 authentication feature, which is still in testing.

+++

## Setting up AWS S3 credentials

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

## Navigating GIOP files in OCSSW

+++

In the 'Run Level-2 Generator (l2gen) OCSSW program on OCI data' tutorial, we learned how to navigate files within the OCSSW directory. 

Let's take a look at the msl12_defaults_IOP.par file:

```{code-cell} ipython3
!cat $OCSSWROOT/share/oci/msl12_defaults_IOP.par
```

**TODO: Figure out why opening this .par file is formatted weird here?**

+++

 Let's discuss some of these parameters: 

* proc_uncertainty=1 (uncertainty propagation mode. 1 =  uncertainty propagation generating error variance)
* l2prod= a bb aph Kd adg_442 adg_s bbp_442 bbp_s rrsdiff aph_unc_442 adg_unc_442 bbp_unc_442 (L2 products to be included in ofile)
* wavelength_3d=400,413,425,442,460,475,490,510,532,555,583,618,640,655,665,678,701 (wavelength output)
* iop_opt=7 (The IOP model used for use in downstream products. 7 = GIOP.)

So, running the 'IOP l2gen suite' produces these L2 data products, with 3D variables containing 17 wavelengths.

+++

To find a couple other useful GIOP options, you can take a look at 'common/msl_defaults.par' and 'oci/msl_defaults.par'. <br>

The common GIOP defaults are:

* giop_fit_opt=1 (GIOP model optimization method. 1 = Levenberg-Marquardt (L-M) fit)
* giop_rrs_opt=0 (GIOP model Rrs to bb/(a+bb) method. 0 = Gordon quadratic (specified with giop_grd))
* giop_aph_opt=2 (GIOP model aph function type. 2 = Bricaud 1998 aph spectrum)
* giop_adg_opt=1 (GIOP model adg function type. 1 = exponential adg function)
* giop_adg_s=0.018 (spectral parameter for adg. Set as default 0.018)
* giop_bbp_opt=3 (GIOP model bbp function type. 3 = power-law with exponent derived via Lee et al. (2002))
* iop_opt=0 (IOP model for use in downstream products. 0 = None)
* raman_opt=2 (Raman scattering Rrs correction options. 2 = Westberry et al. (2013) analytical correction)

The OCI GIOP defaults are:

* giop_wave=[413,442,490,510,555,670] (wavelengths used in L-M optimization)

This means that running `l2gen` on OCI data to get the IOP data suite products will use these default options. The user must make modifications to produce different outputs. 

*Remember, you can find more information about these parameters using 'l2gen --help'.*

+++

## Writing OCSSW parameter files

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

[back to top](#Contents)

+++

# 2. Search and access L1B data 

Let's use the earthaccess Python package to access a L1B file.

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
:scrolled: true

l1b_paths = earthaccess.open(results)
l1b_paths
```

And let's do a quick plot of a `rhot_red` wavelength to see what the data looks like:

```{code-cell} ipython3
dataset = xr.open_datatree(l1b_paths[0])
dataset = xr.merge(dataset.to_dict().values())
dataset = dataset.set_coords(("longitude", "latitude"))
plot = dataset["rhot_red"].sel({"red_bands": 100}).plot()
```

[back to top](#Contents)

+++

# 3. Run `l2gen` with default GIOP configurations

+++

Let's now run `l2gen` using the default GIOP configuration. 

Let's write a .par file that has an ifile, ofile, IOP data suite, and latitude and longitude boundaries. Trust us ... subsetting the L1B file to a smaller region makes processing time faster for this demo!

+++

Let's run it on our L1B file, using the `--use_filename` parameter to parse only the filename for datetime information.
The filename from `l1b_paths` can be passed to the `%%bash` magic via the `-s` argument, but first must be assigned to a `str` variable.

```{code-cell} ipython3
l1b_path = l1b_paths[0].full_name
l1b_name = Path(l1b_path).name
```

Let's also first make a folder called 'data' to store the outputs:

```{code-cell} ipython3
data = Path("data")
data.mkdir(exist_ok=True)
```

```{code-cell} ipython3
par = {
    "ifile": l1b_path,
    "ofile": data / l1b_name.replace("L1B", "L2_IOP"),
    "suite": "IOP",
    "north": 39,
    "south": 35,
    "west": -76,
    "east": -74.5,
}
write_par("l2gen_iop.par", par)
```

A file named "l2gen_iop.par" should now appear in your working directory.

Now, let's run `l2gen` using this new .par file. This can take several minutes.

```{code-cell} ipython3
---
collapsed: true
jupyter:
  outputs_hidden: true
---
%%bash
source $OCSSWROOT/OCSSW_bash.env

l2gen par=l2gen_iop.par
```

You'll know `l2gen` processing is finished when you see "Processing Completed" at the end of the cell output. 

Let's open up this new L2 data using XArray's open_datatree function:

```{code-cell} ipython3
dat = xr.open_datatree(par["ofile"])
dat = xr.merge(dat.to_dict().values())
dat = dat.set_coords(("longitude", "latitude"))
dat
```

We can see the variables included in the IOP data suite. What we don't see are the eigenvalues, or the magnitudes of the IOPs, shown in red in this equation:

$$
r_{rs}(\lambda) = G(\lambda) \cdot \frac{b_{bw}(\lambda) + {\color{red}M_{bp}}\, b^*_{bp}(\lambda)}{a_w(\lambda) + {\color{red}M_{ph}}\, a^*_{ph}(\lambda) + {\color{red}M_{dg}}\, a^*_{dg}(\lambda)}
$$


We have to make a small modification to our l2gen.par file by adding "fit_par_X_giop" to l2prod. The 'fit_par_X_giop products' are the eigenvalues in the order of M_aph, M_adg, M_bbp.

```{code-cell} ipython3
par = {
    "ifile": l1b_path,
    "ofile": data / l1b_name.replace("L1B", "L2_IOP"),
    "suite": "IOP",
    "north": 39,
    "south": 35,
    "west": -76,
    "east": -74.5,
    "l2prod": "fit_par_1_giop fit_par_2_giop fit_par_3_giop a bb aph Kd adg_442 adg_s bbp_442 bbp_s rrsdiff aph_unc_442 adg_unc_442 bbp_unc_442 ",
}
write_par("l2gen_iop.par", par)
```

Let's run `l2gen` again with this new .par file. You will have to delete the previous L2 file, or rename this ofile as some OCSSW functions cannot overwrite files.

```{code-cell} ipython3
---
collapsed: true
jupyter:
  outputs_hidden: true
---
%%bash
source $OCSSWROOT/OCSSW_bash.env

l2gen par=l2gen_iop.par
```

Let's open up this new L2 file to see if the new variables are included:

```{code-cell} ipython3
dat = xr.open_datatree(par["ofile"])
dat = xr.merge(dat.to_dict().values())
dat = dat.set_coords(("longitude", "latitude"))
dat
```

# 4. Plot L2 IOP data products

+++

Let's plot each of the IOP variables:

```{code-cell} ipython3
target_wavelength = 443
wl_idx = dat.wavelength_3d.sel(wavelength_3d=target_wavelength, method="nearest")

vars_to_plot = {
    "fit_par_1_giop": "M_aph",
    "fit_par_2_giop": "M_adg",
    "fit_par_3_giop": "M_bbp",
    "a": f"a [{wl_idx.values:.1f} nm]",
    "bb": f"bb [{wl_idx.values:.1f} nm]",
    "aph": f"aph [{wl_idx.values:.1f} nm]",
    "adg_442": "adg at 442 nm",
    "adg_s": "adg slope",
    "bbp_s": "bbp slope",
}

limits = {
    "fit_par_1_giop": (0, 0.6),  # aph
    "fit_par_2_giop": (0, 0.1),  # adg
    "fit_par_3_giop": (0, 0.01),  # bbp
    "a": (0, 0.1),
    "bb": (0, 0.02),
    "aph": (0, 0.1),
    "adg_442": (0, 0.2),
    "adg_s": (0.015, 0.02),
    "bbp_s": (0, 2),
}

n = len(vars_to_plot)
ncols = 3
nrows = (n + ncols - 1) // ncols
fig, axes = plt.subplots(nrows=nrows, ncols=ncols, figsize=(10, 3 * nrows))
axes = axes.flatten()

for i, (var, title) in enumerate(vars_to_plot.items()):
    ax = axes[i]
    da = dat[var].sel(wavelength_3d=wl_idx) if var in ["a", "bb", "aph"] else dat[var]

    vmin, vmax = limits.get(var, (None, None))

    da.plot(
        ax=ax,
        x="longitude",
        y="latitude",
        cmap="viridis",
        vmin=vmin,
        vmax=vmax,
        cbar_kwargs={"shrink": 0.75, "label": "", "orientation": "vertical"},
        add_labels=False,
    )
    ax.set_title(title, fontsize=14)
    ax.tick_params(labelsize=12)

for j in range(i + 1, len(axes)):
    axes[j].axis("off")

plt.tight_layout()
plt.show()
```

We can also plot the shapes of absorption (a), backscattering (bb), and aph (phytoplankton absorption). Let's choose two pixels from the scene shown in this map:

```{code-cell} ipython3
:lines_to_next_cell: 2

plot = dat.aph.sel({"wavelength_3d": 510}).plot(
    x="longitude", y="latitude", vmin=0, vmax=0.025
)
plt.plot(-74.5, 38, marker="o", color="red", markersize=8)
plt.plot(-74, 35.5, marker="o", color="magenta", markersize=8)
```

```{code-cell} ipython3
lat1, lon1 = 38, -74.5
distance1 = np.sqrt((dat.latitude - lat1) ** 2 + (dat.longitude - lon1) ** 2)
line_idx1, pixel_idx1 = np.unravel_index(distance1.argmin().values, distance1.shape)

lat2, lon2 = 35.5, -74
distance2 = np.sqrt((dat.latitude - lat2) ** 2 + (dat.longitude - lon2) ** 2)
line_idx2, pixel_idx2 = np.unravel_index(distance2.argmin().values, distance2.shape)

wavelengths = dat["wavelength_3d"].values

a1 = dat["a"][line_idx1, pixel_idx1, :].values
bb1 = dat["bb"][line_idx1, pixel_idx1, :].values
aph1 = dat["aph"][line_idx1, pixel_idx1, :].values

a2 = dat["a"][line_idx2, pixel_idx2, :].values
bb2 = dat["bb"][line_idx2, pixel_idx2, :].values
aph2 = dat["aph"][line_idx2, pixel_idx2, :].values

# Calculate min/max for each variable across both pixels
a_min = min(a1.min(), a2.min())
a_max = max(a1.max(), a2.max())

bb_min = min(bb1.min(), bb2.min())
bb_max = max(bb1.max(), bb2.max())

aph_min = min(aph1.min(), aph2.min())
aph_max = max(aph1.max(), aph2.max())

fig, axs = plt.subplots(2, 3, figsize=(8, 6))
fig.text(
    0.5,
    0.95,
    "Location 1: lat=38, lon=-74.5",
    ha="center",
    fontsize=14,
    weight="bold",
    color="red",
)
fig.text(
    0.5,
    0.48,
    "Location 2: lat=35.5, lon=-74",
    ha="center",
    fontsize=14,
    weight="bold",
    color="magenta",
)

axs[0, 0].plot(wavelengths, a1, color="blue")
axs[0, 0].set_title("a (absorption)")
axs[0, 0].set_ylim(a_min, a_max)
axs[0, 0].set_ylabel("m-1")

axs[0, 1].plot(wavelengths, bb1, color="orange")
axs[0, 1].set_title("bb (backscatter)")
axs[0, 1].set_ylim(bb_min, bb_max)

axs[0, 2].plot(wavelengths, aph1, color="green")
axs[0, 2].set_title("aph (phytoplankton)")
axs[0, 2].set_ylim(aph_min, aph_max)

axs[1, 0].plot(wavelengths, a2, color="blue")
axs[1, 0].set_ylabel("m-1")
axs[1, 0].set_ylim(a_min, a_max)
axs[1, 0].set_xlabel("Wavelength (nm)")

axs[1, 1].plot(wavelengths, bb2, color="orange")
axs[1, 1].set_ylim(bb_min, bb_max)
axs[1, 1].set_xlabel("Wavelength (nm)")

axs[1, 2].plot(wavelengths, aph2, color="green")
axs[1, 2].set_ylim(aph_min, aph_max)
axs[1, 2].set_xlabel("Wavelength (nm)")

for ax in axs.flat:
    ax.grid(True)

fig.tight_layout(pad=4.0)

plt.show()
```

# 5. Run GIOP with modifications to the configurations

+++

There are many ways you can configure the GIOP to your research needs. Let's say you want to run the GIOP with a dynamic Sdg calculation instead of the default fixed value at 0.018 nm^-1. We can choose to use the QAA dynamic calculation instead by setting giop_adg_opt to 2 (exponential with exponent derived via Lee et al. (2002)), and removing giop_adg_s from the l2prod in the par file:

```{code-cell} ipython3
par = {
    "ifile": l1b_path,
    "ofile": data / l1b_name.replace("L1B", "L2_IOP_mod"), 
    "suite": "IOP",
    "north": 39,
    "south": 35,
    "west": -76,
    "east": -74.5,
    "giop_adg_opt": 2,
    "l2prod": "fit_par_1_giop fit_par_2_giop fit_par_3_giop a bb aph Kd adg_442 bbp_442 bbp_s rrsdiff aph_unc_442 adg_unc_442 bbp_unc_442 ",
}
write_par("l2gen_iop_mod.par", par)
```

```{code-cell} ipython3
---
collapsed: true
jupyter:
  outputs_hidden: true
---
%%bash
source $OCSSWROOT/OCSSW_bash.env

l2gen par=l2gen_iop_mod.par
```

```{code-cell} ipython3
dat_mod = xr.open_datatree(par["ofile"])
dat_mod = xr.merge(dat_mod.to_dict().values())
dat_mod = dat_mod.set_coords(("longitude", "latitude"))
dat_mod
```

```{code-cell} ipython3
fig, ax = plt.subplots()

x = dat["adg_442"]
y = dat_mod["adg_442"]

ax.scatter(x, y, s=20)
ax.set_xlabel("Fixed Sdg")
ax.set_ylabel("QAA dynamic calculation of Sdg")
ax.plot([0, 1], [0, 1], transform=ax.transAxes, color="black")
ax.set_ylim(bottom=0)
ax.set_xlim(left=0)

plt.show()
```

[back to top](#Contents)

<div class="alert alert-info" role="alert">

You have completed the tutorial "Running the Generalized Inherent Optical Property (GIOP) inversion model in the Level-2 Generator (l2gen) OCSSW program on OCI data". We suggest looking at the tutorial "_____"
</div>
