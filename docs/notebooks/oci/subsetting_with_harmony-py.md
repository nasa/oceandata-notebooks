---
jupytext:
  cell_metadata_filter: all,-trusted
  notebook_metadata_filter: -all,kernelspec,jupytext
  text_representation:
    extension: .md
    format_name: myst
    format_version: 0.13
    jupytext_version: 1.19.4
kernelspec:
  display_name: Python 3 (ipykernel)
  language: python
  name: python3
---

# Subsetting PACE OCI data

**Authors:** Anna Windle (NASA, SSAI), Carina Poulin (NASA, SSAI), Ian Carroll (NASA, UMBC) 

Last Updated: June 29, 2026

<div class="alert alert-success" role="alert">

The following notebooks are **prerequisites** for this tutorial.

- Learn with OCI: [Data Access](oci-data-access)

</div>

<div class="alert alert-info" role="alert">

An [Earthdata Login][edl] account is required to access data from the NASA Earthdata system, including NASA ocean color data.

</div>

[edl]: https://urs.earthdata.nasa.gov/

## Summary

This tutorial demonstrates how to subset PACE OCI L2 and L3M data. L2 data is subsetted here using `harmony-py`, while L3M data is subsetted using `xarray`. 

[Harmony] is a web service that allows you to customize many NASA datasets, including the ability to subset, reproject and reformat files. Data can be subsetted for a geographic region, a temporal range and by variable. In some caess, data can be “reprojected” from its native coordinate reference system (CRS) to the coordinate reference system relevant to your analysis. Data can also be reformatted from its native file format to a format that is more relevant for your application. These services are collectively called transformation services. However, not all services and transformations are available for all datasets. You will learn how to discover which services are available for a given dataset.

Harmony services can be used in multiple ways:
1. through a graphical user interface (GUI) while downloading applicable granules from [Earthdata Search],
2. by direct requests to [Harmony's RESTful API], or, as in this tutorial,
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

At the end of this notebook you will know how to:

- Use the `harmony-py` Python library to spatially and temporally subset PACE OCI Level-2 data
- Download the subsetted data to your local directory
- Stream the subsetted data
- Open and plot subsetted L2 PACE OCI data
- Open and subset PACE OCI Level-3 mapped data using `xarray`

+++

## 1. Setup

+++

Begin by importing all of the packages used in this notebook.

```{code-cell} ipython3
from datetime import datetime
from pathlib import Path

import earthaccess
import matplotlib.pyplot as plt
import numpy as np
import rasterio
import xarray as xr
from harmony import (
    BBox,
    CapabilitiesRequest,
    Client,
    Collection,
    JobsRequest,
    LinkType,
    Request,
)
from IPython.display import JSON
from rasterio.enums import Resampling
```

## 2. Earthdata authentication and Harmony client initalization

+++

The `earthaccess` package lets us easily authenticate with NASA's Earthdata Login (EDL) and pass an EDL token to Harmony.

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

+++

The Harmony service is based around user-submitted jobs. Using the service is a two-step process of (1) creating a specific type of request, and (2) passing the request to the `harmony_client` in exchange for some response from Harmony.

One type of request, the `JobsRequest`, let's you check for any previously submitted jobs. You can filter these jobs using labels, which we will learn how to apply below.

First step, create a request:

```{code-cell} ipython3
request = JobsRequest(labels=["help-hub-tutorial"])
```

Second, get a response from your request submission:

```{code-cell} ipython3
response = harmony_client.submit(request)
JSON(response)
```

For your first time through this tutorial, you shouldn't see any existing jobs. If you've already submitted a job with this label (e.g. because you are re-running this tutorial), then the response includes information about that existing job.

Let's continue to build a request for the subsetting job we want the service to run. Using the "labels" keyword tags jobs so that we can easily find and re-use results from this job later.

```{code-cell} ipython3
request = Request(
    collection=Collection(id="PACE_OCI_L2_BGC"),
    spatial=BBox(-76.75, 36.97, -75.74, 39.01),
    temporal={"start": datetime(2025, 7, 1), "stop": datetime(2025, 8, 1)},
    variables=["geophysical_data/chlor_a"],
    labels=request.labels,
)
```

Depending on whether we got a non-zero count from the `JobsRequest`, we can either submit the subsetting request or dig into the job info we retrieved. Either way, we come up with a `job_id` that uniquely identifies the subsetting job.

```{code-cell} ipython3
if response["count"]:
    job_id = response["jobs"][0]["jobID"]
else:
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

If you want to access a specific job that has already run, you can simply assign a known id to `job_id` and continue below.

Results are kept for 30 days in the Harmony S3 bucket.

+++

## 5. Access the subsetted data

+++

The subsetted files can be accessed by downloading the files to a local machine, or by streaming the data. We will use both access methods in the examples below.

+++

### Download a single file

+++

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

+++

The `download_all` method can use the `job_id` or the `result_json`, which contains result URLs.

As with `download`, the download directory path on the local machine can be specified with the `directory` keyword. To save downloading the same file, the `overwrite` keyword can be set to `False`.

The paths fo the files are returned as a list.

```{code-cell} ipython3
:scrolled: true

futures = harmony_client.download_all(job_id, directory=subsetted_data)
filelist = [f.result() for f in futures]
```

```{code-cell} ipython3
len(filelist)
```

You can now open the files using `xarray`.

```{code-cell} ipython3
dt = xr.open_datatree(filelist[0])
ds = xr.merge(dt.to_dict().values())
ds = ds.set_coords(("longitude", "latitude"))
ds
```

There's no need to keep these files around if you plan to stream the data instead of downloading.

```{code-cell} ipython3
for item in subsetted_data.glob("*"):
    item.unlink()
```

### Stream the files

+++

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
plot = ds["chlor_a"].plot()
```

Now let's plot multiple subsetted granules:

```{code-cell} ipython3
fig, axes = plt.subplots(2, 5, figsize=(10, 4), constrained_layout=True)
axes = axes.ravel()

for ax, file in zip(axes, urls[:10]):

    dt = xr.open_datatree(file, **kwargs)
    ds = xr.merge(dt.to_dict().values())
    ds = ds.set_coords(("longitude", "latitude"))
    date = ds.attrs["time_coverage_start"]
    im = ds["chlor_a"].plot(ax=ax, cmap="viridis", add_colorbar=False, vmin=0, vmax=20)
    ax.set_title(date, fontsize=8)

fig.colorbar(im, ax=axes, orientation="vertical", shrink=0.8, label="Chl a (mg m-3)")
plt.show()
```

To plot using lat, lon coordinates, we need to project the data onto a defined grid with a given reslution. We will use code presented in the [Projecting PACE Data onto a Predefined Grid tutorial.](notebooks/oci/oci_grid_match)

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
    
    # Run projection
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
    
    return dst.rename({"x": "longitude", "y": "latitude"})
```

We choose a 0.015 degree resolution, and the function above employs the plate carrée (lat, lon) projection.

```{code-cell} ipython3
resolution = (0.015, 0.015)
```

```{code-cell} ipython3
dt = xr.open_datatree(urls[0], **kwargs)
ds = xr.merge(dt.to_dict().values())
ds = ds.set_coords(("longitude", "latitude"))
ds_gridded = grid_data(ds, resolution)
plot = ds_gridded["chlor_a"].plot()
```

Plotting first 10 files as subplots, and keeping the gridded "chlor_a" data array for the next section:

```{code-cell} ipython3
fig, axes = plt.subplots(2, 5, figsize=(10, 4), constrained_layout=True)
axes = axes.ravel()
da = []

for ax, file in zip(axes, urls[:10]):

    dt = xr.open_datatree(file, **kwargs)
    ds = xr.merge(dt.to_dict().values())
    ds = ds.set_coords(("longitude", "latitude"))

    ds_gridded = grid_data(ds, resolution)
    da.append(ds_gridded["chlor_a"])
    date = ds_gridded.attrs["time_coverage_start"]
    im = ds_gridded["chlor_a"].plot(ax=ax, cmap="viridis", add_colorbar=False, vmin=0, vmax=20)
    ax.set_title(date, fontsize=8)

    ax.set_xlabel("")
    ax.set_ylabel("")

fig.colorbar(im, ax=axes, orientation="vertical", shrink=0.8, label="Chl a (mg m-3)")
plt.show()
```

Now, we can make a 10-day Chl a composite:

```{code-cell} ipython3
da = xr.concat(da, dim="scene")
chlor_a_mean = da.mean(dim="scene")
plot = chlor_a_mean.plot(cmap="viridis", vmin=0, vmax=20)
```

## 7. Subsetting L3M data

Currently, `harmony-py` does not support spatial subsetting for PACE OCI L3M products. You can verify this by submitting a Harmony request and inspecting the available services, where the subset capabilities are listed as `False`.

```{code-cell} ipython3
capabilities_request = CapabilitiesRequest(short_name="PACE_OCI_L3M_BGC")
capabilities = harmony_client.submit(capabilities_request)
capabilities
```

Because spatial subsetting is not currently supported for PACE OCI L3M products through Harmony, we will instead use `xarray` to subset the data locally. Since L3M products are already mapped to a regular spatial grid, this approach is both straightforward and computationally efficient.

Let's begin by opening a monthly (MO) PACE_OCI_L3M_BGC composite at 4 km spatial resolution using `earthaccess`:

```{code-cell} ipython3
results = earthaccess.search_data(
        short_name="PACE_OCI_L3M_BGC",
        temporal=("2025-07", "2025-07"),
        granule_name="*.MO.*.4km.*",
)
paths = earthaccess.open(results)
```

```{code-cell} ipython3
ds = xr.open_dataset(paths[0])
ds
```

```{code-cell} ipython3
ds_sub = ds['chlor_a'].sel({"lat": slice(39.01, 36.97), "lon": slice(-76.75, -75.74)})
plot = ds_sub.plot.imshow()
```

If we now save this sliced dataset to a netCDF file, we have effectively "downloaded" a subsetted dataset:

```{code-cell} ipython3
path = subsetted_data / ds.attrs["product_name"]
path = path.with_suffix(".subsetted.nc")
print(path)
```

```{code-cell} ipython3
ds_sub.to_netcdf(path)
```

You should now see this file in your "subsetted_data" folder. Let's compare the size to the original L3M file:

```{code-cell} ipython3
og_size = results[0].size()
sub_size = path.stat().st_size / 2**20
print(f"Original Data Size: {og_size:.2f} MB")
print(f"Output Data Size: {sub_size:.2f} MB")
print(f"Data Size % Change: {100 * (1 - sub_size / og_size):.2f} % reduction")
```

<div class="alert alert-info" role="alert">

You have completed the notebook on Subsetting PACE OCI data!

</div>
