---
jupytext:
  formats: ipynb,md:myst
  text_representation:
    extension: .md
    format_name: myst
    format_version: 0.13
    jupytext_version: 1.17.2
kernelspec:
  display_name: Python 3 (ipykernel)
  language: python
  name: python3
---

# Visualize HARP2 CLOUD GPC Product

**Author(s):** Chamara (NASA, SSAI), Kirk (NASA), Andy (NASA, UMBC), Meng (NASA, SSAI), Sean (NASA, MSU)

Last updated: August 3, 2025

## Summary

This notebook summarizes how to access HARP2 GISS Polarimetric Cloud (GPC) products (CLOUD_GPC).
Note that this notebook is based on an early preliminary version of the product and is therefore subject to future optimizations and changes.

## Learning Objectives

By the end of this notebook, you will understand:

- How to acquire HARP2 L2 data
- Available variables in the product
- How to visualize variables

+++

## 1. Setup

Begin by importing all of the packages used in this notebook. If your kernel uses an environment defined following the guidance on the [tutorials] page, then the imports will be successful.

[tutorials]: https://oceancolor.gsfc.nasa.gov/resources/docs/tutorials/

```{code-cell} ipython3
from pathlib import Path
from textwrap import wrap
from fnmatch import fnmatch
import cartopy.crs as ccrs
import earthaccess
import matplotlib.colors as mcolors
import matplotlib.pyplot as plt
import numpy as np
import requests
import xarray as xr

plt.style.use("seaborn-v0_8-notebook")
```

```{code-cell} ipython3
auth = earthaccess.login(persist=True)
fs = earthaccess.get_fsspec_https_session()
```

## 2. Get Level-2 Data

You can use "PACE_HARP2_L2_CLOUD_GPC" (or PACE_HARP2_L2_CLOUD_GPC_NRT) as the short name to get the most recent version available for HARP2 L2.CLOUD_GPC_NRT provisional product (or "Near-Real-Time" products).

```{code-cell} ipython3
results = earthaccess.search_datasets(instrument="harp2")
for item in results:
    summary = item.summary()
    if 'CLOUD' in summary["short-name"]:
        print(summary["short-name"])
```

```{code-cell} ipython3
results = earthaccess.search_data(
    short_name="PACE_HARP2_L2_CLOUD_GPC",
    temporal=("2025-07-02", "2025-07-02"),
    bounding_box=(-90, -15, -89, -14),  # (west, south, east, north) if desired
    count=1,
)
paths = earthaccess.open(results)
```

```{code-cell} ipython3
datatree = xr.open_datatree(paths[0])
```

Here we merge all the data group together for convenience in data manipulations.

```{code-cell} ipython3
dataset = xr.merge(datatree.to_dict().values())
```

## 3. Understanding HARP2 L2.CLOUD_GPC Product Structure

HARP2 CLOUD_GPC products provide descriptive metadata for the variables. However, given the early stage of the product, improvements and changes are expected in future versions.

```{code-cell} ipython3
def print_variable_description(datatree, ret_type_list, exclude=False):
    """
    Print a table of variables, units, and descriptions from the
    ``geophysical_data`` group of a DataTree-like object.

    Parameters
    ----------
    datatree : DataTree or dict-like
        Object containing a ``"geophysical_data"`` group with variables
        whose metadata are stored in ``attrs`` (e.g., ``units`` and ``long_name``).
    ret_type_list : list of str
        Substrings used to filter variable names.
    exclude : bool, default False
        If False (default), only variables whose names contain any of the
        substrings in ``ret_type_list`` are shown. If True, show all others.

    Notes
    -----
    Long descriptions are wrapped to 100 characters; only the first line
    prints the variable name and units.
    """
    print(f"{'Variable':50} | {'Units':10} | Description")
    print("-" * 100)

    for var, da in datatree["geophysical_data"].items():
        # Check inclusion/exclusion logic
        match = any(key in var for key in ret_type_list)
        if (match and not exclude) or (not match and exclude):
            units = da.attrs.get("units", "")
            desc = da.attrs.get("long_name", "")
            wrapped = wrap(desc, 100)
            print(f"{var:50} | {units:10} | {wrapped[0]}")
            for line in wrapped[1:]:
                print(f"{'':50} | {'':10} | {line}")
```

### Cloud Bow Retrievals

One of the main retrieval techniques implemented is the parametric cloud bow retrieval method (Bréon & Goloub, 1998; Alexandrov et al., 2012). The phrase "cloud_bow" is appended to variable names, their corresponding diagnostic variables, and additional variables derived by combining them with OCI Level 2 products. For example, "cloud_bow_droplet_number_concentration_adiabatic" and "cloud_bow_liquid_water_path" are derived using the retrieved droplet size distributions along with OCI L2.CLOUD properties. Additional descriptions can be found in the file attributes as follows:

```{code-cell} ipython3
print_variable_description(datatree, ["bow"])
```

### RFT Retrievals

The second retrieval technique is the Rainbow Fourier Transform (RFT) method (Alexandrov et al., 2012). The prefix cloud_rft is appended to variable names, their associated diagnostic variables, and other outputs generated by this algorithm.

```{code-cell} ipython3
print_variable_description(datatree, ["rft"])
```

### Cloud Liquid Index Retrievals
Cloud Bow Liquid Index (CLI) retrievals provide a measure of the fraction of a cloud top composed of liquid vs ice.

```{code-cell} ipython3
print_variable_description(datatree, ["index"], exclude=False)
```

### Additional Variables From OCI L2.CLOUD Products

In addition to the main quantities retrieved by the algorithms, CLOUD_GPC also includes several commonly useful ancillary variables.

```{code-cell} ipython3
print_variable_description(datatree, ["index", "rft", "bow"], exclude=True)
```

## 4. Visulizing Variables

```{code-cell} ipython3
transform = ccrs.PlateCarree(central_longitude=0)
projection = ccrs.PlateCarree()
def extremes_removed_ids(x):
    """
    Return a boolean mask indicating which elements of `x` are not extreme
    outliers based on the interquartile range (IQR) rule.

    Parameters
    ----------
    x : array-like
        Input numeric array.

    Returns
    -------
    mask : ndarray of bool
        True for values within the range [Q1 − 1.5·IQR, Q3 + 1.5·IQR],
        False for extreme outliers.
    """
    q3 = np.percentile(x, 75)
    q1 = np.percentile(x, 25)
    xmin = q1 - 1.5 * (q3 - q1)
    xmax = q3 + 1.5 * (q3 - q1)
    return (xmin <= x) * (x < xmax)
def geo_axis_tags(ax, crs=ccrs.PlateCarree(central_longitude=0)):
    """
    Add coastlines and labeled latitude/longitude gridlines to a Cartopy axis.

    Parameters
    ----------
    ax : cartopy.mpl.geoaxes.GeoAxes
        Axes object on which to draw the gridlines and coastlines.
    crs : cartopy.crs.CRS, optional
        Coordinate reference system used for the gridlines.
        Default is a Plate Carrée projection with central longitude = 0.

    Returns
    -------
    gl : cartopy.mpl.gridliner.Gridliner
        The configured gridliner object, with labels disabled on the
        top and right sides and font size/color styling applied.
    """
    gl = ax.gridlines(crs=crs, draw_labels=True)
    ax.coastlines()
    gl.top_labels = False
    gl.right_labels = False
    gl.xlabel_style = {"size": 12, "color": "k"}
    gl.ylabel_style = {"size": 12, "color": "k"}

    ax.coastlines()
    return gl
```

Here we visualize the effective radius retrieved using the cloud-bow (parametric) technique. The colorbar limits are adjusted based on the range of observed effective radii, excluding extreme values. Retrievals are only possible in the central portion of the HARP2 granule, where the required angular sampling for the cloud-bow and supernumerary-bow scattering angles is available. Retrieval failure flags, provided in the variable cloud_bow_quality_retrieval_fail, indicate the reasons for unsuccessful retrievals.

```{code-cell} ipython3
var = "cloud_bow_droplet_effective_radius"
fig1, ax1 = plt.subplots(figsize=(10, 6), subplot_kw={"projection": projection})
cmap = plt.get_cmap("viridis", 20)
_arr = dataset[var].values
arr_tes = np.ma.masked_array(_arr, mask=np.isnan(_arr))
vmin, vmax = (
    arr_tes.compressed()[extremes_removed_ids(arr_tes.compressed())].min(),
    arr_tes.compressed()[extremes_removed_ids(arr_tes.compressed())].max(),
)
ctf = ax1.pcolormesh(
    dataset.longitude,
    dataset.latitude,
    arr_tes,
    transform=transform,
    cmap=cmap,
    vmin=vmin,
    vmax=vmax,
)
ax1.set_title(var, size=12)
gl = geo_axis_tags(ax1, crs=transform)
fig1.colorbar(
    ctf, ax=ax1, orientation="vertical", label="%s [%s]" % (var, dataset[var].units)
)
```

Cloud Effective Variance is a key parameter uniquely provided by polarimetry, and together with Cloud Effective Radius, it fully characterizes the modified gamma distribution of cloud droplet sizes. A logarithmic color scale is used to display its detailed variability.

```{code-cell} ipython3
var = "cloud_bow_droplet_effective_variance"
fig1, ax1 = plt.subplots(figsize=(10, 6), subplot_kw={"projection": projection})
cmap = plt.get_cmap("viridis", 40)
norm = mcolors.LogNorm(vmin=0.005, vmax=0.4)
_arr = dataset[var].values
arr_tes = np.ma.masked_array(_arr, mask=np.isnan(_arr))
ctf = ax1.pcolormesh(
    dataset.longitude,
    dataset.latitude,
    arr_tes,
    transform=transform,
    cmap=cmap,
    norm=norm,
)
ax1.set_title(var, size=12)
gl = geo_axis_tags(ax1, crs=transform)
fig1.colorbar(
    ctf, ax=ax1, orientation="vertical", label="%s [%s]" % (var, dataset[var].units)
)
```

When the cloud effective radius is known, the cloud liquid water path can be derived by combining it with OCI’s cloud optical thickness retrievals. The GPC products include such derived cloud liquid water path fields based on the cloud-bow effective radius.

```{code-cell} ipython3
var = "cloud_bow_liquid_water_path"
fig1, ax1 = plt.subplots(figsize=(10, 6), subplot_kw={"projection": projection})
cmap = plt.get_cmap("viridis", 20)
_arr = dataset[var].values
arr_tes = np.ma.masked_array(_arr, mask=np.isnan(_arr))
vmin, vmax = (
    arr_tes.compressed()[extremes_removed_ids(arr_tes.compressed())].min(),
    arr_tes.compressed()[extremes_removed_ids(arr_tes.compressed())].max(),
)
ctf = ax1.pcolormesh(
    dataset.longitude,
    dataset.latitude,
    arr_tes,
    transform=transform,
    cmap=cmap,
    vmin=vmin,
    vmax=vmax,
)
ax1.set_title(var, size=12)
gl = geo_axis_tags(ax1, crs=transform)
fig1.colorbar(
    ctf, ax=ax1, orientation="vertical", label="%s [%s]" % (var, dataset[var].units)
)
```

## 5. Reference

- Breon, F.-M., & Doutriaux-Boucher, M. (2005). A comparison of cloud droplet radii measured from space. IEEE Transactions on Geoscience and Remote Sensing, 43(8), 1796–1805. https://doi.org/10.1109/TGRS.2005.852838
- Alexandrov, M. D., Cairns, B., Emde, C., Ackerman, A. S., & Van Diedenhoven, B. (2012). Accuracy assessments of cloud droplet size retrievals from polarized reflectance measurements by the research scanning polarimeter. Remote Sensing of Environment, 125, 92–111. https://doi.org/10.1016/j.rse.2012.07.012
- Van Diedenhoven, B., Fridlind, A. M., Ackerman, A. S., & Cairns, B. (2012). Evaluation of Hydrometeor Phase and Ice Properties in Cloud-Resolving Model Simulations of Tropical Deep Convection Using Radiance and Polarization Measurements. Journal of the Atmospheric Sciences, 69(11), 3290–3314. https://doi.org/10.1175/JAS-D-11-0314.1
- Alexandrov, M. D., Cairns, B., & Mishchenko, M. I. (2012). Rainbow Fourier transform. Journal of Quantitative Spectroscopy and Radiative Transfer, 113(18), 2521–2535. https://doi.org/10.1016/j.jqsrt.2012.03.025

```{code-cell} ipython3

```
