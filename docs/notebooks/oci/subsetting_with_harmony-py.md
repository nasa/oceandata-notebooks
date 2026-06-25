---
jupytext:
  notebook_metadata_filter: -all,kernelspec,jupytext
  cell_metadata_filter: all,-trusted
  text_representation:
    extension: .md
    format_name: myst
    format_version: 0.13
    jupytext_version: 1.19.4
kernelspec:
  name: python3
  display_name: Python 3 (ipykernel)
  language: python
---

# Subsetting PACE OCI data using harmony-py

**Authors:** Anna Windle (NASA, SSAI), Carina Poulin (NASA, SSAI), Ian Carroll (NASA, UMBC) 

Last Updated: June 25, 2026

<div class="alert alert-success" role="alert">

The following notebooks are **prerequisites** for this tutorial.

- Learn with OCI: [Data Access](oci-data-access)

</div>

<div class="alert alert-info" role="alert">

An [Earthdata Login][edl] account is required to access data from the NASA Earthdata system, including NASA ocean color data.

</div>

[edl]: https://urs.earthdata.nasa.gov/

## Summary

[Harmony] is a service that allows you to customize many NASA datasets, including the ability to subset, reproject and reformat files. Data can be subsetted for a geographic region, a temporal range and by variable. Data can be “reprojected” from its native coordinate reference system (CRS) to the coordinate reference system relevant to your analysis. Data can be reformatted from its native file format to a format that is more relevant for your application. These services are collectively called transformation services. However, not all services are available for all datasets. You will learn how to discover which services are available for a given dataset.

Harmony services can be used in multiple ways:
1. through a graphical user interface (GUI) while downloading applicable granules from [Earthdata Search],
2. by direct requests to [Harmony's RESTful API], or as in this tutorial,
3. using the `harmony-py` Python package.

The Python package handles NASA Earthdata Login (EDL) authentication and optionally integrates with the CMR Python Wrapper by accepting collection results as a request parameter. It's convenient for scientists who wish to use Harmony from Jupyter notebooks.
After this tutorial, you can dive deeper into `harmony-py` on [ReadTheDocs](https://harmony-py.readthedocs.io/en/main/). 

This tutorial demonstrates how to subset and reformat PACE OCI data from the NASA Earthdata Cloud using `harmony-py`. It is modelled off of tutorials developed by [NSIDC] and [NASA-Openscapes]. 

[Harmony]: https://harmony.earthdata.nasa.gov/
[Earthdata Search]: https://search.earthdata.nasa.gov/
[Harmony's RESTful API]: https://harmony.earthdata.nasa.gov/docs
[harmony-py]: https://github.com/nasa/harmony-py
[NSIDC]: https://github.com/nsidc/NSIDC-Data-Tutorials/blob/main/notebooks/NASA_Earthdata_webinar_short/harmony-py-webinar-short.ipynb
[NASA-Openscapes]: https://nasa-openscapes.github.io/earthdata-cloud-cookbook/tutorials/Harmony.html

## Learning Objectives

At the end of this notebook you will know:

- How to use the `harmony-py` Python library to spatially and temporally subset PACE OCI Level-2 data
- Download the subsetted data to your local directory
- Stream the subsetted data
- Open and plot subsetted L2 PACE OCI data

## Contents
1. [Setup](#1.-Setup)
2. [Earthdata authentication and Harmony client initalization](#2.-Earthdata-authentication-and-Harmony-client-initalization)
3. [Discover subsetting capabilities for Level-2 PACE OCI data](#3.-Discover-subsetting-capabilities-for-Level-2-PACE-OCI-data)
4. [Build and submit a request](#4.-Build-and-submit-a-request)
5. [Access the subsetted data](#5.-Access-the-subsetted-data)
6. [Plot the subsetted data](#6.-Plot-the-subsetted-data)
7. [Subsetting L3M data](#7.-Subsetting-L3M-data)

+++

## 1. Setup

+++

Begin by importing all of the packages used in this notebook.

```{code-cell} ipython3
import datetime as dt
import getpass
from pathlib import Path

import earthaccess
import matplotlib.pyplot as plt
import numpy as np
import rasterio
import xarray as xr
from harmony import BBox, CapabilitiesRequest, Client, Collection, LinkType, Request
from rasterio.enums import Resampling
```

## 2. Earthdata authentication and Harmony client initalization

```{code-cell} ipython3
auth = earthaccess.login()
harmony_client = Client(token=earthaccess.get_edl_token())
```

## 3. Discover subsetting capabilities for Level-2 PACE OCI data

+++

Define which data set you’d like to access using either the dataset `short_name` or its collection `concept_id`. For this example, we’ll use PACE OCI Level-2 Regional Ocean Biogeochemical Properties Data (PACE_OCI_L2_BGC).

```{code-cell} ipython3
capabilities_request = CapabilitiesRequest(short_name="PACE_OCI_L2_BGC")
capabilities = harmony_client.submit(capabilities_request)
capabilities
```

You can see here under `['services']` that this dataset can be subsetted using the `'podacc/l2-subsetter'`

+++

## 4. Build and submit a request

Based on what is returned in the subsetting capabilities above, we can ask for a paticular subsetting.

```{code-cell} ipython3
request = Request(
    collection=Collection(id="PACE_OCI_L2_BGC"),
    spatial=BBox(-76.75, 36.97, -75.74, 39.01),
    temporal={"start": dt.datetime(2025, 7, 1), "stop": dt.datetime(2025, 8, 1)},
    variables=["geophysical_data/chlor_a"],
)
```

Submit the request to the harmony client:

```{code-cell} ipython3
job_id = harmony_client.submit(request)
job_id
```

The `job_id` can be used to check on the details of your job progress. If you are logged into Earthdata, you can see your jobs here: https://harmony.earthdata.nasa.gov/workflow-ui
or look at your process by running this line:

```{code-cell} ipython3
harmony_client.wait_for_processing(job_id, show_progress=True)
```

Note: Requesting a job can take a variable amount of time. In our experience, running this particular job has ranged from 2 to 24 minutes.

```{code-cell} ipython3
job_summary = harmony_client.result_json(job_id)
```

```{code-cell} ipython3
print("Number of granules:", job_summary["numInputGranules"])
print("Original Data Size:", job_summary["originalDataSize"])
print("Output Data Size:", job_summary["outputDataSize"])
print("Data Size % Change:", job_summary["dataSizePercentChange"])
```

If you want to access a job that has already run, you can simply call:

`job_id = '{put job_id here}'`

Results are staged for 30 days in the Harmony s3 bucket.

+++

## 5. Access the subsetted data

The subsetted files can be accessed by downloading the files to a local machine, or by streaming the data. We will use both access methods in the examples below.

+++

### Download a single file

The download method takes a url to a single subsetted file. There are two optional arguments; `directory` used to specify an *existing* folder for storing data (defaults to the current directory), and `overwrite` which defaults to `False` to avoid downloading the same file twice. If you need to download the file again, then set `overwrite=True`.

Let's download the first granule:

```{code-cell} ipython3
url = list(harmony_client.result_urls(job_id))[0]
filepath = harmony_client.download(url).result()
```

You should see this file saved in your local directory.

+++

You can also make a new folder in your local directory to save the subsetted data. Here, we are naming it "subsetted_data":

```{code-cell} ipython3
subsetted_data = Path("subsetted_data")
subsetted_data.mkdir(exist_ok=True)

filepath = harmony_client.download(url, directory=subsetted_data).result()
```

### Download all files
The `download_all` method can use the `job_id` or the `result_json`, which contains result URLs.

As with `download`, the download directory path on the local machine can be specified with the `directory` keyword. To save downloading the same file, the `overwrite` keyword can be set to `False`.

The paths fo the files are returned as a list.

```{code-cell} ipython3
futures = harmony_client.download_all(job_id, directory=subsetted_data)
filelist = [f.result() for f in futures]
```

```{code-cell} ipython3
len(filelist)
```

You can now open the files using `xarray`.

```{code-cell} ipython3
ds = xr.open_datatree(filelist[0])
ds = xr.merge(ds.to_dict().values())
ds = ds.set_coords(("longitude", "latitude"))
ds
```

### Stream the files

If you are working in the AWS `us-west-2` region (the same region as NASA Earthdata Cloud) you can *stream* the data using direct S3 access.

You must be running this notebook in the AWS us-west-2 region to run the following code cells.

We need to get the url for the data in the S3 bucket. We can do this using `result_urls`, as we did for `download` but we set link_type=LinkType.s3 to specify we want the S3 url.

```{code-cell} ipython3
:scrolled: true

urls = list(harmony_client.result_urls(job_id, link_type=LinkType.s3))
urls
```

We need AWS credentials to access the S3 bucket with the results. These can be passed when using `xr.open_datatree`:

```{code-cell} ipython3
kwargs = {
    "engine": "h5netcdf",
    "storage_options": {
        "client_kwargs": harmony_client.aws_credentials(),
    },
}

dt = xr.open_datatree(urls[0], **kwargs)
ds = xr.merge(dt.to_dict().values())
ds = ds.set_coords(("longitude", "latitude"))
ds
```

## 6. Plot the subsetted data

Let's do a quick plot of `chlor_a` from the first granule:

```{code-cell} ipython3
ds.chlor_a.plot()
```

Now let's plot multiple subsetted granules:

```{code-cell} ipython3
fig, axes = plt.subplots(2, 5, figsize=(10, 4), constrained_layout=True)
axes = axes.ravel()

for ax, file in zip(axes, urls[:10]):

    dt = xr.open_datatree(file, **kwargs)
    ds = xr.merge(dt.to_dict().values())
    date = ds.attrs["time_coverage_start"]
    im = ds.chlor_a.plot(ax=ax, cmap="viridis", add_colorbar=False, vmin=0, vmax=20)
    ax.set_title(date, fontsize=8)

fig.colorbar(im, ax=axes, orientation="vertical", shrink=0.8, label="Chl a (mg m-3)")
plt.show()
```

To plot using lat, lon coordinates, we need to project the data onto a defined grid with a given reslution. We will use code presented in the [Projecting PACE Data onto a Predefined Grid tutorial.](https://nasa.github.io/oceandata-notebooks/notebooks/oci/oci_grid_match.html)

```{code-cell} ipython3
def grid_data(src, resolution, dst_crs="epsg:4326", resampling=Resampling.nearest):
    """
    Reproject a L2 dataset to match an input grid. Makes sure 3D variables are
        in (Z, Y, X) dimension order, and all variables have spatial dims/crs 
        assigned.
    Args:
        src - an xarray dataset or dataarray to reproject
        resolution - resolution of the output grid, in dst_crs units
        dst_crs - CRS of the output data
        resampling - resampling method (see rasterio.enums)
    Returns:
        dst - projected xr dataset
    """
    if (len(list(src.dims)) == 3) and (list(src.dims)[0] != "wavelength_3d"):
        src = src.transpose("wavelength_3d", ...)
    src = src.rio.set_spatial_dims("pixels_per_line", "number_of_lines")
    src = src.rio.write_crs("epsg:4326")

    # Calculating the default affine transform
    defaults = rasterio.warp.calculate_default_transform(
        src.rio.crs,
        dst_crs,
        src.rio.width,
        src.rio.height,
        left=src.attrs["geospatial_lon_min"],
        bottom=src.attrs["geospatial_lat_min"],
        right=src.attrs["geospatial_lon_max"],
        top=src.attrs["geospatial_lat_max"],
    )
    # Aligning that transform to our desired resolution
    transform, width, height = rasterio.warp.aligned_target(*defaults, resolution)
    
    dst = src.rio.reproject(
        dst_crs=dst_crs,
        shape=(height, width),
        transform=transform,
        src_geoloc_array=(
            src["longitude"],
            src["latitude"],
        ),
        nodata=np.nan,
        resample=resampling,
    )
    dst["x"] = dst["x"].round(9)
    dst["y"] = dst["y"].round(9)
    
    return dst.rename({"x":"longitude", "y":"latitude"})

resolution = (0.015, 0.015)

ds_gridded = grid_data(ds, resolution)
ds_gridded.rio.transform()

ds_gridded.chlor_a.plot()
```

Plotting first 10 files as subplots:

```{code-cell} ipython3
files = urls[:10]

fig, axes = plt.subplots(2, 5, figsize=(10, 4), constrained_layout=True)
axes = axes.ravel()

for ax, file in zip(axes, files):

    dt = xr.open_datatree(file, **kwargs)
    ds = xr.merge(dt.to_dict().values())
    ds = ds.set_coords(("longitude", "latitude"))

    ds_gridded = grid_data(ds, resolution)
    date = ds_gridded.attrs["time_coverage_start"]
    im = ds_gridded.chlor_a.plot(ax=ax, cmap="viridis", add_colorbar=False, vmin=0, vmax=20)
    ax.set_title(date, fontsize=8)

    ax.set_xlabel("")
    ax.set_ylabel("")

fig.colorbar(im, ax=axes, orientation="vertical", shrink=0.8, label="Chl a (mg m-3)")
plt.show()
```

Now, we can make a 10-day Chl a composite:

```{code-cell} ipython3
gridded_list = []

for file in urls[:10]:

    dt = xr.open_datatree(file, **kwargs)
    ds = xr.merge(dt.to_dict().values())
    ds = ds.set_coords(("longitude", "latitude"))

    ds_gridded = grid_data(ds, resolution)

    gridded_list.append(ds_gridded.chlor_a)

stack = xr.concat(gridded_list, dim="scene")

chl_mean = stack.mean(dim="scene", skipna=True)

fig, ax = plt.subplots(figsize=(6, 4))

chl_mean.plot(
    ax=ax,
    cmap="viridis",
    vmin=0,
    vmax=20
)

ax.set_xlabel("")
ax.set_ylabel("")

plt.tight_layout()
plt.show()
```

## 7. Subsetting L3M data

There are currently no `harmony-py` capabilities to subset PACE OCI L3M data:

```{code-cell} ipython3
capabilities_request = CapabilitiesRequest(short_name="PACE_OCI_L3M_BGC")
capabilities = harmony_client.submit(capabilities_request)
capabilities
```

```{code-cell} ipython3
TODO: figure out xarray workaround
```

<div class="alert alert-info" role="alert">

You have completed the notebook on ... suggest what's next. And don't add an empty cell after this one.

</div>
