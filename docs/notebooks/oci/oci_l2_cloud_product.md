---
jupytext:
  text_representation:
    extension: .md
    format_name: myst
    format_version: 0.13
    jupytext_version: 1.19.5
kernelspec:
  display_name: Python 3 (ipykernel)
  language: python
  name: python3
---

# Visualize OCI CLOUD L2 Product

**Author(s):** Chamara Rajapakshe (NASA, SSAI), Andy Sayer (NASA, UMBC), Kirk Knobelspiesse (NASA), Meng Gao (NASA, SSAI), Sean Foley (NASA, MSU)

Last updated: Sep 16, 2026

## Summary

This notebook summarizes how to access OCI CLOUD products (CLOUD) in Level-2 (L2) granules. The CLOUD product provides cloud optical and microphysical retrievals derived from multi-spectral observations. Note that this notebook is based on an early preliminary version of the product and is therefore subject to future optimizations and changes.

## Learning Objectives

By the end of this notebook, you will understand:

- How to acquire OCI Level-2 CLOUD data
- Available variables in the product
- How to visualize variables

+++

## 1. Setup

+++

Begin by importing all of the packages used in this notebook. If you followed the guidance on the [Getting Started](/getting-started) page, then the imports will be successful.

```{code-cell} ipython3
import re

import cartopy.crs as ccrs
import earthaccess
import matplotlib.colors as mcolors
import matplotlib.pyplot as plt
import numpy as np
import xarray as xr
```

Global settings and variables used throughout the notebook.

```{code-cell} ipython3
plt.style.use("seaborn-v0_8-notebook")
plt.rcParams.update(
    {
        "xtick.labelsize": 12,
        "ytick.labelsize": 12,
    }
)
projection = ccrs.PlateCarree()
```

Define your area and time of interest. Note that the bounding box is supplied as longitudes and latitudes in the order west, south, east, then north.

```{code-cell} ipython3
bbox = (-90, -13, -89, -12)
tspan = ("2025-07-02", "2025-07-02")
```

Set (and optionally `persist` to your home directory as a "netrc" file) your Earthdata Login credentials.

```{code-cell} ipython3
auth = earthaccess.login()
```

## 2. Get Level-2 Data

+++

You can use the short name PACE_OCI_L2_CLOUD to get the most recent version available for the CLOUD product at Level-2 for the OCI instrument. Add the Near Real Time (NRT) suffix for the most recent observations (i.e. PACE_OCI_L2_CLOUD_NRT).

```{code-cell} ipython3
results = earthaccess.search_datasets(
    keyword="clouds",
    instrument="oci",
    processing_level_id="2",
)
```

Print the product short names and titles:

```{code-cell} ipython3
for item in results:
    summary = item.summary()
    title = item["umm"]["EntryTitle"][26:]
    print(f'{summary["short-name"]}: {title}')
```

Search for available granules within a time range and geospatial area of interest. The `sort_key` parameter can help when multiple versions are available; the `-revision_date` key will show the most recent versions first.

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

Here we merge all the data groups together for convenience in data manipulations.

```{code-cell} ipython3
datatree = xr.open_datatree(paths[0])
dataset = xr.merge(datatree.to_dict().values())
dataset = dataset.set_coords(("latitude", "longitude"))
```

## 3. Understanding OCI L2.CLOUD Product Structure

OCI CLOUD products provide various cloud optical and microphysical properties. The product structure includes multiple variables with descriptive metadata. Given the early stage of the product, improvements and changes are expected in future versions.

```{code-cell} ipython3
def print_variable_description(dataset, variables_pattern=None):
    """
    Print a table of variables, units, and descriptions from a dataset.

    Parameters
    ----------
    dataset : xarray.Dataset
        Dataset containing variables whose metadata are stored in `attrs`
        (e.g., `units` and `long_name`).
    variables_pattern : str, optional
        Pattern to filter variable names. If None, all variables are shown.

    Notes
    -----
    Long descriptions are wrapped to 100 characters; only the first line
    prints the variable name and units.
    """
    import pandas as pd

    df = pd.DataFrame(columns=("Units", "Description"))
    for key, value in dataset.data_vars.items():
        if variables_pattern is None or variables_pattern in key:
            units = value.attrs.get("units", "")
            desc = value.attrs.get("long_name", "")
            df.loc[key, :] = [units, desc]
    return df
```

### Cloud Optical Properties

Cloud optical thickness and effective radius are fundamental properties retrieved from multi-spectral observations.

```{code-cell} ipython3
print_variable_description(dataset, variables_pattern="cer")
print_variable_description(dataset, variables_pattern="cot")
```

### Cloud Phase and Other Properties

Additional variables include cloud phase information and other cloud properties.

```{code-cell} ipython3
print_variable_description(dataset)
```

## 4. Visualizing Variables

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


def geo_axis_tags(ax, crs=ccrs.PlateCarree()):
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
    gl = ax.gridlines(
        crs=crs,
        draw_labels=["left", "bottom"],
        xlabel_style={"size": 12, "color": "k"},
        ylabel_style={"size": 12, "color": "k"},
    )
    ax.coastlines()
    return
```

### Cloud Effective Radius

Visualize the cloud effective radius retrieved from OCI observations. The colorbar limits are adjusted based on the range of observed effective radii, excluding extreme values.

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

Cloud optical thickness provides information about the opacity of clouds to solar radiation.

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

Cloud phase classification distinguishes between liquid and ice clouds.

```{code-cell} ipython3
def plot_cloud_flag(dataset, name, fig, ax):
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
    )
    cbar = fig.colorbar(ctf, ax=ax, orientation="vertical")
    cbar.set_ticks(flag_values)
    cbar.set_ticklabels(flag_meanings)
    ax.gridlines(draw_labels=["left", "bottom"])
    ax.coastlines()
    ax.set_title(name)
```

```{code-cell} ipython3
fig, ax = plt.subplots(figsize=(10, 6), subplot_kw={"projection": projection})
plot_cloud_flag(dataset, "cld_phase_21", fig, ax)
plt.show()
```

## 5. Reference

+++

- Platnick, S., Meyer, K., King, M. D., Wind, G., Amarasinghe, N., Marchant, B., Arnold, G. T., Zhang, Z., Hubanks, P. A., Ridgway, B., & Riedi, J. (2017). The MODIS Cloud Optical and Microphysical Products: Collection 6 Updates and Examples From Terra and Aqua. IEEE Transactions on Geoscience and Remote Sensing, 55(1), 502–525. https://doi.org/10.1109/TGRS.2016.2610522
- Sayer, A. M., Cairns, B., Knobelspiesse, K. D., Lelli, L., Rajapakshe, C., Giangrande, S. E., Thomas, G. E., and Zhang, D.: Evaluation of cloud height, optical thickness, and phase retrievals from the CHROMA algorithm applied to Sentinel-3 OLCI data, Atmos. Meas. Tech., 18, 6681–6703, https://doi.org/10.5194/amt-18-6681-2025, 2025.

<div class="alert alert-info" role="alert">

You have completed the notebook on OCI cloud products. May we suggest studying the notebook on [HARP2 cloud products]?

[HARP2 cloud products]: https://nasa.github.io/oceandata-notebooks/notebooks/harp2/harp2_l2_cloud_gpc_product.html

</div>

```{code-cell} ipython3

```
