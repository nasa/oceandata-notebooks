---
kernelspec:
  display_name: Python 3 (ipykernel)
  language: python
  name: python3
---

# Orientation to Earthdata Cloud Access

**Tutorial Lead:** Anna Windle (NASA, SSAI) <br>
Last updated: July 21, 2025

<div class="alert alert-info" role="alert">

An [Earthdata Login][edl] account is required to access data from the NASA Earthdata system, including NASA ocean color data.

</div>

[edl]: https://urs.earthdata.nasa.gov/

## Summary

In this example we will use the `earthaccess` package to search for
OCI products on NASA Earthdata. The `earthaccess` package, published
on the [Python Package Index][pypi] and [conda-forge][conda],
facilitates discovery and use of all NASA Earth Science data
products by providing an abstraction layer for NASA’s [Common
Metadata Repository (CMR) API][cmr] and by simplifying requests to
NASA's [Earthdata Cloud][edcloud]. Searching for data is more
approachable using `earthaccess` than low-level HTTP requests, and
the same goes for S3 requests.

In short, `earthaccess` helps **authenticate** with an Earthdata Login,
makes **search** easier, and provides a stream-lined way to **load
data** into `xarray` containers. For more on `earthaccess`, visit
the [documentation][earthaccess-docs] site. Be aware that
`earthaccess` is under active development.

To understand the discussions below on downloading and opening data,
we need to clearly understand **where our notebook is
running**. There are three cases to distinguish:

1. The notebook is running on the local host. For instance, you started a Jupyter server on your laptop.
1. The notebook is running on a remote host, but it does not have direct access to the AWS us-west-2 region. For instance, you are running in [GitHub Codespaces][codespaces], which is run on Microsoft Azure.
1. The notebook is running on a remote host that does have direct access to the NASA Earthdata Cloud (AWS us-west-2 region). This is the case for the PACE Hackweek.

[pypi]: https://pypi.org/
[conda]: https://oceancolor.gsfc.nasa.gov/resources/docs/tutorials/notebooks/oci-data-access/
[cmr]: https://www.earthdata.nasa.gov/eosdis/science-system-description/eosdis-components/cmr
[edcloud]: https://www.earthdata.nasa.gov/eosdis/cloud-evolution
[earthaccess-docs]: https://earthaccess.readthedocs.io/en/latest/
[codespaces]: https://github.com/features/codespaces

## Learning Objectives

At the end of this notebook you will know:

* How to store your NASA Earthdata Login credentials with `earthaccess`
* How to use `earthaccess` to search for OCI data using search filters
* How to download OCI data, but only when you need to

## Contents

1. [Setup](#1.-Setup)
2. [NASA Earthdata Authentication](#2.-NASA-Earthdata-Authentication)
3. [Search for Data](#3.-Search-for-Data)
4. [Open Data](#4.-Open-Data)
5. [Download Data](#5.-Download-Data)

+++

## 1. Setup

We begin by importing the packages used in this notebook.

```{code-cell} ipython3
import earthaccess
import xarray as xr
import matplotlib.pyplot as plt
import numpy as np
import cartopy.crs as ccrs
```

[back to top](#Contents)

+++

## 2. NASA Earthdata Authentication

Next, we authenticate using our Earthdata Login
credentials. Authentication is not needed to search publicly
available collections in Earthdata, but is always needed to access
data. We can use the `login` method from the `earthaccess`
package. This will create an authenticated session when we provide a
valid Earthdata Login username and password. The `earthaccess`
package will search for credentials defined by **environmental
variables** or within a **.netrc** file saved in the home
directory. If credentials are not found, an interactive prompt will
allow you to input credentials.

<div class="alert alert-info" role="alert">

The `persist=True` argument ensures any discovered credentials are
stored in a `.netrc` file, so the argument is not necessary (but
it's also harmless) for subsequent calls to `earthaccess.login`.

</div>

```{code-cell} ipython3
auth = earthaccess.login(persist=True)
```

[back to top](#Contents)

+++

## 3. Search for Data

Collections on NASA Earthdata are discovered with the
`search_datasets` function, which accepts an `instrument` filter as an
easy way to get started. Each of the items in the list of
collections returned has a "short-name".

```{code-cell} ipython3
results = earthaccess.search_datasets(instrument="oci")
```

```{code-cell} ipython3
:scrolled: true

for item in results:
    summary = item.summary()
    print(summary["short-name"])
```

<div class="alert alert-info" role="alert">
The short name can also be found on <a href="https://search.earthdata.nasa.gov/search?fi=SPEXone!HARP2!OCI" target="_blank"> Eartdata Search</a>, directly under the collection name, after clicking on the "i" button for a collection in any search result.
</div>

Next, we use the `search_data` function to find granules within a
collection. Let's use the `short_name` for the PACE/OCI Level-2 product for biogeochemical properties (although you can
search for granules across collections too).



The `count` argument limits the number of granules whose metadata is returned and stored in the `results` list.

```{code-cell} ipython3
results = earthaccess.search_data(
    short_name="PACE_OCI_L2_BGC",
    count=1,
)
len(results)
```

We can refine our search by passing more parameters that describe
the spatiotemporal domain of our use case. Here, we use the
`temporal` parameter to request a date range and the `bounding_box`
parameter to request granules that intersect with a bounding box. We
can even provide a `cloud_cover` threshold to limit files that have
a lower percetnage of cloud cover. We do not provide a `count`, so
we'll get all granules that satisfy the constraints.

```{code-cell} ipython3
tspan = ("2024-07-01", "2024-07-31")
bbox = (-76.75, 36.97, -75.74, 39.01)
clouds = (0, 50)
```

```{code-cell} ipython3
results = earthaccess.search_data(
    short_name="PACE_OCI_L2_BGC",
    temporal=tspan,
    bounding_box=bbox,
    cloud_cover=clouds,
)
len(results)
```

Displaying results shows the direct download link: try it! The
link will download one granule to your local machine, which may or
may not be what you want to do. Even if you are running the notebook
on a remote host, this download link will open a new browser tab or
window and offer to save a file to your local machine. If you are
running the notebook locally, this may be of use. However, in the
next section we'll see how to download all the results with one
command.

```{code-cell} ipython3
results[0]
```

[back to top](#Contents)

+++

## 4. Open L2 Data

Let's go ahead and open a couple granules using `xarray`. The `earthaccess.open` function is used when you want to directly read bytes from a remote filesystem, but not download a whole file. When
running code on a host with direct access to the NASA Earthdata
Cloud, you don't need to download the data and `earthaccess.open`
is the way to go.

```{code-cell} ipython3
paths = earthaccess.open(results)
```

The `paths` list contains references to files on a remote filesystem. The ob-cumulus-prod-public is the S3 Bucket in AWS us-west-2 region.

```{code-cell} ipython3
paths
```

Let's open up the first file using XArray.

```{code-cell} ipython3
dat = xr.open_dataset(paths[0])
dat
```

Notice that this `xarray.Dataset` has nothing but "Attributes". The NetCDF data model includes multi-group hierarchies within a single file, where each group maps to an `xarray.Dataset`. The whole file maps to a `xarray.Datatree`, which we can open using:

```{code-cell} ipython3
datatree = xr.open_datatree(paths[0])
datatree
```

Let's convert the `xarray.Datatree` into a `xarray.Dataset` by merging all the nested dictionary values:

```{code-cell} ipython3
dataset = xr.merge(datatree.to_dict().values())
dataset
```

Let's do a quick plot of the `chlor_a` variable.

```{code-cell} ipython3
artist = dataset["chlor_a"].plot(vmax=5)
```

Let's plot with latitude and longitude so we can project the data onto a grid.

```{code-cell} ipython3
dataset = dataset.set_coords(("longitude", "latitude"))
plot = dataset["chlor_a"].plot(x="longitude", y="latitude", cmap="viridis", vmax=5)
```

And if we want to get fancy, we can add the coastline.

```{code-cell} ipython3
fig = plt.figure()
ax = plt.axes(projection=ccrs.PlateCarree())
ax.coastlines()
ax.gridlines(draw_labels={"left": "y", "bottom": "x"})
plot = dataset["chlor_a"].plot(
    x="longitude", y="latitude", cmap="viridis", vmax=5, ax=ax
)
```

[back to top](#Contents)

+++

## 5. Open L3M Data

Let's use `earthaccess` to open some L3 mapped chlorophyll a granules. We will use a new search filter available in earthaccess.search_data: the granule_name argument accepts strings with the "*" wildcard. We need this to distinguish daily ("DAY") from eight-day ("8D") composites, as well as to get the 0.1 degree resolution projections.

```{code-cell} ipython3
tspan = ("2024-04-12", "2024-04-24")

results = earthaccess.search_data(
    short_name="PACE_OCI_L3M_CHL",
    temporal=tspan,
    granule_name="*.DAY.*.0p1deg.*",
)

paths = earthaccess.open(results)
```

Let's open the first file using `xarray`.

```{code-cell} ipython3
dataset = xr.open_dataset(paths[0])
dataset
```

Because the L3M variables have lat and lon coordinates, it's possible to stack multiple granules along a new dimension that corresponds to time. Instead of xr.open_dataset, we use xr.open_mfdataset to create a single xarray.Dataset (the "mf" in open_mfdataset stands for multiple files) from an array of paths.

The paths list is sorted temporally by default, which means the shape of the paths array specifies the way we need to tile the files together into larger arrays. We specify combine="nested" to combine the files according to the shape of the array of files (or file-like objects), even though paths is not a "nested" list in this case. The concat_dim="date" argument generates a new dimension in the combined dataset, because "date" is not an existing dimension in the individual files.

```{code-cell} ipython3
dataset = xr.open_mfdataset(
    paths,
    combine="nested",
    concat_dim="date",
)
dataset
```

A common reason to generate a single dataset from multiple, daily images is to create a composite. Compare the map from a single day ...

```{code-cell} ipython3
chla = np.log10(dataset["chlor_a"])
chla.attrs.update({"units": f'log({dataset["chlor_a"].attrs["units"]})'})

plot = chla.sel({"date": 0}).plot(aspect=2, size=4, cmap="GnBu_r")
```

... to a map of average values, skipping "NaN" values that result from clouds.

```{code-cell} ipython3
chla_avg = chla.mean("date", keep_attrs=True)
plot = chla_avg.plot(aspect=2, size=4, cmap="GnBu_r")
```

## 6. Download Data

Let's go ahead and download a couple granules.

+++

Let's look at the `earthaccess.download` function, which is used
to copy files onto a filesystem local to the machine executing the
code. For this function, provide the output of
`earthaccess.search_data` along with a directory where `earthaccess` will store downloaded granules.

Even if you only want to read a slice of the data, and downloading
seems unncessary, if you use `earthaccess.open` while not running on a remote host with direct access to the NASA Earthdata Cloud,
performance will be very poor. This is not a problem with "the
cloud" or with `earthaccess`, it has to do with the data format and may soon be resolved.

```{code-cell} ipython3
results = earthaccess.search_data(
    short_name="PACE_OCI_L2_BGC",
    temporal=tspan,
    bounding_box=bbox,
    cloud_cover=clouds,
)
```

The `paths` list now contains paths to actual files on the local
filesystem.

```{code-cell} ipython3
paths = earthaccess.download(results, local_path="data")
paths
```

We can open up that locally saved file using `xarray` as well.

```{code-cell} ipython3
xr.open_datatree(paths[0])
```

[back to top](#Contents)
