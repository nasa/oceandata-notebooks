---
kernelspec:
  display_name: Python 3 (ipykernel)
  language: python
  name: python3
---

# OCI CLOUD Products

**Authors:** Chamara Rajapakshe (NASA, SSAI), Andy Sayer (NASA, UMBC), Kirk Knobelspiesse (NASA), Meng Gao (NASA, SSAI), Sean Foley (NASA, MSU)

<div class="alert alert-info" role="alert">

An [Earthdata Login][edl] account is required to access data from the NASA Earthdata system, including NASA ocean color data.

</div>

[edl]: https://urs.earthdata.nasa.gov/

## Summary

This notebook summarizes how to access OCI cloud products (CLDMASK and CLOUD) in Level-2 (L2) granules and visualize the variables they contain.
Note that this notebook is based on an early, preliminary version of the product and is therefore subject to future optimizations and changes.

## Learning Objectives

By the end of this notebook, you will understand:

- How to acquire OCI CLDMASK and CLOUD L2 data
- Key variables in these products
- How to visualize those variables

## Contents

1. [Setup](#1.-Setup)
2. [Get Level-2 Data](#2.-Get-Level-2-Data)
3. [Visualizing L2 CLDMASK Variables](#3.-Visualizing-L2-CLDMASK-Variables)
4. [Visualizing L2 CLOUD Variables](#4.-Visualizing-L2-CLOUD-Variables)

+++

## 1. Setup

Begin by importing all of the packages used in this notebook. If your kernel uses an environment defined following the guidance on the [tutorials] page, then the imports will be successful.

[tutorials]: https://oceancolor.gsfc.nasa.gov/resources/docs/tutorials/

```{code-cell} ipython3
import re

import cartopy.crs as ccrs
import earthaccess
import matplotlib.colors as mcolors
import matplotlib.pyplot as plt
import numpy as np
import xarray as xr
```

Configure matplotlib for all plots below.

```{code-cell} ipython3
plt.rcParams.update({
    "xtick.labelsize": 12,
    "ytick.labelsize": 12,
})
plt.style.use("seaborn-v0_8-notebook")
projection = ccrs.PlateCarree()
transform = ccrs.PlateCarree(central_longitude=0) # why have a transform?
```

Define our area and time of interest.
Note that the bounding box is supplied as latitudes or longitudes in the order west, south, east, then north.
Also note that the timespan is rounded down for the start and rounded up for the end.

```{code-cell} ipython3
bbox = (-90, -13, -89, -12)
tspan = ("2025-07-02", "2025-07-02")
```

Set (and persist to your home directory as a "netrc" file) or check your Earthdata Login credentials.

```{code-cell} ipython3
auth = earthaccess.login(persist=True)
```

[back to top](#Contents)

+++

## 2. Get Level-2 Data

You can find the appropriate product "short name" for CLOUD_MASK and CLOUD products as follows.
Note that you don't need to do this search if you already know the `short_name` you are interested in.

```{code-cell} ipython3
:scrolled: true

results = earthaccess.search_datasets(
    keyword="clouds", instrument="oci", processing_level_id="2",
)
```

The keyword "clouds" is easy to guess, but you can always print the full title, as below, even when you don't use a keyword.

```{code-cell} ipython3
for item in results:
    summary = item.summary()
    title = item["umm"]["EntryTitle"][26:]
    print(f'{summary["short-name"]}: {title}')
```

Your may want to look for data in both the refined and near real-time (NRT) collections.
If your temporal constraint is very recent, the refined product may not be available,
so your search will fall back on the NRT product.
The `sort_key` can help when multiple versions are available; the `-revision_date` key
will show the most recent versions first.

```{code-cell} ipython3
results = earthaccess.search_data(
    short_name=["PACE_OCI_L2_CLOUD_MASK", "PACE_OCI_L2_CLOUD_MASK_NRT"],
    temporal=tspan,
    bounding_box=bbox,
    sort_key="-revision_date",
)
for item in results:
    display(item)
```

```{code-cell} ipython3
paths = earthaccess.open(results[:1])
```

Here we merge all the data group together for convenience in data manipulations.

```{code-cell} ipython3
datatree = xr.open_datatree(paths[0])
cldmask = xr.merge(datatree.to_dict().values())
cldmask = cldmask.set_coords(("latitude", "longitude"))
cldmask
```

```{code-cell} ipython3
results = earthaccess.search_data(
    short_name=["PACE_OCI_L2_CLOUD", "PACE_OCI_L2_CLOUD_NRT"],
    temporal=tspan,
    bounding_box=bbox,
    sort_key="-revision_date",
)
for item in results:
    display(item)
```

```{code-cell} ipython3
paths = earthaccess.open(results[:1])
```

```{code-cell} ipython3
datatree = xr.open_datatree(paths[0])
cloud = xr.merge(datatree.to_dict().values())
cloud = cloud.set_coords(("latitude", "longitude"))
cloud
```

[back to top](#Contents)

+++

## 3. Visualizing L2 CLDMASK Variables

The product includes two cloud flags. The first, cloud_flag, classifies each pixel as either cloudy or clear. The second, cloud_flag_dilated, provides a more conservative classification: it labels pixels as either cloud-free and not adjacent to cloudy pixels, or as cloudy or adjacent to cloudy pixels.

```{code-cell} ipython3
def plot_cloud_flag(dataset, name, fig, ax, transform):
    """
    To plot projected maps of cloud_flag
    parameters:
        dataset: xarray.core.dataset.Dataset
        cloud_flag_option: 'cloud_flag' or 'cloud_flag_dilated'
        fig,ax : fig,ax = plt.subplots(figsize=(8,6), subplot_kw={'projection':projection=ccrs.PlateCarree(central_longitude=0)})
        transform : ccrs.PlateCarree(central_longitude=0)
    """
    array = dataset[name]
    flag_values = array.attrs["flag_values"]
    flag_meanings = array.attrs["flag_meanings"].split(", ")
    cmap = plt.get_cmap("tab20", flag_values.size)
    cmap.set_bad("grey")
    ctf = array.plot.pcolormesh(
        x="longitude",
        y="latitude",
        cmap=cmap,
        vmin=flag_values.min() - 0.5,
        vmax=flag_values.max() + 0.5,
        add_colorbar=False,
        transform=transform,
    )
    cbar = fig.colorbar(ctf, ax=ax, orientation="vertical")
    cbar.set_ticks(flag_values)
    cbar.set_ticklabels(flag_meanings)
    ax.gridlines(crs=transform, draw_labels=["left", "bottom"])
    ax.coastlines()
    ax.set_title(name)
```

```{code-cell} ipython3
fig, ax = plt.subplots(figsize=(10, 6), subplot_kw={"projection": projection})
plot_cloud_flag(cldmask, "cloud_flag", fig, ax, transform)
plt.show()
```

```{code-cell} ipython3
fig, ax = plt.subplots(figsize=(10, 6), subplot_kw={"projection": projection})
plot_cloud_flag(cldmask, "cloud_flag_dilated", fig, ax, transform)
plt.show()
```

[back to top](#Contents)

+++

## 4. Visualizing L2 CLOUD Variables

```{code-cell} ipython3
def vlims(array):
    """
    """
    q0, q1, q3, q4 = array.quantile([0, 0.25, 0.75, 1])
    vmin = q1 - 1.5 * (q3 - q1)
    vmax = q3 + 1.5 * (q3 - q1)
    return max(q0, vmin), min(q4, vmax)

def plot_cloud(dataset, name, fig, ax, transform):
    array = dataset[name]
    vmin, vmax = vlims(array)
    array.plot.pcolormesh(
        x="longitude",
        y="latitude",
        ax=ax,
        cmap="viridis",
        vmin=vmin,
        vmax=vmax,
        transform=transform,
    )
    ax.gridlines(crs=transform, draw_labels=["left", "bottom"])
    ax.coastlines()
    ax.set_title(name)
```

```{code-cell} ipython3
fig, ax = plt.subplots(figsize=(10, 6), subplot_kw={"projection": projection})
plot_cloud(cloud, "cer_21", fig, ax, transform)
plt.show()
```

```{code-cell} ipython3
fig, ax = plt.subplots(figsize=(10, 6), subplot_kw={"projection": projection})
plot_cloud(cloud, "cot_22", fig, ax, transform)
plt.show()
```

The "cld_phase_21" variable is currently (as of version 3.1) missing the conventional attributes for enum type variables.
The following cell, which extracts that missing attribute information from the `long_name` attribute, wouldn't typically be needed!

```{code-cell} ipython3
array = cloud["cld_phase_21"]
description = array.attrs["long_name"]
long_name, flags = description.split(": ")
flag_pairs = re.findall(r"([0-9]) - ([^,]+)", flags)
flag_values = np.array([int(a) for a, b in flag_pairs], dtype=array.encoding["dtype"])
flag_meanings = ", ".join((b.replace(" ", "_") for a, b in flag_pairs))
array.attrs["long_name"] = long_name
array.attrs["flag_values"] = flag_values
array.attrs["flag_meanings"] = flag_meanings
```

With that patched up, we can visualize the cloud phase using the previously defined function.

```{code-cell} ipython3
fig, ax = plt.subplots(figsize=(10, 6), subplot_kw={"projection": projection})
plot_cloud_flag(cloud, "cld_phase_21", fig, ax, transform)
plt.show()
```

[back to top](#Contents)
