---
kernelspec:
  display_name: custom
  language: python
  name: custom
---

# Exploring nitrogen dioxide (NO$_\mathrm{2}$) data from OCI 

**Authors:** Anna Windle (NASA, SSAI) <br>
Modified from a notebook by Zachary Fasnacht (NASA, SSAI)

<div class="alert alert-success" role="alert">

The following notebooks are **prerequisites** for this tutorial.

- [File Structure (OCI Example)](https://oceancolor.gsfc.nasa.gov/resources/docs/tutorials/notebooks/oci-file-structure/)

</div>

## Summary

This tutorial describes how to access and download nitrogen dioxide (NO$_\mathrm{2}$) data products developed from PACE OCI data. More information on how these products were created can be found in [Fasnacht et al. (2025)][paper]. This notebook will also include examples on how to plot NO$_\mathrm{2}$ data as a static and interactive map, as well as how to plot an interactive time series plot. 

[paper]:[10.1088/1748-9326/addfef]

## Learning Objectives

At the end of this notebook you will know:

- How to access and download PACE NO$_\mathrm{2}$ data through the NASA Aura Validation Data Center
- How to open those data using `xarray's` datatree function
- How to plot NO$_\mathrm{2}$ vertical column retrievals as a static and interactive map
- How to create a time series of NO$_\mathrm{2}$ data collected at a single location


## Contents

1. [Setup](#1.-Setup)
2. [Download NO$_\mathrm{2}$ Data](#2.-Download-NO$_\mathrm{2}$-Data)
3. [Read in data using `xarray` and plot
](#3.-Read-in-data-using-xarray-and-plot)
4. [Interactive NO$_\mathrm{2}$ plot](#4.-Interactive-NO$_\mathrm{2}$-plot)
5. [Time Series](#5.-Time-Series)

+++

## 1. Setup

Begin by importing all of the packages used in this notebook. If your kernel uses an environment defined following the guidance on the [tutorials] page, then the imports will be successful.

[tutorials]: https://oceancolor.gsfc.nasa.gov/resources/docs/tutorials/

```{code-cell} ipython3
import subprocess
import os
import re 
import requests

import xarray as xr
import matplotlib.pyplot as plt
import cartopy
import cartopy.crs as ccrs
import cartopy.feature as cfeature
import matplotlib.colors
import hvplot.xarray 
from bs4 import BeautifulSoup
from urllib.parse import urljoin
import pandas as pd
```

[back to top](#Contents)

+++

## 2. Download NO$_\mathrm{2}$ Data

Currently, the NO$_\mathrm{2}$ product has been made available at
[NASA’s Aura Validation Data Center
(AVDC)][aura]. While the data are hosted there, we need to manually download files from this site using the Python modules `subprocess` and `wget`. `subprocess` enables the execution of `wget`, which is a command-line utility for retrieving files from web serviers using https protocols.  However, this product is in the process of implementation and will soon be available in the EarthData Cloud. This tutorial will be updated to use the `earthaccess` Python package to access data once available. 

[aura]: https://avdc.gsfc.nasa.gov/pub/tmp/PACE_NO2/

For this exercise, we will download the file named 'PACE_NO2_Gridded_NAmerica_2024m0501.nc'. Running this cell should save the file in the directory you're working in. 

</div>

```{code-cell} ipython3
url = "https://avdc.gsfc.nasa.gov/pub/tmp/PACE_NO2/NO2_L3_Gridded_NAmerica/PACE_NO2_Gridded_NAmerica_2024m0401.nc"
filename = "PACE_NO2_Gridded_NAmerica_2024m0401.nc"
subprocess.run(["wget", url, "-O", filename], stderr=subprocess.DEVNULL)
```

[back to top](#Contents)

+++

## 3. Read in data using `xarray` and plot

We will use `xarray`'s open_datatree function to open and merge multiple groups of the netcdf as well as swapping the lat, lon dimensions.

```{code-cell} ipython3
dat = xr.open_datatree(filename)
dat = xr.merge(dat.to_dict().values())
dat = dat.swap_dims({"nlat":"latitude", "nlon":"longitude"})
dat
```

If you expand the 'nitrogen_dioxide_total_vertical_column' variable, you'll see that it is a 2D variable consisting of total vertical column NO$_\mathrm{2}$ measurements with units of molecules cm$^\mathrm{-2}$. 
Let's plot it!

```{code-cell} ipython3
fig, ax = plt.subplots(figsize=(9,5), subplot_kw={"projection": ccrs.PlateCarree()})

ax.gridlines(draw_labels={"left": "y", "bottom": "x"}, linewidth=0.25)
ax.coastlines(linewidth=0.5)
ax.add_feature(cfeature.BORDERS, linewidth=0.5)
ax.add_feature(cfeature.OCEAN, linewidth=0.5)
ax.add_feature(cfeature.LAKES, linewidth=0.5)
ax.add_feature(cfeature.LAND, facecolor="oldlace", linewidth=0.5)

cmap = matplotlib.colors.LinearSegmentedColormap.from_list("", ["lightgrey","cyan","yellow","orange","red","darkred"])

dat.nitrogen_dioxide_total_vertical_column.plot(
    x="longitude", y="latitude", vmin=3e15, vmax=10e15, 
    cmap=cmap, zorder=100)

plt.show()
```

Let's zoom in to Los Angeles, California.

```{code-cell} ipython3
fig, ax = plt.subplots(figsize=(9,5), subplot_kw={"projection": ccrs.PlateCarree()})

ax.gridlines(draw_labels={"left": "y", "bottom": "x"}, linewidth=0.25)
ax.coastlines(linewidth=0.5)
ax.add_feature(cfeature.BORDERS, linewidth=0.5)
ax.add_feature(cfeature.OCEAN, linewidth=0.5)
ax.add_feature(cfeature.LAKES, linewidth=0.5)
ax.add_feature(cfeature.LAND, facecolor="oldlace", linewidth=0.5)

cmap = matplotlib.colors.LinearSegmentedColormap.from_list("", ["lightgrey","cyan","yellow","orange","red","darkred"])

dat.nitrogen_dioxide_total_vertical_column.plot(
    x="longitude", y="latitude", vmin=3e15, vmax=10e15, 
    cmap=cmap, zorder=100)

ax.set_extent([-125,-110,30,40])
plt.show()
```

You'll also see other variables in the dataset 'U10M', and 'V10M. These are 10-meter Eastward Wind, and 10-meter Northward Wind, respectively. 

+++

## 4. Interactive NO$_\mathrm{2}$ plot

An interative plot allows you to engage with the data such as zooming, panning, and hovering over for more information. We will use the Python module `hvplot` to make an interactive plot of the single file we downloaded above.

```{code-cell} ipython3
dat.nitrogen_dioxide_total_vertical_column.hvplot(
    x="longitude",
    y="latitude",
    cmap=cmap,
    clim=(3e15, 10e15),
    aspect=2,
    title="Total vertical column NO₂ April 2024",
    widget_location="top",
    geo=True,
    coastline=True,
    tiles="EsriWorldStreetMap"
)
```

# 5. Time Series

Since there are many NO$_\mathrm{2}$ files in the public directory, we can make a time series of NO$_\mathrm{2}$ concentrations over time. First, we have to download all the files locally. This code will download all of the files in a folder called "no2_files".

```{code-cell} ipython3
:scrolled: true

# 1. Set the URL of the directory listing
base_url = "https://avdc.gsfc.nasa.gov/pub/tmp/PACE_NO2/NO2_L3_Gridded_NAmerica/"

# 2. Download the page and parse file links
response = requests.get(base_url)
response.raise_for_status()
soup = BeautifulSoup(response.text, "html.parser")

file_links = []
for link in soup.find_all("a"):
    href = link.get("href")
    if href and "PACE_NO2_Gridded" in href:  # grab only PACE files
        full_url = urljoin(base_url, href)
        file_links.append(full_url)

print(f"Found {len(file_links)} files to download.")

# 3. Create local download folder
download_folder = "no2_files"
os.makedirs(download_folder, exist_ok=True)

# 4. Download files with wget via subprocess
for file_url in file_links:
    local_path = os.path.join(download_folder, os.path.basename(file_url))
    if not os.path.exists(local_path):
        print(f"Downloading {file_url} ...")
        subprocess.run(["wget", "-nc", "-P", download_folder, file_url],
        stdout=subprocess.DEVNULL,
        stderr=subprocess.DEVNULL)
    else:
        print(f"File {local_path} already exists, skipping.")
```

Now we will combine the files into one `xarray` dataset. We will include a new time dimension by grabbing the date in the filename.

```{code-cell} ipython3
folder = "no2_files"
files = sorted([
    os.path.join(folder, f)
    for f in os.listdir(folder)
    if f.endswith(".nc")])

def extract_time(filename):
    # Extract pattern like 2024m0401 → 2024-04-01
    match = re.search(r"(\d{4})m(\d{2})(\d{2})", filename)
    if match:
        year, month, day = match.groups()
        return pd.to_datetime(f"{year}-{month}-{day}")
    else:
        raise ValueError(f"Can't parse date from filename: {filename}")

datasets = []
for f in files:
    ds = xr.open_datatree(f)  
    ds = xr.merge(ds.to_dict().values())
    ds = ds.swap_dims({"nlat":"latitude", "nlon":"longitude"})
    ds = ds.expand_dims(time=[extract_time(f)])
    datasets.append(ds)

# Concatenate along the time dimension
all_no2_dat = xr.concat(datasets, dim="time")
all_no2_dat
```

Let's select the nearest pixel at 34, -118.

```{code-cell} ipython3
no2_sel = all_no2_dat.sel(latitude=34, longitude=-118, method="nearest")
no2_sel
```

You can see how this selection creates a new 1D dataset with values for one pixel across time. Let's plot it using `hvplot`.

```{code-cell} ipython3
line = no2_sel.hvplot.line(
    x="time",
    y="nitrogen_dioxide_total_vertical_column",
    line_width=2,
    color="darkblue",
    alpha=0.8,
)

dots = no2_sel.hvplot.scatter(
    x="time",
    y="nitrogen_dioxide_total_vertical_column",
    size=20,
    color="crimson",
    marker="o",
    alpha=0.7
)

# Combine and add styling
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

You have completed the notebook introducing NO$_\mathrm{2}$ data products from OCI. We suggest looking at the notebook on "Orientation to PACE/OCI Terrestrial Products" tutorial to learn more about the terrestrial data products that can be derived from PACE. 

</div>
