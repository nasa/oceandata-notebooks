---
jupytext:
  cell_metadata_filter: all,-trusted
  notebook_metadata_filter: -all,kernelspec,jupytext
  text_representation:
    extension: .md
    format_name: myst
    format_version: 0.13
    jupytext_version: 1.19.4
kernelspec:
  name: python3
  display_name: Python 3 (ipykernel)
  language: python
---

# Applying Spectral Derivative Pigment (SDP) Phytoplankton Community Composition Algorithm to OCI data

**Author(s):** Anna Windle (NASA, SSAI), Ian Carroll (NASA, UMBC) <br>
Adatped from code developed by: Max Danenhower (Bowdoin College), Sasha Kramer (Boston University)

Last updated: July 21, 2026

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

+++

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
from sdp import sdp_from_pace
```

Set (and persist to your home directory on the host, if needed) your Earthdata Login credentials.

```{code-cell} ipython3
auth = earthaccess.login()
```

# 2. Access and open data

We need the following data to run SDP:
* Rrs: PACE OCI L2 AOP data products
* Sea surface salinity: JPL SMAP-SSS V5.0 CAP, 8-day running mean, level 3 mapped, sea surface salinity (SSS) product from the NASA Soil Moisture Active Passive (SMAP) observatory
* Sea surface temperature: Group for High Resolution Sea Surface Temperature (GHRSST) Level 4 sea surface temperature

We can use `earthaccess` to find PACE OCI L2 data. 

```{code-cell} ipython3
tspan = ("2026-05-05 17:35", "2026-05-05 17:35")
results = earthaccess.search_data(
    short_name=["PACE_OCI_L2_AOP", "PACE_OCI_L2_AOP_NRT"],
    temporal=tspan,
    count=1,
)  
paths = earthaccess.open(results)
```

Let's take a quick look at Rrs at 500nm:

```{code-cell} ipython3
datatree = xr.open_datatree(paths[-1])
rrs = datatree["geophysical_data"]["Rrs"]
for item in ("longitude", "latitude"):
    rrs[item] = datatree["navigation_data"][item]
rrs
```

```{code-cell} ipython3
crs = ccrs.PlateCarree()
fig, ax = plt.subplots(figsize=(8, 6), subplot_kw={"projection": crs})

da = rrs.sel({"wavelength": 500}, method="nearest")
da.plot(
    x="longitude",
    y="latitude",
    vmin=0,
    vmax=0.008,
    ax=ax,
    cbar_kwargs={"label": "Rrs ($sr^{-1}$)"},
)

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

Now, we can use `sdp_from_pace` to calculate phytoplankton pigment concentrations for this data. Let's take a look at the docstring for this function:

```{code-cell} ipython3
?sdp_from_pace
```

You can see that this function accepts a bounding box (`bbox`) as a parameter. The default is `bbox=None`, meaning the algorithm is applied to every single pixel in the L2 granule, which can take a significnat amount of time and may exceed available system memory. We will supply the bbox parameter with the following coordinates: 38 N, 35 S, -70 E, -67 W.

```{code-cell} ipython3
bbox = (-69.3, 35.2, -67.5, 37)

lon_min, lat_min, lon_max, lat_max = bbox
rect_lon = [lon_min, lon_max, lon_max, lon_min, lon_min]
rect_lat = [lat_min, lat_min, lat_max, lat_max, lat_min]
ax.plot(rect_lon, rect_lat, color="red", linewidth=2)

fig
```

We need to find corresponding sea-surface salinity and temperature data for the SDP algorithm.

```{code-cell} ipython3
results = earthaccess.search_data(
    short_name='SMAP_JPL_L3_SSS_CAP_8DAY-RUNNINGMEAN_V5',
    temporal=tspan,
    count=1,
)
sss_paths = earthaccess.open(results)
```

```{code-cell} ipython3
results = earthaccess.search_data(
    short_name='MUR-JPL-L4-GLOB-v4.1',
    temporal=tspan,
    count=1
)
sst_paths = earthaccess.open(results)
```

## 2. Run SDP on L2 Data

Now we're ready to run SDP. Let's name what we want the outfile to be:

```{code-cell} ipython3
output_file = paths[-1].full_name.split("/")[-1]
output_file = output_file.replace(".nc", "_SDP_pigments.nc")
output_file
```

And let's run it!

```{code-cell} ipython3
sdp_from_pace(
    paths[-1],
    output_file,
    sss_file=sss_paths[-1],
    sst_file=sst_paths[-1],
    bbox=bbox
)
```

# 3. Open and plot SDP output

Let's open the new file:

```{code-cell} ipython3
dat = xr.open_dataset(output_file)
dat
```

You can see all the different pigment concentrations derived for our L2 granule. Let's plot them:

```{code-cell} ipython3
variables = [
    "chla",
    "chlb",
    "chlc",
    "zea",
    "dvchla",
    "butfuco",
    "hexfuco",
    "allo",
    "neo",
    "viola",
    "fuco",
    "chlc3",
    "perid",
]

nrows, ncols = 5, 3

fig, axs = plt.subplots(
    nrows,
    ncols,
    figsize=(8, 8),
)

axs = axs.ravel()

for i, ax in enumerate(axs):

    if i >= len(variables):
        ax.set_visible(False)
        continue

    var = variables[i]

    data = dat[var]
    lon = dat.longitude
    lat = dat.latitude

    data_log = np.log10(data.where(data > 0))

    vmin = np.nanpercentile(data, 1)
    vmax = np.nanpercentile(data, 99)

    im = ax.pcolormesh(lon, lat, data, cmap="viridis", shading="auto", vmin=vmin, vmax=vmax)


    gl.top_labels = False
    gl.right_labels = False
    gl.left_labels = i % ncols == 0
    gl.bottom_labels = i >= (nrows - 1) * ncols

    ax.set_xlim(bbox[0], bbox[2])
    ax.set_ylim(bbox[1], bbox[3])
    ax.set_title(var)

    cbar = fig.colorbar(
        im,
        ax=ax,
        #shrink=0.75,
        pad=0.02,
    )
    cbar.set_label("mg m$^{-3}$")

plt.tight_layout()
plt.show()
```

```{code-cell} ipython3

```
