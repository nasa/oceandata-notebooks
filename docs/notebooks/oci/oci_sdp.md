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

**Author(s):** Anna Windle (NASA, SSAI), Ian Carroll (NASA, UMBC), Max Danenhower (Bowdoin College), Sasha Kramer (Boston University)

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

- About searching for auxiliary data for the SDP algorithm
- How to run the SDP algorithm on PACE OCI L2 data

+++

## 1. Setup

+++

The SDP algorithm has been implemented as a Python package, so it can be easily installed, imported, and reused.
While the package is not on PyPI or conda-forge, it can be installed directly from the [source repository][sdp] on GitHub.
If you have followed the setup instructions, then `sdp` is available to import along with the other packages needed for this notebook.

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

## 2. Access and open data

+++

We need the following data to run SDP:
* Remote sensing reflectance (Rrs): PACE OCI L2 AOP data products
* Sea surface salinity (SSS): JPL SMAP-SSS V5.0 CAP, 8-day running mean, level 3 mapped product from the NASA Soil Moisture Active Passive (SMAP) observatory
* Sea surface temperature (SST): Group for High Resolution Sea Surface Temperature (GHRSST) Level 4 sea surface temperature

We can use `earthaccess` to find PACE OCI L2 data, checking in both the near-real-time and refined collections.

```{code-cell} ipython3
tspan = ("2026-05-05 17:35", "2026-05-05 17:35")
results = earthaccess.search_data(
    short_name=["PACE_OCI_L2_AOP_NRT", "PACE_OCI_L2_AOP"],
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

You can see that this function accepts a `bbox` parameter for limiting calculations to a bounding box. The default is `bbox=None`, meaning the algorithm is applied to every single pixel in the L2 granule, which can take a significnat amount of time and may exceed available system memory. We will supply the `bbox` parameter with the following coordinates: 38 N, 35 S, -70 E, -67 W.

```{code-cell} ipython3
bbox = (-73.5, 37.5, -67, 40.5)

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

## 3. Run SDP on L2 Data

+++

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

## 4. Open and Plot SDP output

+++

Let's open the new file:

```{code-cell} ipython3
ds = xr.open_dataset(output_file)
ds
```

You can see all the different pigment concentrations derived for our L2 granule. Let's plot them:

```{code-cell} ipython3
fig, axs = plt.subplots(
    nrows=7,
    ncols=2,
    figsize=(10, 12),
    sharex=True,
    sharey=True,
    constrained_layout=False,
)

variables = tuple(ds)
axs = axs.ravel().tolist()
ax = axs.pop(1)
ax.set_visible(False)

for i, ax in enumerate(axs):
    da = ds[variables[i]]
    da.attrs["units"] = "mg m$^{-3}$"
    da.plot(
        x="longitude",
        y="latitude",
        cmap="viridis",
        vmax=da.quantile(0.99),
        ax=ax,
    )
    ax.set_xlim(bbox[0], bbox[2])
    ax.set_ylim(bbox[1], bbox[3])
    ax.set_xlabel("")
    ax.set_ylabel("")

plt.tight_layout()
plt.show()
```

<div class="alert alert-info" role="alert">

You have completed the notebook on the SDP Python algorithm!

</div>
