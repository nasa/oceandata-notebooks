---
jupytext:
  text_representation:
    extension: .md
    format_name: myst
    format_version: 0.13
    jupytext_version: 1.19.4
kernelspec:
  display_name: Python 3 (ipykernel)
  language: python
  name: python3
---

# Applying Gaussian Pigment (GPig) Phytoplankton Community Composition Algorithm to OCI data

**Author(s):** Anna Windle (NASA, SSAI), Ian Carroll (NASA, UMBC) <br>
Adapted from code developed by: Max Danenhower (Bowdoin College), Ali Chase (University of Washington)

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

This notebook applies the inversion algorithm described in [Chase et al., 2017][Chase-et-al] to estimate phytoplankton pigment concentrations from PACE OCI Rrs data. This algorithm, called Gaussian Pigment (GPig), is currently being implemented in OBPG's OCSSW software. This work was originally [developed in MatLab](https://github.com/alisonpchase/Rrs_inversion_pigments) by Ali Chase and subsequently [translated to Python](https://github.com/max-danenhower/pace-rrs-inversions-pigments) by Max Danenhower, Charles Stern, and Ali Chase. This tutorial demonstrates how to apply the Python GPig algorithm to Level-2 (L2) and Level-3 Mapped (L3M) PACE OCI data.

[Chase-et-al]: https://doi.org/10.1002/2017JC012859

## Learning Objectives

At the end of this notebook you will know:

- How to use a packaged Python project
- How to run the GPig Algorithm on PACE OCI L2 and L3 data

+++

## 1. Setup

The GPig Python code has been packaged to allow it to be easily installed, imported, and reused.
While the package is not on PyPI or conda-forge, it can be installed directly from the [source repository][gpig] on GitHub.
If you have followed the setup instructions, then GPig is available to import along with the other packages needed for this notebook.

[gpig]: https://github.com/max-danenhower/pace-rrs-inversions-pigments

```{code-cell} ipython3
:scrolled: true

import cartopy.crs as ccrs
import cartopy.feature as cfeature
import earthaccess
import matplotlib.pyplot as plt
import numpy as np
import xarray as xr
from gpig import L2_utils, L3_utils

crs = ccrs.PlateCarree()
```

Set (and persist to your home directory on the host, if needed) your Earthdata Login credentials.

```{code-cell} ipython3
auth = earthaccess.login()
```

# 2. Access and open data

We need the following data to run GPig:

* Rrs: PACE OCI L2 or L3M AOP data products
* Sea surface salinity: JPL SMAP-SSS V5.0 CAP, 8-day running mean, level 3 mapped, sea surface salinity (SSS) product from the NASA Soil Moisture Active Passive (SMAP) observatory
* Sea surface temperature: Group for High Resolution Sea Surface Temperature (GHRSST) Level 4 sea surface temperature

We can use `earthaccess` to find this data.

```{code-cell} ipython3
tspan = ("2025-05-01 20:13", "2025-05-01 20:13")
bbox = (-127, 40, -126, 41)

results = earthaccess.search_data(
    short_name=["PACE_OCI_L2_AOP", "PACE_OCI_L2_AOP_NRT"],
    temporal=tspan,
    bounding_box=bbox,
    count=1,
)  
l2_paths = earthaccess.open(results)
```

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

Let's take a look at our L2 granule:

```{code-cell} ipython3
datatree = xr.open_datatree(l2_paths[-1])
rrs = datatree["geophysical_data"]["Rrs"]
for variable in ("longitude", "latitude"):
    rrs[variable] = datatree["navigation_data"][variable]
rrs
```

```{code-cell} ipython3
fig, ax = plt.subplots(figsize=(8, 6), subplot_kw={"projection": crs})

data = rrs.sel({"wavelength": 500}, method='nearest')
data.plot(
    x="longitude",
    y="latitude",
    vmin=0,
    vmax=0.008,
    ax=ax,
    cbar_kwargs={"label": "Rrs ($sr^{-1}$)"},
)

ax.set_extent([-135, -115, 35, 55], crs=crs)
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

## 2. Run GPig on L2 Data

+++

Now, we can use `L2_utils.estimate_inv_pigments` to calculate phytoplankton pigment concentrations for this data. Let's take a look at the docstring for this function:

```{code-cell} ipython3
?L2_utils.estimate_inv_pigments
```

You can see that this function accepts a bounding box (bbox) as a parameter. The default is `None` which means it will run the algorithm on every single pixel in the L2 file, which can take a long time. We will supply the `bbox` parameter with the following coordinates:
48 N, 47 S, -125 E, -126 W.

Let's first see what this bounding box covers:

```{code-cell} ipython3
bbox = (-126, 47, -125, 48)

lon_min, lat_min, lon_max, lat_max = bbox
rect_lon = [lon_min, lon_max, lon_max, lon_min, lon_min]
rect_lat = [lat_min, lat_min, lat_max, lat_max, lat_min]
ax.plot(rect_lon, rect_lat, color="red", linewidth=2)

fig
```

Let's run it. This can take some time depending on bounding box size.

```{code-cell} ipython3
:scrolled: true
:tags: [scroll-output]

l2_pigments = L2_utils.estimate_inv_pigments(l2_paths[-1], sss_paths[-1], sst_paths[-1], bbox)
```

The inversion provides four phytoplankton pigment concenrations. Let's plot them:

```{code-cell} ipython3
fig, axs = plt.subplots(2, 2, figsize=(10, 8), subplot_kw={"projection": crs})

variables = ["chla", "chlb", "chlc", "ppc"]
titles = ["Chlorophyll-a", "Chlorophyll-b", "Chlorophyll-c", "PPC"]
for ax, var, title in zip(axs.flat, variables, titles):
    data = l2_pigments[var]
    lon = l2_pigments["longitude"]
    lat = l2_pigments["latitude"]

    data_log = np.log10(data.where(data > 0))

    im = ax.pcolormesh(lon, lat, data_log, cmap="viridis", shading="auto")

    ax.gridlines(
        draw_labels=["left", "bottom"],
        linewidth=0.5,
        color="gray",
        alpha=0.5,
        linestyle="--",
    )
    ax.set_title(title)
    ax.set_xlim(bbox[0], bbox[2])
    ax.set_ylim(bbox[1], bbox[3])

    cbar = fig.colorbar(im, ax=ax, orientation="vertical")
    cbar.set_label(r"$\log_{10}(\mathrm{mg\ m^{-3}})$")

plt.tight_layout()
plt.show()
```

## 3. Run GPig on L3M Data

+++

We can also run GPig on L3M data. Let's open a PACE OCI L3m (4km), SSS and SST data for June 12, 2024:

```{code-cell} ipython3
tspan = ("2024-06-12", "2024-06-12")

results = earthaccess.search_data(
    short_name=["PACE_OCI_L3M_AOP", "PACE_OCI_L3M_AOP_NRT"],
    temporal=tspan,
    granule_name="*DAY*4km*",
    count=1)

l3m_paths = earthaccess.open(results)
```

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

Let's quickly look at L3M Rrs at 500 nm:

```{code-cell} ipython3
l3_dataset = xr.open_dataset(l3m_paths[-1])
l3_dataset
```

```{code-cell} ipython3
fig, ax = plt.subplots(figsize=(10, 6), subplot_kw={"projection": crs})

data = l3_dataset["Rrs"].sel({"wavelength": 500}, method='nearest')
data.plot.imshow(
    x="lon",
    y="lat",
    vmin=0,
    vmax=0.008,
    ax=ax,
    cbar_kwargs={"label": r"Rrs ($sr^{-1}$)", "fraction": 0.046},
)

ax.coastlines(resolution="10m")
ax.gridlines(
    draw_labels=["left", "bottom"],
    linewidth=0.5,
    color="gray",
    alpha=0.5,
    linestyle="--",
)

plt.show()
```

Let's look at what `L3_utils.estimate_inv_pigments` requires as input:

```{code-cell} ipython3
?L3_utils.estimate_inv_pigments
```

We'll provide the Rrs, SSS, and SST file and input a bounding box corresponding to the coast of Washington, U.S.

Let's take a look at what data this bounding box covers:

```{code-cell} ipython3
bbox = (-127, 40, -126, 41)

lon_min, lat_min, lon_max, lat_max = bbox
rect_lon = [lon_min, lon_max, lon_max, lon_min, lon_min]
rect_lat = [lat_min, lat_min, lat_max, lat_max, lat_min]
ax.plot(rect_lon, rect_lat, color="red", linewidth=2)

ax.set_extent([-130, -115, 32, 50], crs=crs)

fig
```

```{code-cell} ipython3
:scrolled: true
:tags: [scroll-output]

l3_pigments = L3_utils.estimate_inv_pigments(l3m_paths, sss_paths, sst_paths, bbox)
l3_pigments
```

The inversion provides four phytoplankton pigment concentrations. Let's plot them:

```{code-cell} ipython3
fig, axs = plt.subplots(2, 2, figsize=(10, 8), subplot_kw={"projection": crs})

variables = ["chla", "chlb", "chlc", "ppc"]
titles = ["Chlorophyll-a", "Chlorophyll-b", "Chlorophyll-c", "PPC"]
for ax, var, title in zip(axs.flat, variables, titles):

    data = l3_pigments[var]
    data_log = np.log10(data.where(data > 0))

    im = data_log.plot.imshow(
        ax=ax,
        cmap="viridis",
        add_colorbar=False,
    )

    ax.coastlines(resolution="10m")
    ax.set_title(title)
    ax.gridlines(
        draw_labels=["left", "bottom"],
        linewidth=0.5,
        color="gray",
        alpha=0.5,
        linestyle="--",
    )

    fig.colorbar(im, ax=ax, orientation="vertical", label=f"$log_{{10}}({var})$")

plt.tight_layout()
plt.show()
```

<div class="alert alert-info" role="alert">

You have completed the notebook on the GPig Python algorithm!

</div>
