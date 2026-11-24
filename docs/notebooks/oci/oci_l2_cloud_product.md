---
jupytext:
  text_representation:
    extension: .md
    format_name: myst
    format_version: 0.13
kernelspec:
  display_name: Python 3 (ipykernel)
  language: python
  name: python3
---

# Visualize the PACE-OCI Level-2 CLOUD Products

**Author(s):** Chamara Rajapakshe (NASA, SSAI), Andy Sayer (NASA, UMBC), Kirk Knobelspiesse (NASA), Meng Gao (NASA, SSAI), Sean Foley (NASA, MSU)

Last updated: November 24, 2026

<div class="alert alert-info" role="alert">

An [Earthdata Login][edl] account is required to access data from the NASA Earthdata system, including NASA ocean color data.

</div>

[edl]: https://urs.earthdata.nasa.gov/

## Summary

This notebook summarizes how to access PACE-OCI cloud optical properties (CLOUD) in Level-2 (L2) granules. The CLOUD suite provides cloud optical and microphysical retrievals derived from multi-spectral observations. 

**Note:** This tutorial uses an early, preliminary version of the product. Product contents, variable definitions, and processing algorithms may be updated or optimized in future releases.

## Learning Objectives

By the end of this notebook, you will understand:

- How to acquire PACE-OCI L2 CLOUD data
- Identify and describe the variables available in the product
- Visualize and explore key variables

+++

## 1. Setup

+++

Begin by importing all of the packages used in this notebook. If you followed the guidance on the [Getting Started](https://nasa.github.io/oceandata-notebooks/getting-started.html) page, then the imports will be successful.

```{code-cell} ipython3
import re

import cartopy.crs as ccrs
import earthaccess
import matplotlib.colors as mcolors
import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
import xarray as xr
```

Global settings and variables used throughout the notebook.

```{code-cell} ipython3
pd.options.display.max_colwidth = None
projection = ccrs.PlateCarree()
```

Define your area and time of interest. Note that the bounding box is supplied as longitudes and latitudes in the order west, south, east, then north.

```{code-cell} ipython3
bbox = (-90, -13, -89, -12)
tspan = ("2025-07-02", "2025-07-02")
```

Set your Earthdata Login credentials. You can add `persist=True` to save your credentials in a .netrc file, allowing you to authenticate automatically in the future sessions without re-entering your Earthdata credentials.

```{code-cell} ipython3
auth = earthaccess.login()
```

We'll define functions for some repeatable tasks performed in the tutorial.

```{code-cell} ipython3
def print_variable_description(datatree, variables, exclude=False):
    """
    Print a table of variables, units, and descriptions from the
    `geophysical_data` group of a DataTree-like object.

    Parameters
    ----------
    datatree : DataTree or dict-like
        Object containing a `geophysical_data` group with variables
        whose metadata are stored in `attrs` (e.g., `units` and `long_name`).
    variables: list of str
        Substrings used to filter variable names.
    exclude : bool, default False
        If False (default), only variables whose names contain any of the
        substrings in `ret_type_list` are shown. If True, show all others.

    Notes
    -----
    Long descriptions are wrapped to 100 characters; only the first line
    prints the variable name and units.
    """
    df = pd.DataFrame(columns=("Units", "Description"))
    for key, value in datatree["geophysical_data"].data_vars.items():
        # select based on inclusion (or exclusion) logic
        match = any(i in key for i in variables)
        if (match and not exclude) or (not match and exclude):
            units = value.attrs.get("units", "")
            desc = value.attrs.get("long_name", "")
            df.loc[key, :] = [units, desc]
    return df
```

```{code-cell} ipython3
def extremes_removed_limits(array):
    """
    Return suggested min and max axis limits based on the interquartile range (IQR) rule.

    Parameters
    ----------
    array : array-like
        Input numeric array.

    Returns
    -------
    tuple
        Suggested min and max for axis limits in plots
    """
    q0, q1, q3, q4 = array.quantile([0, 0.25, 0.75, 1])
    vmin = q1 - 1.5 * (q3 - q1)
    vmax = q3 + 1.5 * (q3 - q1)
    return max(q0, vmin), min(q4, vmax)
```

```{code-cell} ipython3
def geo_axis_tags(ax, crs=None):
    """
    Add coastlines and labeled latitude/longitude gridlines to a Cartopy axis.

    Parameters
    ----------
    ax : cartopy.mpl.geoaxes.GeoAxes
        Axes object on which to draw the gridlines and coastlines.
    crs : cartopy.crs.CRS, optional
        Coordinate reference system used for the gridlines.
        Default is a Plate Carrée projection with central longitude = 0.
    """
    if crs is None:
        crs = ccrs.PlateCarree()
    gl = ax.gridlines(
        crs=crs,
        draw_labels=["left", "bottom"],
        xlabel_style={"size": 12, "color": "k"},
        ylabel_style={"size": 12, "color": "k"},
    )
    ax.coastlines()
    return
```

```{code-cell} ipython3
def plot_cloud_phase(dataset, name, ax):
    """Plot a map of cloud phase, a categorical variable, on a cartopy GeoAxes

    Parameters
    ----------
    dataset: xarray.Dataset
        The granule with cloud phase variables
    name: str
        The name of a variable with categorical values
    ax : cartopy.mpl.geoaxes.GeoAxes
        Axes object on which to draw the gridlines and coastlines.
    """
    array = dataset[name]
    try:
        flag_values = array.attrs["flag_values"]
        flag_meanings = array.attrs["flag_meanings"].split(" ")
    except KeyError:
        description = array.attrs["long_name"]
        long_name, flags = description.split(": ")
        flag_pairs = re.findall(r"([0-9]) - ([^,]+)", flags)
        flag_values = np.array([int(a) for a, b in flag_pairs], dtype=array.dtype)
        flag_meanings = [b.replace(" ", "_") for a, b in flag_pairs]
    cmap = plt.get_cmap("tab20", flag_values.size)
    cmap.set_bad("grey")
    ctf = array.plot.pcolormesh(
        x="longitude",
        y="latitude",
        cmap=cmap,
        vmin=flag_values.min() - 0.5,
        vmax=flag_values.max() + 0.5,
        add_colorbar=False,
    )
    cbar = ax.figure.colorbar(ctf, ax=ax, orientation="vertical")
    cbar.set_ticks(flag_values)
    cbar.set_ticklabels(flag_meanings)
    ax.gridlines(draw_labels=["left", "bottom"])
    ax.coastlines()
    ax.set_title(name)
```

## 2. Access L2 CLOUD Data

+++

First, let's search for "CLOUD" in the short-names of OCI data.

```{code-cell} ipython3
results = earthaccess.search_datasets(instrument="oci")

for item in results:
    short_name = item.summary["short-name"]
    if "CLOUD" in short_name:
        print(short_name)
```

You can use the short-name `PACE_OCI_L2_CLOUD` to get the most recent version available. Add the Near Real Time (NRT) suffix for the most recent observations (i.e., PACE_OCI_L2_CLOUD_NRT).

We can also search for available granules within a time range and geospatial area of interest. The `sort_key` parameter can help when multiple versions are available; the `-revision_date` key will show the most recent versions first.

```{code-cell} ipython3
results = earthaccess.search_data(
    short_name="PACE_OCI_L2_CLOUD",
    temporal=tspan,
    bounding_box=bbox,
    sort_key="-revision_date",
)
for item in results:
    display(item)
```

```{code-cell} ipython3
paths = earthaccess.open(results)
```

Let's merge all the data groups together for convenience in data manipulations.

```{code-cell} ipython3
datatree = xr.open_datatree(paths[0])
dataset = xr.merge(datatree.to_dict().values())
dataset = dataset.set_coords(("latitude", "longitude"))
dataset
```

## 3. Understanding PACE-OCI L2 CLOUD Variables

+++

PACE-OCI CLOUD products provide various cloud optical and microphysical properties. The product structure includes multiple variables with descriptive metadata. Given the early stage of the product, improvements and changes are expected in future versions.

We'll use our own `print_variable_description` function to inspect the dataset.

```{code-cell} ipython3
help(print_variable_description)
```

### Cloud Optical Properties

+++

Cloud optical thickness (cot) and cloud effective radius (cer) are fundamental properties retrieved from multispectral observations.

```{code-cell} ipython3
print_variable_description(datatree, ["cot", "cer"])
```

### Cloud Phase and Other Properties

+++

Additional variables include cloud phase information and other cloud properties.

```{code-cell} ipython3
print_variable_description(datatree, ["cld_phase", "cloud"])
```

## 4. Visualizing Variables

+++

To visualize the L2 variables, we plot them on `cartopy` GeoAxes dressed up with our `geo_axis_tags` function with the color range limited by our `extremes_removed_limits` function.

```{code-cell} ipython3
help(geo_axis_tags)
```

```{code-cell} ipython3
help(extremes_removed_limits)
```

### Cloud Effective Radius

+++

Let's visualize the cloud effective radius `cer_21`. The colorbar limits are adjusted based on the range of observed effective radii, excluding extreme values.

```{code-cell} ipython3
fig, ax = plt.subplots(figsize=(10, 6), subplot_kw={"projection": projection})
var = "cer_21"
array = dataset[var]
vmin, vmax = extremes_removed_limits(array)
cmap = plt.get_cmap("viridis", 20)
img = array.plot.pcolormesh(
    x="longitude",
    y="latitude",
    cmap=cmap,
    vmin=vmin,
    vmax=vmax,
)
img.colorbar.set_label(array.attrs.get("units", ""))
ax.set_title(var, size=12)
geo_axis_tags(ax, projection)
plt.show()
```

### Cloud Optical Thickness

+++

Cloud optical thickness (`cot_22`) provides information about the opacity of clouds to solar radiation.

```{code-cell} ipython3
fig, ax = plt.subplots(figsize=(10, 6), subplot_kw={"projection": projection})
var = "cot_22"
array = dataset[var]
vmin, vmax = extremes_removed_limits(array)
cmap = plt.get_cmap("viridis", 20)
img = array.plot.pcolormesh(
    x="longitude",
    y="latitude",
    cmap=cmap,
    vmin=vmin,
    vmax=vmax,
)
img.colorbar.set_label(array.attrs.get("units", ""))
ax.set_title(var, size=12)
geo_axis_tags(ax, projection)
plt.show()
```

### Cloud Phase

+++

Cloud phase classification distinguishes between liquid and ice clouds. These variables are discrete, also known as categorical, which we visualize with our `plot_cloud_phase` function.

```{code-cell} ipython3
help(plot_cloud_phase)
```

```{code-cell} ipython3
fig, ax = plt.subplots(figsize=(10, 6), subplot_kw={"projection": projection})
plot_cloud_phase(dataset, "cld_phase_21", ax)
plt.show()
```

<div class="alert alert-info" role="alert">

You have completed the notebook on OCI cloud products. May we suggest reviewing the notebook on [HARP2 cloud products]?

[HARP2 cloud products]: https://nasa.github.io/oceandata-notebooks/notebooks/harp2/harp2_l2_cloud_gpc_product.html

</div>
