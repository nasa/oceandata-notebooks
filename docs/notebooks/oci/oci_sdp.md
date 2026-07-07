---
jupytext:
  cell_metadata_filter: all,-trusted
  notebook_metadata_filter: -all,kernelspec,jupytext
  text_representation:
    extension: .md
    format_name: myst
    format_version: 0.13
    jupytext_version: 1.16.0
kernelspec:
  display_name: custom
  language: python
  name: custom
---

# Applying Spectral Derivative Pigment (SDP) Phytoplankton Community Composition Algorithm to OCI data

**Author(s):** Anna Windle (NASA, SSAI), Max Danenhower (Bowdoin College), Sasha Kramer (Boston University)

Last updated: July 7, 2026

<div class="alert alert-success" role="alert">

The following notebooks are **prerequisites** for this tutorial.

- Learn with OCI: [Data Access][oci-data-access]

</div>

<div class="alert alert-info" role="alert">

An [Earthdata Login][edl] account is required to access data from the NASA Earthdata system, including NASA ocean color data.

</div>

[edl]: https://urs.earthdata.nasa.gov/
[oci-data-access]: /notebooks/oci_data_access/

## Summary

This notebook applies the inversion algorithm described in [Kramer et al., 2022][Kramer-et-al] to estimate phytoplankton pigment concentrations from PACE OCI Rrs data. This algorithm, called Spectral Derivative Pigment (SDP), is currently being implemented in OBPG's OCSSW software. This work was originally [developed in MatLab](https://github.com/sashajane19/Rrs_pigments) by Sasha Kramer and subsequently [translated to Python](https://github.com/max-danenhower/rrs-SDP-pigments/) by Max Danenhower. This tutorial demonstrates how to apply the Python SDP algorithm to Level-2 (L2) PACE OCI data.

[Kramer-et-al]: https://doi.org/10.1016/j.rse.2021.112879

## Learning Objectives

At the end of this notebook you will know:

- How to use a packaged Python project
- How to run the SDP algorithm on PACE OCI L2 data

+++

## 1. Setup

The SDP Python code has been packaged to allow it to be easily installed, imported, and reused.
While the package is not on PyPI or conda-forge, it can be installed directly from the [source repository][sdp] on GitHub.
If you have followed the setup instructions, then SDP is available to import along with the other packages needed for this notebook.

[sdp]: https://github.com/max-danenhower/rrs-SDP-pigments/

```{code-cell} ipython3
import cartopy.crs as ccrs
import cartopy.feature as cfeature
import earthaccess
import matplotlib.pyplot as plt
import numpy as np
import xarray as xr

crs = ccrs.PlateCarree()
```

```{code-cell} ipython3
pip install ray openpyxl #scikit-learn 
```

```{code-cell} ipython3
import sys
from pathlib import Path

sys.path.insert(0, str(Path("src").resolve()))
import sdp
from sdp.core import sdp_from_pace
```

Set (and persist to your home directory on the host, if needed) your Earthdata Login credentials.

```{code-cell} ipython3
auth = earthaccess.login()
```

# 2. Access and open data

We need the following data to run SDP:
* Rrs: PACE OCI Level-2 AOP data products
* Sea surface salinity: JPL SMAP-SSS V5.0 CAP, 8-day running mean, level 3 mapped, sea surface salinity (SSS) product from the NASA Soil Moisture Active Passive (SMAP) observatory
* Sea surface temperature: Group for High Resolution Sea Surface Temperature (GHRSST) Level 4 sea surface temperature

We can use `earthaccess` to find PACE OCI l2 data. We will use a specific granule using the `granule_name` argument:

```{code-cell} ipython3
results = earthaccess.search_data(
    short_name=["PACE_OCI_L2_AOP_NRT"],
    granule_name='*20260505T173406*')  
results
```

```{code-cell} ipython3
paths = earthaccess.open(results)
paths
```

```{code-cell} ipython3
paths[1]
```

Let's take a quick look at Rrs at 500nm:

```{code-cell} ipython3
datatree = xr.open_datatree(paths[1])
rrs = datatree["geophysical_data"]["Rrs"]
for item in ("longitude", "latitude"):
    rrs[item] = datatree["navigation_data"][item]
rrs
```

```{code-cell} ipython3
fig, ax = plt.subplots(figsize=(8, 6), subplot_kw={"projection": crs})

data = rrs.sel({"wavelength": 500}, method="nearest")
data.plot(
    x="longitude",
    y="latitude",
    vmin=0,
    vmax=0.008,
    ax=ax,
    cbar_kwargs={"label": "Rrs ($sr^{-1}$)"},
)

#ax.set_extent([-135, -115, 35, 55], crs=crs)
ax.coastlines(resolution="10m")
ax.add_feature(cfeature.BORDERS, linestyle=":")
ax.gridlines(
    draw_labels=["left", "bottom"],
    linewidth=0.5,
    color="gray",
    alpha=0.5,
    linestyle="--",
)
plt.show()
```

We can use the `load_data()` function to download sss and sst:

TODO: could move this to core.py?

```{code-cell} ipython3
def load_data(tspan):
    '''
    Downloads one L2 PACE apparent optical properties (AOP) file that intersects the coordinate box passed in, as well as 
    temperature and salinity files. Data files are saved to local folders named 'L2_rrs_data', 'sal_data', and 'temp_data'.

    Parameters:
    -----------
    tspan : tuple of str
        A tuple containing two strings both with format 'YYYY-MM-DD'. The first date in the tuple must predate the second date in the tuple.
    bbox : tuple of floats or ints
        A tuple representing spatial bounds in the form (lower_left_lon, lower_left_lat, upper_right_lon, upper_right_lat).

    Returns:
    --------
    list
        A list of file paths to a PACE L2 AOP files intersecting the passed in bounding box.
    string
        A single file path to a salinity file.
    string
        A single file path to a temperature file.
    '''

    #L2_results = earthaccess.search_data(
    #    short_name='PACE_OCI_L2_AOP',
    #    bounding_box=bbox,
    #    temporal=tspan
    #)
    #if (len(L2_results) > 0):
    #    L2_paths = earthaccess.download(L2_results, 'L2_rrs_data')
    #else:
    #    L2_paths = []
     #   print('No L2 AOP data found')

    sal_results = earthaccess.search_data(
        short_name='SMAP_JPL_L3_SSS_CAP_8DAY-RUNNINGMEAN_V5',
        temporal=tspan,
        count=1
    )
    if (len(sal_results) > 0):
        sal_paths = earthaccess.download(sal_results, 'sal_data')
    else:
        sal_paths = []
        print('No salinity data found')

    temp_results = earthaccess.search_data(
        short_name='MUR-JPL-L4-GLOB-v4.1',
        temporal=tspan,
        count=1
    )
    if (len(temp_results) > 0):
        temp_paths = earthaccess.download(temp_results, 'temp_data')
    else:
        temp_paths = []
        print('No temperature data found')

    return sal_paths[0], temp_paths[0]

load_data(tspan = ("2026-05-05", "2026-05-05"))  #2026-03-03", "2026-03-03
```

## 2. Run SDP on L2 Data

Now we're ready to run SDP. Let's name what we want the outfile to be:

```{code-cell} ipython3
output_file = paths[1].full_name.split("/")[-1]
output_file = output_file.replace(".nc", "_SDP_pigments.nc")
output_file
```

And then run it! Note that it will run up memory and blow up in the cloud......

```{code-cell} ipython3
%%time

sdp_from_pace(paths[1], output_file, 
             sss_file='/glusteruser/awindled/rrs-SDP-pigments/sal_data/SMAP_L3_SSS_20260501_8DAYS_V5.0.nc',
             sst_file='/glusteruser/awindled/rrs-SDP-pigments/temp_data/20260505090000-JPL-L4_GHRSST-SSTfnd-MUR-GLOB-v02.0-fv04.1.nc')
```

TODO: should we get rid of warnings? should we use ray?

+++

# 3. Open and plot SDP output

```{code-cell} ipython3
dat = xr.open_dataset('PACE_OCI.20260505T173406.L2.OC_AOP.V3_2.NRT_SDP_pigments.nc')
dat
```

You can see all the different pigment concentrations derived for our L2 granule. Let's plot them:

```{code-cell} ipython3
bbox = (-77, 30, -60, 42)
variables = [
    "chla", "chlb", "chlc", "zea", "dvchla", "butfuco", 
    "hexfuco", "allo", "neo", "viola", "fuco", "chlc3", "perid"
]
 
 
fig, axs = plt.subplots(4, 4, figsize=(20, 16), subplot_kw={"projection": crs})
 
# Iterate over all 16 subplots
for i, ax in enumerate(axs.flat):
    if i < len(variables):
        var = variables[i]

        data = dat[var]
        lon = dat["longitude"]
        lat = dat["latitude"]
 
        vmin = np.nanpercentile(data, 0)
        vmax = np.nanpercentile(data, 98)
 
        # Add land features
        ax.add_feature(cfeature.LAND, facecolor='lightgray', edgecolor='black', linewidth=0.5)
        ax.add_feature(cfeature.COASTLINE, linewidth=1)
        ax.add_feature(cfeature.BORDERS, linewidth=0.5, linestyle='--', alpha=0.5)
        ax.add_feature(cfeature.LAKES, facecolor='lightgray', alpha=0.7)
 
        im = ax.pcolormesh(
            lon, lat, data, 
            cmap="viridis", 
            shading="auto", 
            zorder=10,
            vmin=vmin,    
            vmax=vmax,
            transform=ccrs.PlateCarree() # Ensures coordinates map correctly
        )
 
        ax.gridlines(
            draw_labels=["left", "bottom"],
            linewidth=0.5,
            color="gray",
            alpha=0.5,
            linestyle="--",
        )
        # Set title as the variable name
        ax.set_title(var.upper())
        # Set map extent based on bbox bounds
        ax.set_xlim(bbox[0], bbox[2])
        ax.set_ylim(bbox[1], bbox[3])
 
        cbar = fig.colorbar(im, ax=ax, orientation="vertical", shrink=0.50, pad=0.04)
        cbar.set_label(f"{var} (mg m$^{{-3}}$)")  
    else:
        # Hide any unused subplots
        ax.set_visible(False)
 
plt.tight_layout() 

# Save the figure - optional
plt.savefig('SDP_all_pigments_map_linear.png', dpi=300, bbox_inches='tight')

plt.show()
```
