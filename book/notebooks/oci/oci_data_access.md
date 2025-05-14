# Access Data from the Ocean Color Instrument (OCI)

**Authors:** Anna Windle (NASA, SSAI), Ian Carroll (NASA, UMBC), Carina Poulin (NASA, SSAI)

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
approachable using `earthaccess` when compared to using low-level
HTTP requests or working diectly with S3 object stores.

In short, `earthaccess` helps **authenticate** with Earthdata Login,
makes **search** easier, and provides a stream-lined way to **load
data** into `xarray` containers. For more on `earthaccess`, visit
the [documentation][earthaccess-docs] site. Be aware that
`earthaccess` is under active development.

To understand the discussions below on downloading and opening data,
we need to clearly understand **where our notebook is
running**. There are three cases to distinguish:

1. The notebook is running on the local host. A Jupyter server on your laptop is a local host.
1. The notebook is running on a remote host, but it does not have direct access to the NASA Earthdata Cloud. For instance, [GitHub Codespaces][codespaces] is a remote host that runs on a different cloud platform than the NASA Earthdata Cloud.
1. The notebook is running on a remote host that does have direct access to the NASA Earthdata Cloud.

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

```{code-cell}
import earthaccess
import xarray as xr
```

[back to top](#Contents)

+++

## 2. NASA Earthdata Authentication

Next, we authenticate using our Earthdata Login
credentials. Authentication is not needed to search publicly
available collections in Earthdata, but is always needed to access
data. We use the `login` method from the `earthaccess`
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

```{code-cell}
auth = earthaccess.login(persist=True)
```

[back to top](#Contents)

+++

## 3. Search for Data

Collections on NASA Earthdata are discovered with the
`search_datasets` function, which accepts an `instrument` filter as an
easy way to get started. Each item in the list of
collections returned in the search results has a "short-name".

```{code-cell}
results = earthaccess.search_datasets(instrument="oci")
```

```{code-cell}
for item in results:
    summary = item.summary()
    print(summary["short-name"])
```

<div class="alert alert-info" role="alert">

The short name can also be found on [Earthdata Search](https://search.earthdata.nasa.gov/search?fi=OCI),
directly under the collection name, after clicking on the "i" button for a collection in any search result.

</div>

Next, we use the `search_data` function (as opposed to `search_datasets`) to
find granules within a collection. Let's use the `short_name` for the PACE/OCI Level-2
near real time (NRT) product for biogeochemical properties (although you can
search for granules accross collections too).

The `count` argument limits the number of granule records that are returned in the search results.

```{code-cell}
results = earthaccess.search_data(
    short_name="PACE_OCI_L2_BGC_NRT",
    count=1,
)
```

Displaying results shows the direct download link (try it!), along
with a "quick-look" of some variable within the granule. The
link will download the granule to your local machine, which may or
may not be what you want to do. Even if you are running the notebook
on a remote host, this download link will open a new browser tab or
window and offer to save a file to your local machine. If you are
running the notebook locally, this may be of use. More likely, you
want to open or download the granules by following the steps below.

```{code-cell}
results[0]
```

We can refine our search by passing more parameters that describe
the spatiotemporal domain of our use case. Here, we use the
`temporal` parameter to request a date range and the `bounding_box`
parameter to request granules that intersect with a bounding box. We
can even provide a `cloud_cover` threshold to limit files that have
a lower percetnage of cloud cover. We do not provide a `count`, so
we'll get all granules that satisfy the constraints.

```{code-cell}
tspan = ("2024-05-01", "2024-05-16")
bbox = (-76.75, 36.97, -75.74, 39.01)
clouds = (0, 50)
```

```{code-cell}
results = earthaccess.search_data(
    short_name="PACE_OCI_L2_BGC_NRT",
    temporal=tspan,
    bounding_box=bbox,
    cloud_cover=clouds,
)
```

```{code-cell}
results[0]
```

```{code-cell}
results[1]
```

```{code-cell}
results[2]
```

[back to top](#Contents)

+++

## 4. Open Data

The results returned by `earthaccess.search_data` are just catalog entries, but include
links to the data that we are able to access with `xarray`. The `earthaccess.open` function
is used when you want to directly load data from a remote filesystem without downloading whole granules.
When running code on a host with direct access to the NASA Earthdata Cloud, you don't need to download
the granule and `earthaccess.open` is the way to go.

Here is another search, this time for Level-3 granules from a single day, followed by `earthaccess.open`
on the `results` list.

```{code-cell}
results = earthaccess.search_data(
    short_name="PACE_OCI_L3M_CHL_NRT",
    temporal=("2024-06-01", "2024-06-01"),
)
paths = earthaccess.open(results)
```

The list of outputs, which we called `paths`, contains references to files on a remote filesystem. They're not
paths to a local file, but many utilities that expect a file path can also use these "file-like" paths.

```{code-cell}
paths
```

<div class="alert alert-danger" role="alert">

The string "ob-cumulus-prod-public" is the name of an AWS S3 bucket in the "us-west-2" region. If you don't see
that string in the output above, then `earthaccess` has determined that you do not have
direct access to the NASA Earthdata Cloud.

</div>

+++

Despite not having downloaded these granules, we can now access their content with `xarray`. As always,
the `xarray` package does "lazy loading", so only coordinates are loaded until the daa variables are
actually needed.

```{code-cell}
dataset = xr.open_dataset(paths[0])
dataset
```

Even if you only want to read a slice of the data, and downloading
seems unncessary, if you use `earthaccess.open` while not running on
a remote host with direct access to the NASA Earthdata Cloud,
performance will be very poor. This is not a problem with the
cloud or with `earthaccess`, it has to do with the data format and
may soon be improved.

For one reason or another, you also need to know how to download whole granules
to the local or remote host running your code.

+++

## 5. Download Data

When you do not have direct access to the Earthdata Cloud, you'll want to download the data. You may also
want to download a granule for faster reads while you are learning your way around the files. Rather
than `earthaccess.open` we call `earthaccess.download` on the same search results.

For this function, provide the list returned by `earthaccess.search_data`
along with a directory for `earthaccess` to use for the downloads.

```{code-cell}
paths = earthaccess.download(results, local_path="granules")
```

The `paths` list now contains paths to actual files.

```{code-cell}
paths
```

We can open one of these downnloaded files in just the same way with `xarray`.

```{code-cell}
dataset = xr.open_dataset(paths[0])
dataset
```

<div class="alert alert-block alert-warning">

Anywhere in any of [these notebooks](https://oceancolor.gsfc.nasa.gov/resources/docs/tutorials/) where `paths = earthaccess.open(...)` is used to read data directly from the NASA Earthdata Cloud, you need to substitute `paths = earthaccess.download(..., local_path)` before running the notebook on a local host or a remote host that does not have direct access to the NASA Earthdata Cloud.

</div>

+++

[back to top](#Contents)

<div class="alert alert-info" role="alert">

You have completed the notebook on downloading and opening datasets. We now suggest starting the notebook on "File Structure at Three Processing Levels".

</div>
