---
jupytext:
  text_representation:
    extension: .md
    format_name: myst
    format_version: 0.13
    jupytext_version: 1.18.1
kernelspec:
  display_name: Python 3 (ipykernel)
  language: python
  name: python3
---

# Applying Gaussian Pigment (GPig) Phytoplankton Community Composition Algorithm to OCI data

**Author(s):** Anna Windle (NASA, SSAI), Max Danenhower (Bowdoin College), Ali Chase (University of Washington)

Last updated: August 20, 2025

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
auth = earthaccess.login(persist=True)
```

## 2. Run GPig on L2 Data

+++

Let's first download the data using the `L2_utils.load()` function. Let's take a look at the docstring:

```{code-cell} ipython3
?L2_utils.load_data
```

Running `L2_utils.load_data()` downloads several data files from NASA EarthData:

* Rrs: PACE OCI Level-2 AOP data products
* Sea surface salinity: JPL SMAP-SSS V5.0 CAP, 8-day running mean, level 3 mapped, sea surface salinity (SSS) product from the NASA Soil Moisture Active Passive (SMAP) observatory
* Sea surface temperature: Group for High Resolution Sea Surface Temperature (GHRSST) Level 4 sea surface temperature

Let's run `L2_utils.load_data()` to download data collected on May 5, 2025 corresponding to a bounding box off the coast of Washington, U.S.

```{code-cell} ipython3
rrs, sss, sst = L2_utils.load_data(("2025-05-01", "2025-05-01"), (-127, 40, -126, 41))
datatree = xr.open_datatree(rrs[0])
dataset = xr.merge(datatree.to_dict().values())
l2_dataset = dataset.set_coords(("longitude", "latitude"))
```

You should see 3 new folders in your working directory called `L2_rrs_data`, `sal_data`, and `temp_data`. Let's take a quick look at Rrs at 500 nm:

```{code-cell} ipython3
fig, ax = plt.subplots(figsize=(8, 6), subplot_kw={"projection": crs})

data = l2_dataset["Rrs"].sel({"wavelength_3d": 500})
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

Now, we can use `L2_utils.estimate_inv_pigments` to calculate phytoplankton pigment concentrations for this data. Let's take a look at the docstring for this function:

```{code-cell} ipython3
?L2_utils.estimate_inv_pigments
```

You can see that this function accepts a bounding box (bbox) as a parameter. The default is `None` which means it will run the algorithm on every single pixel in the L2 file, which can take a long time. We will supply the `bbox` parameter with the following coordinates:
45 N, 44 S, -125 E, -126 W.

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

l2_pigments = L2_utils.estimate_inv_pigments(rrs[0], sss, sst, bbox)
```

The inversion provides four pigment variables.

```{code-cell} ipython3
l2_pigments
```

Let's plot the phytoplankton pigment concentrations:

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
    cbar.set_label(f"$log_{{10}}({var})$")

plt.tight_layout()
plt.show()
```

## 3. Run GPig on L3M Data

+++

We can also run GPig on L3M data. Let's look at the `L3_utils.load_data()` docstring:

```{code-cell} ipython3
?L3_utils.load_data
```

We'll use this to download 4km L3M Rrs data, global SSS, and global SST data for June 12, 2024:

```{code-cell} ipython3
rrs, sss, sst = L3_utils.load_data(("2024-06-12", "2024-06-12"), "4km")
l3_dataset = xr.open_dataset(rrs[0])
```

Let's quickly look at L3M Rrs at 500 nm:

```{code-cell} ipython3
fig, ax = plt.subplots(figsize=(10, 6), subplot_kw={"projection": crs})

data = l3_dataset["Rrs"].sel({"wavelength": 500})
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

l3_pigments = L3_utils.estimate_inv_pigments(rrs, sss, sst, bbox)
```

The inversion provides four pigment variables.

```{code-cell} ipython3
l3_pigments
```

Let's plot all phytoplankton pigment concentrations:

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
