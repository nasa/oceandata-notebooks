---
jupytext:
  notebook_metadata_filter: -all,kernelspec,jupytext
  cell_metadata_filter: all,-trusted
  text_representation:
    extension: .md
    format_name: myst
    format_version: 0.13
    jupytext_version: 1.18.1
kernelspec:
  name: python3
  display_name: Python 3 (ipykernel)
  language: python
---

# Subsetting PACE OCI data using harmony-py

**Authors:** Anna Windle (NASA, SSAI), First Last (NASA, ...)

<div class="alert alert-success" role="alert">

The following notebooks are **prerequisites** for this tutorial.

- Learn with OCI: [Data Access](oci-data-access)

</div>

<div class="alert alert-info" role="alert">

An [Earthdata Login][edl] account is required to access data from the NASA Earthdata system, including NASA ocean color data.

</div>

[edl]: https://urs.earthdata.nasa.gov/

## Summary

[Harmony](https://harmony.earthdata.nasa.gov/) is a transformation is a service that allows you to customize many NASA datasets, including the ability to subset, reproject and reformat files. Data can be subsetted for a geographic region, a temporal range and by variable. Data can be “reprojected” from its native coordinate reference system (CRS) to the coordinate reference system relevant to your analysis. And data can be reformatted from its native file format to a format that is more relevant for your application. These services are collectively called transformation services. However, not all services are available for all datasets. You will learn how to discover which services are available for a given dataset.

[`harmony-py`](https://github.com/nasa/harmony-py) is a Python library alternative to directly using Harmony's RESTful API. You can find more information about `harmony-py` in the [readthedocs](https://harmony-py.readthedocs.io/en/main/) documentation. It handles NASA Earthdata Login (EDL) authentication and optionally integrates with the CMR Python Wrapper by accepting collection results as a request parameter. It's convenient for scientists who wish to use Harmony from Jupyter notebooks. 

This tutorial demonstrates how to subset and reformat PACE OCI data from the NASA Earthdata Cloud using `harmony-py`. It is modelled off of tutorials developed by [NSIDC](https://github.com/nsidc/NSIDC-Data-Tutorials/blob/main/notebooks/NASA_Earthdata_webinar_short/harmony-py-webinar-short.ipynb) and [Openscapes](https://nasa-openscapes.github.io/earthdata-cloud-cookbook/tutorials/Harmony.html). 


## Learning Objectives

At the end of this notebook you will know:

- How to use the `harmony-py` Python library to spatially and temporally subset PACE OCI Level-2 data
- Download the subsetted data to your local directory
- Stream the subsetted data
- Open and plot subsetted L2 PACE OCI data 

+++

## 1. Setup

+++

Begin by importing all of the packages used in this notebook.

```{code-cell} ipython3
pip install -U harmony-py
```

```{code-cell} ipython3
import datetime as dt
import getpass
from pathlib import Path
import earthaccess
import s3fs
import xarray as xr
from harmony import BBox, CapabilitiesRequest, Client, Collection, LinkType, Request
```

## 2. Earthdata authentication and Harmony client initalization

```{code-cell} ipython3
EDL_username = input("EDL username?:")
EDL_password = getpass.getpass("EDL password?:")
harmony_client = Client(auth=(EDL_username, EDL_password))
```

## 3. Discover subsetting capabilities for PACE OCI data

+++

Define which data set you’d like to access using either the dataset `short_name` or its collection `concept-id`. For this example, we’ll use PACE OCI Level-2 Regional Ocean Biogeochemical Properties Data (PACE_OCI_L2_BGC).

```{code-cell} ipython3
capabilities_request = CapabilitiesRequest(short_name="PACE_OCI_L2_BGC")
capabilities = harmony_client.submit(capabilities_request)
capabilities
```

You can see here that this dataset be subsetted.

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

Submit the request:

```{code-cell} ipython3
job_id = harmony_client.submit(request)
job_id
```

The `job_id` can be used to check on the details of your job progress. If you are logged into Earthdata, you can see your jobs here: https://harmony.earthdata.nasa.gov/workflow-ui

```{code-cell} ipython3
harmony_client.wait_for_processing(job_id, show_progress=True)
```

Note: Requesting a job can take a variable amount of time. In our experience, running this particular job has ranged from 2 to 24 minutes.

```{code-cell} ipython3
print("Number of granules:", job_summary["numInputGranules"])
print("Original Data Size:", job_summary["originalDataSize"])
print("Output Data Size:", job_summary["outputDataSize"])
print("Data Size % Change:", job_summary["dataSizePercentChange"])
```

If you want to access a job that has already run, you can just simply put in the `job_id`:

`job_id = '286dd8e2-38e0-4de7-a762-1437a543ec4a'`

Results are staged for 30 days in the Harmony s3 bucket.

+++

## 5. Access the subsetted data

The subsetted files can be accessed by downloading the files to a local machine, or by streaming the data. We will use both access methods in the examples below.

+++

### Download a single file
The download method takes a url to a single subsetted file. The `directory` keyword is used to specify a download path. The default is the current working directory (`.`). Setting `overwrite` to False avoids downloading the same file twice. If you need to download the file again, then set `overwrite=True`.

Let's download the first granule:

```{code-cell} ipython3
url = list(harmony_client.result_urls(job_id))[0]
filepath = harmony_client.download(url, directory=".", overwrite=False).result()
```

You should see this file saved in your local directory. 

+++

You can also make a new folder in your local directory to save the subsetted data. Here, we are naming it "subsetted_data":

```{code-cell} ipython3
Path("subsetted_data").mkdir(exist_ok=True)

filepath = harmony_client.download(
    url, directory="subsetted_data", overwrite=False
).result()
```

### Download all files
The `download_all` method can use the `job-id` or the `result-json`, which contains result urls.

As with `download`, the download directory path on the local machine can be specified with the `directory` keyword. To save downloading the same file, the overwrite keyword can be set to False.

The paths fo the files are returned as a list.

```{code-cell} ipython3
---
collapsed: true
jupyter:
  outputs_hidden: true
---
futures = harmony_client.download_all(
    job_id, directory="subsetted_data", overwrite=False
)
filelist = [f.result() for f in futures]
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
---
collapsed: true
jupyter:
  outputs_hidden: true
---
urls = list(harmony_client.result_urls(job_id, link_type=LinkType.s3))
urls
```

We need AWS credentials to access the S3 bucket with the results. These are returned using the `aws_credentials` method.

```{code-cell} ipython3
creds = harmony_client.aws_credentials()
```

We then create a virtual file system that allows us to access the S3 bucket. We pass the credentials to authenticate.

```{code-cell} ipython3
s3_fs = s3fs.S3FileSystem(
    key=creds["aws_access_key_id"],
    secret=creds["aws_secret_access_key"],
    token=creds["aws_session_token"],
    client_kwargs={"region_name": "us-west-2"},
)
```

We then open the S3 url as a file-like object.

A file-like object is just what it sounds like, an object - a collection of bytes in memory - that is recognized as a file by applications.

```{code-cell} ipython3
---
collapsed: true
jupyter:
  outputs_hidden: true
---
f = [s3_fs.open(url, mode="rb") for url in urls]
f
```

We can then open one of the files using `xarray`.

```{code-cell} ipython3
ds = xr.open_datatree(f[0])
ds = xr.merge(ds.to_dict().values())
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
files = f[:10]

fig, axes = plt.subplots(2, 5, figsize=(10, 4), constrained_layout=True)
axes = axes.ravel()

for ax, file in zip(axes, files):

    dt = xr.open_datatree(file)
    ds = xr.merge(dt.to_dict().values())

    date = ds.attrs["time_coverage_start"]

    im = ds.chlor_a.plot(ax=ax, cmap="viridis", add_colorbar=False, vmin=0, vmax=20)

    ax.set_title(date, fontsize=8)

fig.colorbar(im, ax=axes, orientation="vertical", shrink=0.8, label="Chl a (mg m-3)")

plt.show()
```

```{code-cell} ipython3

```

```{code-cell} ipython3

```

## Anna notes:

+++

Only way I could figure out how to plot with lat/lon:

```{code-cell} ipython3
files = f[:10]

fig, axes = plt.subplots(2, 5, figsize=(10, 4), constrained_layout=True)
axes = axes.ravel()

for i, (ax, file) in enumerate(zip(axes, files)):

    # open datatree
    dt = xr.open_datatree(file)
    ds = xr.merge(dt.to_dict().values())

    date = ds.attrs["time_coverage_start"]

    # extract arrays
    lon = ds.longitude.values
    lat = ds.latitude.values
    chl = ds.chlor_a.values

    # mask valid pixels
    mask = np.isfinite(lon) & np.isfinite(lat) & np.isfinite(chl)

    sc = ax.scatter(
        lon[mask], lat[mask], c=chl[mask], s=2, cmap="viridis", vmin=0, vmax=20
    )

    ax.set_title(date, fontsize=8)

# shared colorbar
cbar = fig.colorbar(sc, ax=axes, shrink=0.8)
cbar.set_label("Chl a (mg m-3)")

plt.show()
```

I'd love to show an average chl with all granules, but not sure if possible since misaligned grids. Since plotting with L2 is tricky, I could show example with L3?

```{code-cell} ipython3
capabilities_request = CapabilitiesRequest(short_name="PACE_OCI_L3M_BGC")
capabilities = harmony_client.submit(capabilities_request)
capabilities
```

Looks like I can't with L3M....

+++

So, I think this tool is great to subset spatially/temporally/ by variable to download less data. This workflow cut the data size by  99.3% which is prety significant. But then it's kind of hard to work with the data because they are all on a common grid. So, if we could come up with a way to combine/concatenate them so they're all on same grid that could be useful. I also am not sure why it doesn't work with L3M data, but if it did that would be easier to work with. 

+++

potential solution from chatgpt, but not the mean:

```{code-cell} ipython3
files = f[:10]

all_lon = []
all_lat = []
all_chl = []

for file in files:

    dt = xr.open_datatree(file)
    ds = xr.merge(dt.to_dict().values())

    lon = ds.longitude.values
    lat = ds.latitude.values
    chl = ds.chlor_a.values

    mask = np.isfinite(lon) & np.isfinite(lat) & np.isfinite(chl)

    all_lon.append(lon[mask])
    all_lat.append(lat[mask])
    all_chl.append(chl[mask])

# concatenate ALL granules into one cloud of points
lon_all = np.concatenate(all_lon)
lat_all = np.concatenate(all_lat)
chl_all = np.concatenate(all_chl)

# plot mean field as scatter (composite)
plt.figure(figsize=(6,5))

sc = plt.scatter(
    lon_all,
    lat_all,
    c=chl_all,
    s=6,
    cmap="viridis",
    vmin=0,
    vmax=20
)

plt.colorbar(sc, label="chlor_a")
plt.xlabel("Longitude")
plt.ylabel("Latitude")
plt.title("Multi-granule Chlorophyll Composite (point-based)")

plt.show()
```

<div class="alert alert-info" role="alert">

You have completed the notebook on ... suggest what's next. And don't add an empty cell after this one.

</div>
