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

# Exploring nitrogen dioxide (NO<sub>2</sub>) data from PACE/OCI

**Author(s):** Anna Windle (NASA, SSAI), Zachary Fasnacht (NASA, SSAI)

Last updated: February 26, 2026

<div class="alert alert-success" role="alert">

The following notebooks are **prerequisites** for this tutorial.

- [File Structure (OCI Example)](/notebooks/oci-file-structure/)

</div>

<div class="alert alert-info" role="alert">

An [Earthdata Login][edl] account is required to access data from the NASA Earthdata system, including NASA ocean color data.

</div>

[edl]: https://urs.earthdata.nasa.gov/

## Summary

This tutorial describes how to access and download trace gas data products developed from PACE OCI data. More information on how these products were created can be found in [Fasnacht et al. (2025)][paper]. This notebook includes examples on how to plot L3M NO<sub>2</sub> data as a static and interactive map, as well as how to plot an interactive time series plot. It also provides examples on how to open and plot L2 NO<sub>2</sub> data.

[paper]: http://doi.org/10.1088/1748-9326/addfef

## Learning Objectives

At the end of this notebook you will know:

- How to access PACE OCI trace gas data products
- Where to find high NO<sub>2</sub> vertical column retrievals (hint: it's a big city)
- How to create a time series of NO<sub>2</sub> data collected at a single location
- Open and plot L2 NO<sub>2</sub> data

+++

## 1. Setup

Begin by importing all of the packages used in this notebook and setting your Earthdata Login credentials.

```{code-cell} ipython3
from datetime import datetime

import cartopy
import cartopy.crs as ccrs
import cartopy.feature as cfeature
import earthaccess
import hvplot.xarray
import matplotlib.colors
import matplotlib.pyplot as plt
import pandas as pd
import xarray as xr
import holoviews
holoviews.config.image_rtol = 1e-2
```

```{code-cell} ipython3
auth = earthaccess.login(persist=True)
```

## 2. Search for L3M PACE Trace Gas Data

Level-2 (L2) and Level-3 mapped (L3M) trace gas (TRGAS) data products are available on NASA Earthdata. 

Let's search and open up the first L3M file collected during the temporal span of January 2025 to December 2025:

```{code-cell} ipython3
tspan = ("2025-01-01", "2025-12-31")

results = earthaccess.search_data(
    short_name="PACE_OCI_L3M_TRGAS",
    temporal = tspan,
    count=1,
)
paths = earthaccess.open(results)
```

```{code-cell} ipython3
paths
```

You can see that this search opened `PACE_OCI.20250101_20250131.L3m.MO.TRGAS.V3_0.0p1deg.nc` which is a L3M monthly (MO) composite with a 0.1 (0p1deg) degree pixel resolution.

+++

## 3. Open as an `XArray` dataset

We will use `xarray.open_dataset` to open the NetCDF and then merge them into a single dataset.

```{code-cell} ipython3
dataset = xr.open_dataset(paths[0])
dataset
```

If you expand the `total_column_no2` variable, you'll see that it is a 2D variable consisting of total vertical column NO<sub>2</sub> measurements with units of molecules cm<sup>-2</sup>.
Let's plot it!

```{code-cell} ipython3
fig, ax = plt.subplots(figsize=(9, 5), subplot_kw={"projection": ccrs.PlateCarree()})
ax.gridlines(draw_labels={"left": "y", "bottom": "x"}, linewidth=0.25)
ax.coastlines(linewidth=0.5)
ax.add_feature(cfeature.BORDERS, linewidth=0.5)
ax.add_feature(cfeature.OCEAN, linewidth=0.5)
ax.add_feature(cfeature.LAKES, linewidth=0.5)
ax.add_feature(cfeature.LAND, facecolor="oldlace", linewidth=0.5)
cmap = matplotlib.colors.LinearSegmentedColormap.from_list(
    "",
    ["lightgrey", "cyan", "yellow", "orange", "red", "darkred"],
)
dataset["total_column_no2"].plot(
    x="lon", y="lat", vmin=3e15, vmax=10e15, cmap=cmap, zorder=100
)
plt.show()
```

Let's zoom in to Los Angeles, California.

```{code-cell} ipython3
fig, ax = plt.subplots(figsize=(9, 5), subplot_kw={"projection": ccrs.PlateCarree()})
ax.gridlines(draw_labels={"left": "y", "bottom": "x"}, linewidth=0.25)
ax.coastlines(linewidth=0.5)
ax.add_feature(cfeature.BORDERS, linewidth=0.5)
ax.add_feature(cfeature.OCEAN, linewidth=0.5)
ax.add_feature(cfeature.LAKES, linewidth=0.5)
ax.add_feature(cfeature.LAND, facecolor="oldlace", linewidth=0.5)
dataset["total_column_no2"].plot(
    x="lon", y="lat", vmin=3e15, vmax=10e15, cmap=cmap, zorder=100
)
ax.set_extent([-125, -110, 30, 40])
plt.show()
```

## 4. Interactive NO<sub>2</sub> plot

An interative plot allows you to engage with the data such as zooming, panning, and hovering over for more information. We will use the `hvplot` accessor on XArray data structures to make an interactive plot of the single file we accessed above.

```{code-cell} ipython3
dataset["total_column_no2"].hvplot(
    x="lon",
    y="lat",
    cmap=cmap,
    clim=(3e15, 10e15),
    aspect=2,
    title="Total vertical column NO₂ April 2024",
    widget_location="top",
    geo=True,
    coastline=True,
    tiles="EsriWorldStreetMap",
)
```

## 5. Time Series

Since there are many NO<sub>2</sub> granules available, we can make a time series of NO<sub>2</sub> concentrations over time. Let's search for L3M trace gas data as monthly composites at 4km from January-December 2025:

```{code-cell} ipython3
results = earthaccess.search_data(
    short_name="PACE_OCI_L3M_TRGAS",
    granule_name="*.MO.*.4km.*",
    temporal=tspan,
)
paths = earthaccess.open(results)
```

You can see that 12 L3M files were found, one for each month. Now we will combine the files into one `xarray` dataset. This can take several minutes.

```{code-cell} ipython3
dataset = xr.open_mfdataset(
    paths,
    concat_dim="date",
    combine="nested",
)
dataset
```

Let's replace the date coordiante with date information from dataset attributes.

```{code-cell} ipython3
dates = [xr.open_dataset(i).attrs["time_coverage_end"] for i in paths]
dt = pd.to_datetime(dates)
dataset = dataset.assign_coords(date=dt.values)
dataset
```

Let's select the nearest pixel to 34°N, 118°W (Los Angeles).

```{code-cell} ipython3
array = (
    dataset["total_column_no2"]
    .sel({"lat": 34, "lon": -118}, method="nearest")
)
array
```

You can see how this selection creates a new 1D dataset with values for one pixel across time. Let's plot it using `hvplot`.

```{code-cell} ipython3
(array.hvplot.line(
        x="date",
        line_width=2)
* array.hvplot.scatter(
        x="date",
        size=60, color="crimson")).opts(
    title="Time series of total vertical column NO₂ at (34°N, -118°W)",
    width=800,
    height=400,
    ylabel="NO₂ (molecules cm⁻²)",
    show_grid=True,
)
```

# 6. Search and open Level-2 trace gas data

PACE OCI trace gas data is also available as Level-2 granules. Let's search, open, and plot L2 TRGAS data of the LA region for two weeks in July 2025.

```{code-cell} ipython3
tspan = ("2025-07-01", "2025-07-14")
bbox = (-119.0, 33.5, -117.5, 34.5)

results = earthaccess.search_data(
    short_name="PACE_OCI_L2_TRGAS",
    temporal = tspan,
    bounding_box = bbox)

paths = earthaccess.open(results)
```

```{code-cell} ipython3
fig, axes = plt.subplots(3, 7, figsize=(20, 6), subplot_kw={"projection": ccrs.PlateCarree()}) #, constrained_layout=True)
axes = axes.flatten()

extent = [-119.0, -117.5, 33.5, 34.5]

for i, file_path in enumerate(paths):
    ds = xr.open_datatree(file_path)
    ds = xr.merge(ds.to_dict().values())
    ds = ds.set_coords(("longitude", "latitude"))
    
    var = ds["total_column_no2"]
    start_date = ds.attrs.get("time_coverage_start")
    start_date = datetime.fromisoformat(start_date.replace("Z", ""))

    im = var.plot(ax=axes[i], x="longitude", y="latitude", vmin=3e15, vmax=10e15, cmap=cmap, add_colorbar=False)
    axes[i].set_title(start_date.strftime("%Y-%m-%d %H:%M:%S"))

    # Remove default axes ticks/labels
    axes[i].set_xticks([])
    axes[i].set_yticks([])
    axes[i].set_xlabel("")
    axes[i].set_ylabel("")
    axes[i].set_extent(extent)

    axes[i].coastlines(resolution="10m")
    axes[i].add_feature(cfeature.BORDERS, linestyle=":")
     
    # Gridlines
    gl = axes[i].gridlines(draw_labels=True, linewidth=0.5, color="gray", alpha=0.5, linestyle="--")
    gl.top_labels = False
    gl.right_labels = False

    # Show left labels only for first column
    gl.left_labels = (i % ncols == 0)

    # Show bottom labels only for bottom row
    gl.bottom_labels = (i // ncols == nrows - 1)

# Hide unused axes if n_files < nrows*ncols
for j in range(i+1, len(axes)):
    axes[j].axis("off")

# Add a single colorbar
fig.colorbar(im, ax=axes, orientation="vertical", fraction=0.02, pad=0.02, label=var_name)

plt.show()
```

<div class="alert alert-info" role="alert">

You have completed the notebook introducing NO<sub>2</sub> data products from OCI. We suggest looking at the notebook on [Orientation to PACE/OCI Terrestrial Products][terrestrial] tutorial to learn more about the terrestrial data products that can be derived from PACE OCI data.

</div>

[terrestrial]: /notebooks/oci-terrestrial-data/
