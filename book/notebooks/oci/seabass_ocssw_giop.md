---
kernelspec:
  display_name: Python 3 (ipykernel)
  language: python
  name: python3
---

# Run the Generalized Inherent Optical Property (GIOP) inversion model in the Level-2 Generator (l2gen) OCSSW program on in situ SeaBASS data

**Authors:** Anna Windle (NASA, SSAI), Jeremy Werdell (NASA) 

<div class="alert alert-success" role="alert">

The following notebooks are **prerequisites** for this tutorial.

- Learn with OCI: [Data Access][oci-data-access]
- Learn with OCI: [Installing and Running OCSSW Command-line Tools][ocssw_install]
- Learn with OCI: [Run Level-2 Generator (l2gen) OCSSW program on OCI data][ocssw_l2gen]
- Learn with OCI: [Run the Generalized Inherent Optical Property (GIOP) inversion model in the Level-2 Generator (l2gen) OCSSW program on OCI data][ocssw_giop]

</div>

<div class="alert alert-info" role="alert">

An [Earthdata Login][edl] account is required to access data from the NASA Earthdata system, including NASA ocean color data.

</div>

[edl]: https://urs.earthdata.nasa.gov/
[oci-data-access]: https://oceancolor.gsfc.nasa.gov/resources/docs/tutorials/notebooks/oci_data_access/
[ocssw_install]: https://oceancolor.gsfc.nasa.gov/resources/docs/tutorials/notebooks/oci_ocssw_install/
[ocssw_l2gen]: tbd
[ocssw_giop]: tbd

## Summary 

The [OceanColor Science SoftWare][ocssw] (OCSSW) repository is the operational data processing software package of NASA's Ocean Biology Distributed Active Archive Center (OB.DAAC). OCSSW is publically available through the OB.DAAC's [Sea, earth, and atmosphere Data Analysis System][seadas] (SeaDAS) application, which provides a complete suite of tools to process, display and analyze ocean color data. SeaDAS provides a graphical user interface (GUI) for OCSSW, but command line interfaces (CLI) also exist, which we can use to write processing scripts and notebooks without the desktop application.

In previous tutorials, we demonstrated how to run the Level-2 Generator (`l2gen`) program to generate aquatic Level-2 (L2) data products from calibrated top-of-atmosphere (TOA) radiances. We also demonstrated how to run the GIOP inversion model within `l2gen` to produce inherent optical properties (IOPs). `l2gen` and the GIOP model were designed to work on satellite data; however, `l2gen` includes the ability to process a "SeaBASS-formatted" ASCII file with Rrs values. NASA SeaWiFS Bio-optical Archive and Storage System [(SeaBASS)][seabass] is a publicly accessible data archive that stores and distributes in situ oceanographic data, especially those collected for ocean color remote sensing research.

This tutorial will show you how to modify an existing SeBASS file to process through `l2gen` to retrieve IOP data products. 

[seadas]: https://seadas.gsfc.nasa.gov/
[ocssw]: https://oceandata.sci.gsfc.nasa.gov/ocssw
[seabass]: https://seabass.gsfc.nasa.gov/

## Learning Objectives

At the end of this notebook you will know:

- How to use SeaBASS software tools to open a SeaBASS (.sb) file
- How to format a SeaBASS file to run through GIOP within `l2gen` to produce IOPs


## Contents

1. [Setup](#1.-Setup)
2. [Search and Access L1B Data ](#2.-Search-and-Access-L1B-Data)
3. [Extract L1B data with l1bextract_oci](#3.-Extract-L1B-data-with-l1bextract_oci)
4. [Run l2gen and plot IOP outputs](#4.-Run-l2gen-and-plot-IOP-outputs)

+++

# 1. Setup

Begin by importing all of the packages used in this notebook. If your kernel uses an environment defined following the guidance on the [tutorials] page, then the imports will be successful.

[tutorials]: https://oceancolor.gsfc.nasa.gov/resources/docs/tutorials/

```{code-cell} ipython3
import csv
import os

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
ocsswroot = os.environ.setdefault("OCSSWROOT", "/tmp/ocssw")
```

In every cell where we wish to call an OCSSW command, several lines of code need to appear first to establish the required environment. These are shown below, followed by a call to the OCSSW program `install_ocssw` to see which version (tag) of OCSSW is installed.

```{code-cell} ipython3
%%bash
source $OCSSWROOT/OCSSW_bash.env

install_ocssw --installed_tag
```

## Import SeaBASS software tools

+++

Now, we'll import the [SeaBASS Utilities python package][seabass_software]. The *sb_utilities* package is a collection of Python utilities developed to assist with SeaBASS data processing, file manipulation, and mapping tasks, originally developed at NASA Goddard Space Flight Center (GSFC). We will use a pip install to install the python package. You will need to resart the kernel 

[seabass_software]: https://seabass.gsfc.nasa.gov/wiki/seabass_tools#SeaBASS%20Utilities%20python%20package

```{code-cell} ipython3
!pip install https://seabass.gsfc.nasa.gov/wiki/seabass_tools/sb_utilities-0.0.2.tar.gz
```

**TODO: change this so it grabs the latest version? I had 0.0.1, and didn't realize it changed to 0.0.2**

```{code-cell} ipython3
import sb_utilities as sb
```

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

# 2. Open a SeaBASS file

+++

We will use the .sb_read() function to read a FCHECK-verified SeaBASS formatted data file. Let's look at the docstring for this function.

```{code-cell} ipython3
?sb.sb_read
```

We will open a SeaBASS file with AOP data collected during the TARA Europa campaign. 

```{code-cell} ipython3
sb_file = sb.sb_read(
    "/home/jovyan/shared-public/pace-hackweek/3ad94b4194_TaraEuropa_HyperPro_20240524_Ed_Lu_Lw_Rrs_R2.sb",
    no_warn=True,
)
sb_dat = pd.DataFrame(sb_file.data)
sb_dat.set_index("wavelength", inplace=True)
sb_dat
```

You can see that the in situ Rrs was collected in wavelength values slightly different from OCI's. We need to interpolate the in situ Rrs values to match OCI wavelength values. 

```{code-cell} ipython3
:lines_to_end_of_cell_marker: 2

oci_wv = np.array([314.550, 316.239, 318.262, 320.303, 322.433, 324.649, 326.828, 328.988,  
331.305, 333.958, 336.815, 339.160, 341.321, 343.632, 346.017, 348.468,  
350.912, 353.344, 355.782, 358.235, 360.695, 363.137, 365.610, 368.083,  
370.534, 372.991, 375.482, 377.926, 380.419, 382.876, 385.359, 387.811,  
390.297, 392.764, 395.238, 397.706, 400.178, 402.654, 405.127, 407.605,  
410.074, 412.557, 415.025, 417.512, 419.988, 422.453, 424.940, 427.398,  
429.885, 432.379, 434.869, 437.351, 439.828, 442.327, 444.811, 447.309,  
449.795, 452.280, 454.769, 457.262, 459.757, 462.252, 464.737, 467.244,  
469.729, 472.202, 474.700, 477.189, 479.689, 482.183, 484.689, 487.182,  
489.674, 492.176, 494.686, 497.182, 499.688, 502.190, 504.695, 507.198,  
509.720, 512.213, 514.729, 517.219, 519.747, 522.249, 524.771, 527.276,  
529.798, 532.314, 534.859, 537.346, 539.878, 542.395, 544.904, 547.441,  
549.994, 552.511, 555.044, 557.576, 560.104, 562.642, 565.190, 567.710,  
570.259, 572.796, 575.343, 577.902, 580.450, 582.996, 585.553, 588.086,  
590.548, 593.084, 595.679, 598.262, 600.545, 602.920, 605.461, 607.986,  
610.360, 612.730, 615.145, 617.605, 620.061, 622.530, 624.988, 627.434,  
629.898, 632.376, 634.830, 637.305, 639.791, 641.029, 642.255, 643.479,  
644.716, 645.966, 647.188, 648.435, 649.667, 650.913, 652.153, 653.388,  
654.622, 655.869, 657.101, 658.340, 659.600, 660.833, 662.067, 663.300,  
664.564, 665.795, 667.023, 668.263, 669.518, 670.755, 671.990, 673.245,  
674.503, 675.731, 676.963, 678.208, 679.448, 680.680, 681.919, 683.171,  
684.417, 685.657, 686.894, 688.143, 689.394, 690.647, 691.888, 693.130,  
694.382, 695.644, 696.891, 698.118, 699.376, 700.612, 701.858, 703.097,  
704.354, 705.593, 706.833, 708.089, 709.337, 710.581, 711.826, 713.068,  
714.316, 716.817, 719.298, 721.800, 724.303, 726.796, 729.299, 731.790,  
734.281, 736.791, 739.287, 740.535, 741.785, 743.046, 744.286, 745.534,  
746.789, 748.041])
```

```{code-cell} ipython3
interpolated_sb_dat = pd.DataFrame(
    data={
        col: np.interp(oci_wv, sb_dat.index.values, sb_dat[col].values)
        for col in sb_dat.columns
    },
    index=oci_wv,
)
interpolated_sb_dat
```

Let's do a quick look of Rrs from 400 to 700 nm:

```{code-cell} ipython3
interpolated_sb_dat.rrs.plot(ylabel="Rrs", marker="o", xlim=(400, 700))
```

We need to include some other information such as the year, month, day, hour, min, second, lat, lon, and solar zenith angle (solz). We'll pull this from the header information of the SeaBASS file.

```{code-cell} ipython3
sb_date = sb_file.headers["start_date"].replace("'", "")
year = int(sb_date[:4])
month = int(sb_date[4:6])
day = int(sb_date[6:8])

sb_time = sb_file.headers["start_time"].replace("'", "")
hour = int(sb_time[:2])
min = int(sb_time[3:5])
second = int(sb_time[6:8])

lat = sb_file.headers["north_latitude"].replace("'", "")[:7]
lon = sb_file.headers["east_longitude"].replace("'", "")[:7]

solz = int(40.2)
```

Now, we'll use this function to write a pandas dataframe to a SeaBASS-style file for use in `l2gen`:

```{code-cell} ipython3
def write_sb(df, sensor, filename):
    """
    Write pandas dataframe to seabass-style file.

    Parameters:
        df (pd.DataFrame): dataframe containing the data
        sensor (str): sensor name to include in header
        filename (str): output file path
    """
    # Build the header
    header_lines = [
        "/begin_header",
        "/missing=-9999",
        "/delimiter=comma",
        f"/sensor={sensor}",
        "/fields=year,month,day,hour,minute,second,lat,lon,solz,"
        "rrs_314.550, rrs_316.239, rrs_318.262, rrs_320.303, rrs_322.433, rrs_324.649,"
        "rrs_326.828, rrs_328.988, rrs_331.305, rrs_333.958, rrs_336.815, rrs_339.160,"
        "rrs_341.321, rrs_343.632, rrs_346.017, rrs_348.468, rrs_350.912, rrs_353.344,"
        "rrs_355.782, rrs_358.235, rrs_360.695, rrs_363.137, rrs_365.610, rrs_368.083,"
        "rrs_370.534, rrs_372.991, rrs_375.482, rrs_377.926, rrs_380.419, rrs_382.876,"
        "rrs_385.359, rrs_387.811, rrs_390.297, rrs_392.764, rrs_395.238, rrs_397.706,"
        "rrs_400.178, rrs_402.654, rrs_405.127, rrs_407.605, rrs_410.074, rrs_412.557,"
        "rrs_415.025, rrs_417.512, rrs_419.988, rrs_422.453, rrs_424.940, rrs_427.398,"
        "rrs_429.885, rrs_432.379, rrs_434.869, rrs_437.351, rrs_439.828, rrs_442.327,"
        "rrs_444.811, rrs_447.309, rrs_449.795, rrs_452.280, rrs_454.769, rrs_457.262,"
        "rrs_459.757, rrs_462.252, rrs_464.737, rrs_467.244, rrs_469.729, rrs_472.202,"
        "rrs_474.700, rrs_477.189, rrs_479.689, rrs_482.183, rrs_484.689, rrs_487.182,"
        "rrs_489.674, rrs_492.176, rrs_494.686, rrs_497.182, rrs_499.688, rrs_502.190,"
        "rrs_504.695, rrs_507.198, rrs_509.720, rrs_512.213, rrs_514.729, rrs_517.219,"
        "rrs_519.747, rrs_522.249, rrs_524.771, rrs_527.276, rrs_529.798, rrs_532.314,"
        "rrs_534.859, rrs_537.346, rrs_539.878, rrs_542.395, rrs_544.904, rrs_547.441,"
        "rrs_549.994, rrs_552.511, rrs_555.044, rrs_557.576, rrs_560.104, rrs_562.642,"
        "rrs_565.190, rrs_567.710, rrs_570.259, rrs_572.796, rrs_575.343, rrs_577.902,"
        "rrs_580.450, rrs_582.996, rrs_585.553, rrs_588.086, rrs_590.548, rrs_593.084,"
        "rrs_595.679, rrs_598.262, rrs_600.545, rrs_602.920, rrs_605.461, rrs_607.986,"
        "rrs_610.360, rrs_612.730, rrs_615.145, rrs_617.605, rrs_620.061, rrs_622.530,"
        "rrs_624.988, rrs_627.434, rrs_629.898, rrs_632.376, rrs_634.830, rrs_637.305,"
        "rrs_639.791, rrs_641.029, rrs_642.255, rrs_643.479, rrs_644.716, rrs_645.966,"
        "rrs_647.188, rrs_648.435, rrs_649.667, rrs_650.913, rrs_652.153, rrs_653.388,"
        "rrs_654.622, rrs_655.869, rrs_657.101, rrs_658.340, rrs_659.600, rrs_660.833,"
        "rrs_662.067, rrs_663.300, rrs_664.564, rrs_665.795, rrs_667.023, rrs_668.263,"
        "rrs_669.518, rrs_670.755, rrs_671.990, rrs_673.245, rrs_674.503, rrs_675.731,"
        "rrs_676.963, rrs_678.208, rrs_679.448, rrs_680.680, rrs_681.919, rrs_683.171,"
        "rrs_684.417, rrs_685.657, rrs_686.894, rrs_688.143, rrs_689.394, rrs_690.647,"
        "rrs_691.888, rrs_693.130, rrs_694.382, rrs_695.644, rrs_696.891, rrs_698.118,"
        "rrs_699.376, rrs_700.612, rrs_701.858, rrs_703.097, rrs_704.354, rrs_705.593,"
        "rrs_706.833, rrs_708.089, rrs_709.337, rrs_710.581, rrs_711.826, rrs_713.068,"
        "rrs_714.316, rrs_716.817, rrs_719.298, rrs_721.800, rrs_724.303, rrs_726.796,"
        "rrs_729.299, rrs_731.790, rrs_734.281, rrs_736.791, rrs_739.287, rrs_740.535,"
        "rrs_741.785, rrs_743.046, rrs_744.286, rrs_745.534, rrs_746.789, rrs_748.041,"
        "/end_header",
    ]
    
    data_lines = f"{year},{month},{day},{hour},{min},{second},{lat},{lon},{solz}," + ", ".join(f"{v:.7f}" for v in df.iloc[:, 0])
    dat = pd.DataFrame()

    # Open file for writing
    with open(filename, "w") as f:
        # Write header
        for line in header_lines:
            f.write(line + "\n")

        # Add data lines
        f.write(data_lines + "\n")
        

        # Write data
        dat.to_csv(f, index=False, header=False, na_rep="-9999")
```

```{code-cell} ipython3
new_sb = write_sb(
    df=pd.DataFrame(interpolated_sb_dat.rrs), sensor="OCI", filename="new_sb.sb"
)
```

We will create a .par file for `l2gen` like we've done in previous tutorials. The ifile will be the new .sb file and the output will be a .nc file.

```{code-cell} ipython3
par = {
    "ifile": "/home/jovyan/oceandata-notebooks/notebooks/oci/new_sb.sb",
    "ofile": "/home/jovyan/oceandata-notebooks/notebooks/oci/sb_GIOP.nc",
    "suite": "IOP",
    "atmocor": "off",
    "proc_uncertainty": 0,
    "iop_opt": 7,
    "l2prod": "fit_par_1_giop fit_par_2_giop fit_par_3_giop a bb aph Kd adg_442 adg_s bbp_442 bbp_s rrsdiff aph_unc_442 adg_unc_442 bbp_unc_442 ",
}
write_par("sb_l2gen.par", par)
```

```{code-cell} ipython3
:scrolled: true

%%bash
source $OCSSWROOT/OCSSW_bash.env

l2gen par=sb_l2gen.par
```

Let's use XArray to open the .nc:

```{code-cell} ipython3
dat = open_datatree(par["ofile"])
dat = xr.merge(dat.to_dict().values())
dat = dat.set_coords(("longitude", "latitude"))
dat
```

```{code-cell} ipython3
print(
    "aph =",
    dat.fit_par_1_giop[0, 0].values,
    "adg =",
    dat.fit_par_2_giop[0, 0].values,
    "bbp =",
    dat.fit_par_3_giop[0, 0].values,
)
```

```{code-cell} ipython3
:scrolled: true

fig, axs = plt.subplots(1, 3, figsize=(6, 2), sharex=True)

wavelength = dat.wavelength_3d

# Plot on each subplot
axs[0].plot(wavelength, dat.a[0, 0, :], color="blue")
axs[0].set_title("a")

axs[1].plot(wavelength, dat.bb[0, 0, :], color="orange")
axs[1].set_title("bb")
axs[1].set_xlabel("Wavelength (nm)")

axs[2].plot(wavelength, dat.aph[0, 0, :], color="green")
axs[2].set_title("aph")

for ax in axs.flat:
    ax.grid(True)

# Adjust layout
plt.tight_layout()
plt.show()
```

```{code-cell} ipython3
adg = dat.a[0, 0] - dat.aph[0, 0]
plt.plot(wavelength, adg, color="orange")
```

```{code-cell} ipython3
dat = xr.open_datatree("sb_GIOP_alex.nc")
dat = xr.merge(dat.to_dict().values())
dat = dat.set_coords(("longitude", "latitude"))
dat
```

```{code-cell} ipython3
print(
    "aph =",
    dat.fit_par_1_giop[0, 0].values,
    "adg =",
    dat.fit_par_2_giop[0, 0].values,
    "bbp =",
    dat.fit_par_3_giop[0, 0].values,
)
```

```{code-cell} ipython3
fig, axs = plt.subplots(1, 3, figsize=(6, 2), sharex=True)

wavelength = dat.wavelength_3d

# Plot on each subplot
axs[0].plot(wavelength, dat.a[0, 0, :], color="blue")
axs[0].set_title("a")

axs[1].plot(wavelength, dat.bb[0, 0, :], color="orange")
axs[1].set_title("bb")
axs[1].set_xlabel("Wavelength (nm)")

axs[2].plot(wavelength, dat.aph[0, 0, :], color="green")
axs[2].set_title("aph")

for ax in axs.flat:
    ax.grid(True)

# Adjust layout
plt.tight_layout()
plt.show()
```

```{code-cell} ipython3

```
