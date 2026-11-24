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

# Visualize HARP2 GPC Product

**Author(s):** Chamara Rajapakshe (NASA, SSAI), Kirk Knobelspiesse (NASA), Andy Sayer (NASA, UMBC), Meng Gao (NASA, SSAI), Sean Foley (NASA, MSU)

Last updated: November 24, 2026

<div class="alert alert-info" role="alert">

An [Earthdata Login][edl] account is required to access NASA's Earth science data products.

</div>

[edl]: https://urs.earthdata.nasa.gov/

## Summary

This notebook provides an introduction to accessing and working with the HARP2 GISS Polarimetric Cloud (GPC) Level-2 (L2) product (CLOUD_GPC). It covers data acquisition, product structure, and visualization of key variables.

**Note:** This tutorial uses an early, preliminary version of the product. Product contents, variable definitions, and processing algorithms may be updated or optimized in future releases.

## Learning Objectives

By the end of this notebook, you will be able to:

- Acquire HARP2 L2 GPC data
- Identify and describe the variables available in the product
- Visualize and explore key geophysical variables

+++

## 1. Setup

+++

Begin by importing all of the packages used in this notebook. If you followed the guidance on the [Getting Started](https://nasa.github.io/oceandata-notebooks/getting-started.html) page, then the imports will be successful.

```{code-cell} ipython3
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
pd.set_option("display.max_colwidth", 0)
projection = ccrs.PlateCarree()
```

Set your Earthdata Login credentials. You can add `persist=True` to save your credentials in a .netrc file, allowing you to authenticate automatically in the future sessions without re-entering your Earthdata credentials.

```{code-cell} ipython3
auth = earthaccess.login()
```

## 2. Access L2 GPC Data

+++

First, let's search for "CLOUD" in the short-names of HARP2 data.

```{code-cell} ipython3
results = earthaccess.search_datasets(instrument="harp2")

for item in results:
    short_name = item.summary["short-name"]
    if "CLOUD" in short_name:
        print(short_name)
```

We can also search for available granules within a time range and geospatial area of interest. The order of values in a "bounding_box" is always West (longitude), South (latitude), East (longitude), North (latitude). If you know the actual granule name, you can use "granule_name" explicitly. You may get multiple versions if you include a `*` instead of an explicit version. You can also add the Near Real Time (`NRT`) suffix to the short-name for the most recent observations (i.e., PACE_HARP2_L2_CLOUD_GPC_NRT).

```{code-cell} ipython3
results = earthaccess.search_data(
    short_name="PACE_HARP2_L2_CLOUD_GPC",
    granule_name="PACE_HARP2.20240904T205635.L2.CLOUD_GPC.V4*.nc",
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

## 3. Understanding HARP2 L2 CLOUD_GPC Product Structure

HARP2 CLOUD_GPC products provide descriptive metadata for the variables. However, given the early stage of the product, improvements and changes are expected in future versions. Let's define a function that will print a table of data from the `geophysical_data` group.

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

### Cloud Bow Retrievals

One of the primary retrieval techniques implemented in this product is the parametric cloud bow retrieval method ([Bréon & Goloub, 1998](https://doi.org/10.1109/TGRS.2005.852838); [Alexandrov et al., 2012](https://doi.org/10.1016/j.rse.2012.07.012)). The prefix "cloud_bow" is used in variable names to identify quantities retrieved using this method, their associated diagnostic variables, and additional variables derived by combining the retrieval results with OCI L2 products. For example, `cloud_bow_droplet_number_concentration_adiabatic` and `cloud_bow_liquid_water_path` are derived using the retrieved droplet size distributions in conjunction with OCI L2 CLOUD properties. Additional descriptions can be found in the file attributes as follows:

```{code-cell} ipython3
print_variable_description(datatree, ["bow"])
```

### RFT Retrievals

The second retrieval technique is the Rainbow Fourier Transform (RFT) method ([Alexandrov et al., 2012](https://doi.org/10.1016/j.jqsrt.2012.03.025)), which retrieves the full cloud droplet size distribution from the polarized reflectance signature of the cloudbow. The prefix "cloud_rft" is appended to variable names and their associated diagnostic variables.

```{code-cell} ipython3
print_variable_description(datatree, ["rft"])
```

### Cloud Liquid Index Retrievals
The cloud liquid index (CLI) retrievals provide a measure of the fraction of a cloud top composed of liquid vs ice.

```{code-cell} ipython3
print_variable_description(datatree, ["index"], exclude=False)
```

### Additional Variables From OCI L2 CLOUD Products

In addition to the main quantities retrieved by the algorithms, CLOUD_GPC also includes several commonly useful ancillary variables derived from the OCI CLOUD products. 

```{code-cell} ipython3
print_variable_description(datatree, ["index", "rft", "bow"], exclude=True)
```

## 4. Visulizing Variables

Let's define a couple functions to filter and map data.

```{code-cell} ipython3
def extremes_removed_limits(array):
    """
    Return a boolean mask indicating which elements of `array` are not extreme
    outliers based on the interquartile range (IQR) rule.

    Parameters
    ----------
    array : array-like
        Input numeric array.

    Returns
    -------
    tuple
        suggested min and max for axis limits in plots
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

### Cloud bow droplet effective radius

+++

Here, we visualize the effective radius retrieved using the cloud-bow (parametric) technique (`cloud_bow_droplet_effective_radius`). The colorbar limits are adjusted to reflect the range of observed effective radii while excluding extreme values. Retrievals are limited to the central portion of the HARP2 granule, where the required angular sampling for the cloud-bow and supernumerary-bow scattering angles are available. 

```{code-cell} ipython3
fig, ax = plt.subplots(figsize=(10, 6), subplot_kw={"projection": projection})
var = "cloud_bow_droplet_effective_radius"
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
img.colorbar.set_label("Effective Radius (um)")
ax.set_title(var, size=12)
geo_axis_tags(ax, projection)
plt.show()
```

Reasons for unsuccessful retrievals are documented in the `cloud_bow_quality_retrieval_fail` variable, which provides retrieval failure flags: 

```{code-cell} ipython3
fig, ax = plt.subplots(figsize=(10, 6), subplot_kw={"projection": projection})
var = "cloud_bow_quality_retrieval_fail"
array = dataset[var]
cmap = plt.get_cmap('viridis', 12)
img = array.plot.pcolormesh(
    x="longitude",
    y="latitude",
    vmin=0,
    vmax=11,
    cmap=cmap,
)
img.colorbar.set_label("Quality flag")
ax.set_title(var, size=12)
geo_axis_tags(ax, projection)
plt.show()
```

Here, you can see the pixels where `cloud_bow_quality_retrieval_fail` = 0, indicating successful retrievals. 

+++

### Cloud bow droplet effective variance

Cloud effective variance (`cloud_bow_droplet_effective_variance`) is a key parameter that can be uniquely retrieved through polarimetry. In combination with cloud effective radius, it fully characterizes the modified gamma distribution of cloud droplet sizes. A logarithmic color scale is used to highlight the detailed spatial variability.

```{code-cell} ipython3
fig, ax = plt.subplots(figsize=(10, 6), subplot_kw={"projection": projection})
var = "cloud_bow_droplet_effective_variance"
array = dataset[var]
vmin, vmax = extremes_removed_limits(array)
cmap = plt.get_cmap("viridis", 40)
norm = mcolors.LogNorm(vmin=vmin, vmax=vmax)
img = array.plot.pcolormesh(
    x="longitude",
    y="latitude",
    cmap=cmap,
    norm=norm,
)
img.colorbar.set_label("Effective Variance")
ax.set_title(var, size=12)
geo_axis_tags(ax)
plt.show()
```

Cloud effective radius and variance can fully characterize the full droplet size distribution in the form of a normalized modified gamma distribution:

```{code-cell} ipython3
def mod_gamma_norm(re, ve, r=np.arange(0, 30, 0.2)):
    """
    Normalized modified gamma distribution for effective radius and variance.

    Parameters
    ----------
    re : float
        Effective radius in microns
    ve : float
        Effective variance
    r : ndarray, optional
        Radius array in microns (default: 0 to 30 μm in 0.2 μm steps)

    Returns
    -------
    ndarray
        Normalized distribution (Hansen and Travis, 1974)
    """
    f = r ** ((1.0 - 3.0 * ve) / ve) * np.exp(-r / (re * ve))
    C = np.trapezoid(f, r)
    return f / C
```

We'll apply this `mod_gamma_norm` function to retrieve the normalized modified gamma distribution:

```{code-cell} ipython3
radius = np.arange(0, 30, 0.2)  # droplet radius in μm
n_d = mod_gamma_norm(
    dataset["cloud_bow_droplet_effective_radius"][180, 250].values,
    dataset["cloud_bow_droplet_effective_variance"][180, 250].values,
    r=radius,
)
```

```{code-cell} ipython3
plt.plot(radius, n_d)
plt.xlabel(r"$r$ [$\mu$m]")
plt.ylabel(r"$dN/dr$ [$\mathrm{cm}^{-3}$ $\mu\mathrm{m}^{-1}$]")
plt.show()
```

### Cloud bow liquid water path
When the cloud effective radius is known, it can also be combined with OCI’s cloud optical thickness retrievals to derive the cloud liquid water path (`cloud_bow_liquid_water_path`).

```{code-cell} ipython3
fig, ax = plt.subplots(figsize=(10, 6), subplot_kw={"projection": projection})
var = "cloud_bow_liquid_water_path"
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
img.colorbar.set_label("Liquid Water Path (g m-2)")
ax.set_title(var, size=12)
geo_axis_tags(ax)
plt.show()
```

::::{admonition} Test what you learned in this notebook!
:class: note

<details>
<summary>1. What are the three main retrieval techniques in the HARP2 CLOUD_GPC product, and what do they retrieve?</summary>

**Cloud Bow (parametric):** Retrieves droplet effective radius and variance using the cloud bow feature in polarized reflectance. <br>
**RFT (Rainbow Fourier Transform):** Retrieves bimodal droplet size distributions (two modes with separate radius, variance, and fraction). <br>
**CLI (Cloud Liquid Index):** Measures the fraction of cloud top composed of liquid vs. ice (values &lt; 0.3 indicate glaciated cloud tops).
</details>

<details>
<summary>2. Why do the effective radius and variance maps show data only in a narrow stripe down the center of the swath?</summary>

Cloud bow retrievals require observing the rainbow scattering angles (around 140°), which only occurs when HARP2's multi-angle views span a wide enough range. This angular coverage is only available in the central portion of the swath. The `cloud_bow_quality_retrieval_fail` flag indicates where and why retrievals failed.
</details>

<details>
<summary>3. What makes effective variance a "key parameter uniquely provided by polarimetry"?</summary>

Effective variance describes the width of the cloud droplet size distribution. Traditional passive remote sensing (like OCI) can retrieve effective radius but not variance. Polarimetry is sensitive to the detailed shape of the droplet size distribution, enabling variance retrievals. Together, effective radius and variance fully characterize the modified gamma distribution of cloud droplet sizes.
</details>

<details>
<summary>4. The GPC product includes cloud liquid water path (LWP) derived from HARP2 and OCI data. Which sensor provides which piece of information?</summary>

HARP2 provides the cloud droplet **effective radius** from cloud bow retrievals. OCI provides the cloud **optical thickness**. LWP is calculated by combining these two: LWP is proportional to optical thickness × effective radius, assuming liquid water content increases linearly with height from cloud base.
</details>

<details>
<summary>5. Cloud Bow retrieves a single effective radius, but RFT retrieves two modes. When would a bimodal distribution be more realistic?</summary>

Bimodal distributions occur when clouds have two distinct droplet populations, such as: (1) drizzle formation, where large drops coexist with smaller cloud droplets; (2) mixing between cloud layers with different microphysics; or (3) aerosol effects creating separate nucleation modes. Single-mode retrievals would average these populations, missing important cloud processes.
</details>

::::

<div class="alert alert-info" role="alert">

You have completed the notebook on HARP2 cloud products. We now suggest reviewing the notebook on Clouds from [PACE-OCI](https://nasa.github.io/oceandata-notebooks/notebooks/oci/oci_l2_cloud_product.html)

</div>
