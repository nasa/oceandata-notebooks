---
jupytext:
  text_representation:
    extension: .md
    format_name: myst
    format_version: 0.13
    jupytext_version: 1.17.2
kernelspec:
  name: python3
  display_name: Python 3 (ipykernel)
  language: python
---

# Exploring nitrogen dioxide (NO<sub>2</sub>) data from OCI

**Authors:** Anna Windle (NASA, SSAI), Zachary Fasnacht (NASA, SSAI) <br>
Last updated: July 28, 2025

<div class="alert alert-success" role="alert">

The following notebooks are **prerequisites** for this tutorial.

- [File Structure (OCI Example)](https://oceancolor.gsfc.nasa.gov/resources/docs/tutorials/notebooks/oci-file-structure/)

</div>

## Summary

This tutorial describes how to access and download nitrogen dioxide (NO<sub>2</sub>) data products developed from PACE OCI data. More information on how these products were created can be found in [Fasnacht et al. (2025)][paper]. This notebook will also include examples on how to plot NO<sub>2</sub> data as a static and interactive map, as well as how to plot an interactive time series plot.

[paper]: http://doi.org/10.1088/1748-9326/addfef

## Learning Objectives

At the end of this notebook you will know:

- Where to access NO<sub>2</sub> data products in development for the PACE Mission at the NASA Aura Validation Data Center
- What to select from the XArray `DataTree` objects representing hierarchichal datasets
- Where to find high NO<sub>2</sub> vertical column retrievals (hint: it's a big city)
- How to create a time series of NO<sub>2</sub> data collected at a single location

## Contents

1. [Setup](#1.-Setup)
2. [Download NO<sub>2</sub> Data](#2.-Download-NO<sub>2</sub>-Data)
3. [Read in data using `xarray` and plot](#3.-Read-in-data-using-xarray-and-plot)
4. [Interactive NO<sub>2</sub> plot](#4.-Interactive-NO<sub>2</sub>-plot)
5. [Time Series](#5.-Time-Series)

+++

## 1. Setup

Begin by importing all of the packages used in this notebook. If your kernel uses an environment defined following the guidance on the [tutorials] page, then the imports will be successful.

[tutorials]: https://oceancolor.gsfc.nasa.gov/resources/docs/tutorials/

```{code-cell} ipython3
from datetime import datetime

import cartopy
import cartopy.crs as ccrs
import cartopy.feature as cfeature
import fsspec
import hvplot.xarray
import matplotlib.colors
import matplotlib.pyplot as plt
import pandas as pd
import xarray as xr
import holoviews
holoviews.config.image_rtol = 1e-2

swap_dims = {"nlon": "longitude", "nlat": "latitude"}
```

[back to top](#Contents)

+++

## 2. Download NO<sub>2</sub> Data

While under development, the NO<sub>2</sub> product is available at
[NASA’s Aura Validation Data Center
(AVDC)][aura]. While the data are hosted there, we can access files from this site using the `fsspec` package. Once this product is implemented by the PACE Mission Science Data Segment (SDS), it will be available in the Earthdata Cloud and accessible as usual using the `earthaccess` package.

[aura]: https://avdc.gsfc.nasa.gov/pub/tmp/PACE_NO2/

```{code-cell} ipython3
url = "https://avdc.gsfc.nasa.gov/pub/tmp/PACE_NO2/NO2_L3_Gridded_NAmerica/PACE_NO2_Gridded_NAmerica_2024m0401.nc"
fs = fsspec.filesystem("https")
path = fs.open(url, cache_type="blockcache")
```

[back to top](#Contents)

+++

## 3. Preview this hierarchical dataset

We will use `xarray.open_datatree` to open all groups in the NetCDF and then merge them into a single dataset. We need to clean up some superfluous data stored as `nlat` and `nlon` along the way.

```{code-cell} ipython3
datatree = xr.open_datatree(path)
datatree["/"].dataset = datatree["/"].dataset.drop_vars(swap_dims)
dataset = xr.merge(datatree.to_dict().values()).swap_dims(swap_dims)
dataset
```

If you expand the `nitrogen_dioxide_total_vertical_column` variable, you'll see that it is a 2D variable consisting of total vertical column NO<sub>2</sub> measurements with units of molecules cm<sup>-2</sup>.
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
dataset["nitrogen_dioxide_total_vertical_column"].plot(
    x="longitude", y="latitude", vmin=3e15, vmax=10e15, cmap=cmap, zorder=100
)
plt.show()
```

Let's zoom in to Los Angeles, California ... i.e., the bright red blob in the lower left.

```{code-cell} ipython3
fig, ax = plt.subplots(figsize=(9, 5), subplot_kw={"projection": ccrs.PlateCarree()})
ax.gridlines(draw_labels={"left": "y", "bottom": "x"}, linewidth=0.25)
ax.coastlines(linewidth=0.5)
ax.add_feature(cfeature.BORDERS, linewidth=0.5)
ax.add_feature(cfeature.OCEAN, linewidth=0.5)
ax.add_feature(cfeature.LAKES, linewidth=0.5)
ax.add_feature(cfeature.LAND, facecolor="oldlace", linewidth=0.5)
dataset["nitrogen_dioxide_total_vertical_column"].plot(
    x="longitude", y="latitude", vmin=3e15, vmax=10e15, cmap=cmap, zorder=100
)
ax.set_extent([-125, -110, 30, 40])
plt.show()
```

You'll also see other variables in the dataset `U10M`, and `V10M`.
These are 10-meter Eastward Wind, and 10-meter Northward Wind, respectively.

+++

## 4. Interactive NO<sub>2</sub> plot

An interative plot allows you to engage with the data such as zooming, panning, and hovering over for more information. We will use the `hvplot` accessor on XArray data structures to make an interactive plot of the single file we accessed above.

```{code-cell} ipython3
dataset["nitrogen_dioxide_total_vertical_column"].hvplot(
    x="longitude",
    y="latitude",
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

# 5. Time Series

Since there are many NO<sub>2</sub> granules available for testing, we can make a time series of NO<sub>2</sub> concentrations over time. First, we have to get URLs for all the granules and "open" them for streaming. Alternatively, `fs.get` could be used to download files locally, but we don't want to duplicate data storage if working in the commercial cloud.

```{code-cell} ipython3
:scrolled: true

pattern = "https://avdc.gsfc.nasa.gov/pub/tmp/PACE_NO2/NO2_L3_Gridded_NAmerica/PACE_NO2_Gridded_*.nc"
results = fs.glob(pattern)
paths = [fs.open(i, cache_type="blockcache") for i in results]
```

Now we will combine the files into one `xarray` dataset, for which we have to access one group at a time within the hierarchichal datasets. This can take several minutes.

```{code-cell} ipython3
dataset = xr.open_mfdataset(
    paths,
    group="geophysical_data",
    concat_dim="time",
    combine="nested",
)
```

We can get the spatial coordinates from the first granule, since these are invariant.
We have concatenated along a new dimension (i.e., a dimension not present in the datasets). To incorporate the temporal coordinates, we can add a variable for the "time" dimension by grabbing it from the filename.

```{code-cell} ipython3
space = xr.open_dataset(paths[0], group="navigation_data")
time = [datetime.strptime(i[-12:-3], "%Ym%m%d") for i in results]
dataset = (
    xr.merge((dataset, space, {"time": ("time", time)}))
    .swap_dims(swap_dims)
)
```

Let's select the nearest pixel to 34°N, 118°W.

```{code-cell} ipython3
array = (
    dataset["nitrogen_dioxide_total_vertical_column"]
    .sel({"latitude": 34, "longitude": -118}, method="nearest")
)
array
```

You can see how this selection creates a new 1D dataset with values for one pixel across time. Let's plot it using `hvplot`.

```{code-cell} ipython3
line = array.hvplot.line(line_width=2, color="darkblue", alpha=0.8)
dots = array.hvplot.scatter(size=20, color="crimson", marker="o", alpha=0.7)
```

We've created two plots, and now we combine them, add styling, and display.

```{code-cell} ipython3
(line * dots).opts(
    title="Time series of total vertical column NO₂ at (34, -118)",
    width=800,
    height=400,
    xlabel="Time",
    ylabel="NO₂ (molecules cm⁻²)",
    show_grid=True,
)
```

[back to top](#Contents)

<div class="alert alert-info" role="alert">

You have completed the notebook introducing NO<sub>2</sub> data products from OCI. We suggest looking at the notebook on [Orientation to PACE/OCI Terrestrial Products][terrestrial] tutorial to learn more about the terrestrial data products that can be derived from PACE OCI data.

[terrestrial]: https://oceancolor.gsfc.nasa.gov/resources/docs/tutorials/notebooks/oci-terrestrial-data/)

</div>
