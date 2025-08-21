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

# File Structure at Three Processing Levels for the Ocean Color Instrument (OCI)

**Authors:** Anna Windle (NASA, SSAI), Ian Carroll (NASA, UMBC), Carina Poulin (NASA, SSAI)

<div class="alert alert-success" role="alert">

The following notebooks are **prerequisites** for this tutorial.

- Learn with OCI: [Data Access][oci-data-access]

</div>

<div class="alert alert-info" role="alert">

An [Earthdata Login][edl] account is required to access data from the NASA Earthdata system, including NASA ocean color data.

</div>

[edl]: https://urs.earthdata.nasa.gov/
[oci-data-access]: https://oceancolor.gsfc.nasa.gov/resources/docs/tutorials/notebooks/oci_data_access/

## Summary

In this example we will use the `earthaccess` package to access OCI Level-1B (L1B), Level-2 (L2), and Level-3-Mapped (L3M) NetCDF files and open them using `xarray`. While you can learn alot exploring the datasets in this way, be ready to refer to the full [dataset documentation][user-guides] for details about the data products and processing.

**NetCDF** ([Network Common Data Format][netcdf]) is a binary file format for storing multidimensional scientific data (variables). It is optimized for array-oriented data access and support a machine-independent format for representing scientific data. Files ending in `.nc` are NetCDF files.

**XArray** is a [package][xarray] that supports the use of multi-dimensional arrays in Python. It is widely used to handle Earth observation data, which often involves multiple dimensions — for instance, longitude, latitude, time, and channels/bands.

[netcdf]: https://www.unidata.ucar.edu/software/netcdf/
[user-guides]: https://oceancolor.gsfc.nasa.gov/resources/docs/technical/#UG
[xarray]: https://docs.xarray.dev/

## Learning Objectives

At the end of this notebok you will know:
* How to find groups in a NetCDF file
* How to use `xarray` to open OCI data
* What key variables are present in the groups within OCI L1B, L2, and L3M files

## Contents

1. [Setup](#1.-Setup)
2. [Explore L1B File Structure](#2.-Explore-L1B-File-Structure)
3. [Explore L2 File Structure](#3.-Explore-L2-File-Structure)
4. [Explore L3M File Structure](#4.-Explore-L3M-File-Structure)

+++

## 1. Setup

Begin by importing all of the packages used in this notebook. If your kernel uses an environment defined following the guidance on the [tutorials] page, then the imports will be successful.

[tutorials]: https://oceancolor.gsfc.nasa.gov/resources/docs/tutorials

```{code-cell} ipython3
import cartopy.crs as ccrs
import earthaccess
import h5netcdf
import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
import xarray as xr
```

Set (and persist to your user profile on the host, if needed) your Earthdata Login credentials.

```{code-cell} ipython3
auth = earthaccess.login(persist=True)
```

[back to top](#Contents)

+++

## 2. Explore L1B File Structure

Let's use `xarray` to open up a OCI L1B NetCDF file using `earthaccess`. We will use the same search method used in <a href="oci_data_access.html">OCI Data Access</a>. Note that L1B files do not include cloud coverage metadata, so we cannot use that filter.

```{code-cell} ipython3
tspan = ("2024-05-01", "2024-05-07")
bbox = (-76.75, 36.97, -75.74, 39.01)
```

```{code-cell} ipython3
results = earthaccess.search_data(
    short_name="PACE_OCI_L1B_SCI",
    temporal=tspan,
    bounding_box=bbox,
)
paths = earthaccess.open(results)
```

We want to know whether we are running code on a remote host with direct access to the NASA Earthdata Cloud.
If without direct access, consider the substitution explained in the [Data Access][data-access] notebook to download granules.

[data-access]: https://oceancolor.gsfc.nasa.gov/resources/docs/tutorials/notebooks/oci-data-access/

+++

<div class="alert alert-danger" role="alert">

If you see `HTTPFileSystem` in the output when you display `paths`, then `earthaccess` has determined that you do not have direct access to the NASA Earthdata Cloud.
Note, at present, it may be [wrong](https://github.com/nsidc/earthaccess/issues/231).

</div>

```{code-cell} ipython3
:tags: [remove-cell]

# this cell is tagged to be removed from HTML renders,
# but we currently want to download when we don't have direct access
if not earthaccess.__store__.in_region:
    paths = earthaccess.download(results, "granules")
```

Let's open the first file of the L1B files list:

```{code-cell} ipython3
dataset = xr.open_dataset(paths[0])
dataset
```

Notice that this `xarray.Dataset` has nothing but "Attributes".
Instead of an `xarray.Dataset`, we want an `xarray.DataTree` to open NetCDF files that define more than one group of variable.
These "Groups" are *almost* equivalent to an `xarray.Dataset`, the difference is that a group can also contain another group!

```{code-cell} ipython3
datatree = xr.open_datatree(paths[0])
datatree
```

Now you can view the Dimensions, Coordinates, and Variables of each group.
To show/hide any category, like "Groups", toggle the drop-down arrow.
To show/hide attributes, press the piece-of-paper icon on the right hand side of a variable.
To show/hide data representation, press the stacked-cylinders icon.
For instance, you could check the attributes on "rhot_blue" to see that this variable is the "Top of Atmosphere Blue Band Reflectance".

The dimensions of the "rhot_blue" variable are ("blue_bands", "number_of_scans", "ccd_pixels"), and it has shape (119, 1709, 1272).
The `sizes` attribute of a variable gives us that information as a dictionary.

```{code-cell} ipython3
datatree["observation_data"]["rhot_blue"].sizes
```

Let's plot the reflectance at postion 100 in the "blue_bands" dimension.

```{code-cell} ipython3
plot = datatree["observation_data"]["rhot_blue"].sel({"blue_bands": 100}).plot()
```

[back to top](#Contents)

+++

## 3. Explore L2 File Structure

OCI L2 files include retrievals of geophysical variables, such as Apparent Optical Properties (AOP), for each L1 swath. We'll use the same `earthaccess` search for L2 AOP data. Although now we can use `cloud_cover` too.

```{code-cell} ipython3
clouds = (0, 50)
results = earthaccess.search_data(
    short_name="PACE_OCI_L2_AOP",
    temporal=tspan,
    bounding_box=bbox,
    cloud_cover=clouds,
)
paths = earthaccess.open(results)
```

Let's look at the "geophysical_data" group, which is a new group generated by the level 2 processing, and the "Rrs" variable in particular.

```{code-cell} ipython3
:tags: [remove-cell]

# this cell is tagged to be removed from HTML renders,
# but we currently want to download when we don't have direct access
if not earthaccess.__store__.in_region:
    paths = earthaccess.download(results, "granules")
```

```{code-cell} ipython3
datatree = xr.open_datatree(paths[0])
rrs = datatree["geophysical_data"]["Rrs"]
rrs
```

```{code-cell} ipython3
rrs.sizes
```

The Rrs variable has 172 values in the `wavelength_3d`; the blue, red, and SWIR wavelengths have been combined.
Note that `wavelength_3d` is one of the dimensions, but also that the `Rrs` variable doesn't have any "Coordinates" or "Indexes".
Indices let us look up positions in an array by the value of it's coordinates, so we need to dig more variables out of this L2 file.
The coordinates variable for `wavelength_3d` is in the "sensor_band_parameters" group.
When we add this variable to the `rrs` array, `xarray` creates the corresponding index.

```{code-cell} ipython3
rrs["wavelength_3d"] = datatree["sensor_band_parameters"]["wavelength_3d"]
rrs
```

Now that `wavelength_3d` shows up under "Coordinates" and "Indexes" we can reference wavelengths by value.

```{code-cell} ipython3
plot = rrs.sel({"wavelength_3d": 440}).plot(cmap="viridis", robust=True)
```

The scene is being plotted using `number_of_lines` and `pixels_per_line` as "x" and "y", respectively.
We need to add more coordinates, the latitude and longitude, for a true map.
These coordinates variables are in the "navigation_data" group.

```{code-cell} ipython3
for item in ("longitude", "latitude"):
    rrs[item] = datatree["navigation_data"][item]
rrs
```

Although we now have coordinates, they won't immediately help because the data are not gridded by latitude and longitude.
L2 data come in the original instrument swath and have not been resampled to a regular grid.
That is why latitude and longitude are two-dimensional coordinates, and why the are not also "Indexes" like `wavelength_3d`.
Latitude and longitude are present, but cannot be used immediately to look up values like you can with coordinates that are also indices.

Let's make a scatter plot of some pixel locations so we can see the irregular spacing of latitude and longitude.
By selecting a `slice` with a step size larger than one, we get a subset of the locations for better visualization.

```{code-cell} ipython3
plot = datatree["navigation_data"].sel(
    {
        "number_of_lines": slice(None, None, 1720 // 20),
        "pixels_per_line": slice(None, None, 1272 // 20),
    },
).dataset.plot.scatter(x="longitude", y="latitude")
```

Despite not having indices, let's plot `Rrs` the same way as before, except for the addition of latitude and longitude.

```{code-cell} ipython3
rrs_sel = rrs.sel({"wavelength_3d": 440})
plot = rrs_sel.plot(x="longitude", y="latitude", cmap="viridis", robust=True)
```

Plotting tools can handle non-index Coordinates!
You can even visualize the data as if projected onto a grid.
If you wanna get fancy, add a coastline.

```{code-cell} ipython3
fig, ax = plt.subplots(subplot_kw={"projection": ccrs.PlateCarree()})
im = rrs_sel.plot(x="longitude", y="latitude", cmap="viridis", robust=True, ax=ax)
ax.gridlines(draw_labels={"left": "y", "bottom": "x"})
ax.coastlines()
plt.show()
```

Let's plot the full "Rrs" spectrum for individual pixels.
A visualization with all the pixels wouldn't be useful, but limiting to a bounding box gives a simple way to subset pixels.
Note that, since we don't have gridded data (i.e. our latitude and longitude coordinates are two-dimensional), we can't `slice` on these values.
Without getting into anything complex, we will use a `where` with logical tests.

```{code-cell} ipython3
rrs_box = rrs.where(
    (
        (rrs["latitude"] > 26.0)
        & (rrs["latitude"] < 26.1)
        & (rrs["longitude"] > -84.1)
        & (rrs["longitude"] < -84.0)
    ),
    drop=True,
)
rrs_box.sizes
```

The line plotting method will only draw a line plot for 1D data, which we can get by stacking
our two spatial dimensions and choosing to show the new "pixel dimension" in different hues.

```{code-cell} ipython3
rrs_stack = rrs_box.stack(
    {"pixel": ["number_of_lines", "pixels_per_line"]},
    create_index=False,
)
plot = rrs_stack.plot(hue="pixel", add_legend=False)
```

[back to top](#Contents)

+++

## 4. Explore L3M File Structure

At L3M there are binned (B) and mapped (M) products available.
The L3M remote sensing reflectance (Rrs) files contain global maps of the full spectra, so they can be big!
We'll use the same `earthaccess` method to find the data.

```{code-cell} ipython3
results = earthaccess.search_data(
    short_name="PACE_OCI_L3M_RRS",
    temporal=tspan,
)
len(results)
```

The L3M collections contain granules at different temporal and spatial resolutions.
Let's take a closer look at one of the smaller sized results first, using the metadata available on each one's size.

```{code-cell} ipython3
for item in results:
    if item.size() > 2000:
        display(item)
        break
```

Notice some special parts in the granule name:
1. Right after `L3m` you have a temporal resolution marker.
   The value `DAY` means a daily aggregate, `8D` means an 8-day aggregate, and `MO` means monthly aggregates.
1. Right after `chlor_a` you have a spatial resolution marker, as horizontal cell size at the equator given either in `km` or `deg`. Read `p` as a decimal point.

Within a specific collection, `earthaccess` can retrieve granules whose name matches a pattern given in the `granule_name` argument.
Let's use that to narrow our search to values aggregated to a month and 0.1 degree resolutions.

```{code-cell} ipython3
results = earthaccess.search_data(
    short_name="PACE_OCI_L3M_RRS",
    granule_name="*.MO.*.4km.*",
    temporal=tspan,
)
len(results)
```

```{code-cell} ipython3
paths = earthaccess.open(results)
```

```{code-cell} ipython3
:tags: [remove-cell]

# this cell is tagged to be removed from HTML renders,
# but we currently want to download when we don't have direct access
if not earthaccess.__store__.in_region:
    paths = earthaccess.download(results, "granules")
```

L3M data do not have any groups, so we can open as a dataset rather than a datatree.

```{code-cell} ipython3
dataset = xr.open_dataset(paths[0])
dataset
```

Notice that this L3M granule has `wavelength`, `lat`, and `lon` under "Indexes", so it's easy to slice
out a bounding box and map the "Rrs" variable at a given wavelength.

```{code-cell} ipython3
rrs = dataset["Rrs"]
rrs_440_bbox = rrs.sel({
    "wavelength": 440,
    "lat": slice(bbox[3], bbox[1]),
    "lon": slice(bbox[0], bbox[2]),
})
rrs_440_bbox
```

```{code-cell} ipython3
fig, ax = plt.subplots(subplot_kw={"projection": ccrs.PlateCarree()})
im = rrs_440_bbox.plot(x="lon", y="lat", cmap="viridis", robust=True, ax=ax)
ax.gridlines(draw_labels={"left": "y", "bottom": "x"})
ax.coastlines()
plt.show()
```

Also becuase the L3M variables have gridded `lat` and `lon` coordinates, it's possible to stack multiple granules along a new dimension that corresponds to time.
Using the `granule_name` filter, let's get low spatial-resolution chlorophyll-a data to see daily changes.

```{code-cell} ipython3
results = earthaccess.search_data(
    short_name="PACE_OCI_L3M_CHL",
    temporal=tspan,
    granule_name="*.DAY.*.0p1deg.*",
)
paths = earthaccess.open(results)
```

```{code-cell} ipython3
:tags: [remove-cell]

# this cell is tagged to be removed from HTML renders,
# but we currently want to download when we don't have direct access
if not earthaccess.__store__.in_region:
    paths = earthaccess.download(results, "granules")
```

Instead of `xr.open_dataset`, we use `xr.open_mfdataset` to create a single `xarray.Dataset` (the "mf" in `open_mfdataset` stands for multiple files) from an array of paths.
The `paths` list is sorted temporally by default, which means the shape of the `paths` array specifies the way we need to tile the files together into larger arrays.
We specify `combine="nested"` to combine the files according to the shape of the array of files (or file-like objects), even though `paths` is not a "nested" list in this case.
The `concat_dim="date"` argument generates a new dimension in the combined dataset, because "date" is not an existing dimension in the individual files.

```{code-cell} ipython3
dataset = xr.open_mfdataset(
    paths,
    combine="nested",
    concat_dim="date",
)
```

Add a date variable as a coordinate using the dates from the netCDF files.

```{code-cell} ipython3
dates = [xr.open_dataset(i).attrs["time_coverage_end"] for i in paths]
dt = pd.to_datetime(dates)
dataset = dataset.assign_coords(date=dt.values)
dataset
```

A common reason to generate a single dataset from multiple, daily images is to create a composite. Compare the map from a single day ...

```{code-cell} ipython3
chla = np.log10(dataset["chlor_a"])
chla.attrs.update(
    {
        "units": f'log({dataset["chlor_a"].attrs["units"]})',
    }
)
im = chla.sel(date="2024-05-02").plot(aspect=2, size=4, cmap="GnBu_r")
```

... to a map of average values, which ignore missing values due to clouds.

```{code-cell} ipython3
chla_avg = chla.mean("date", keep_attrs=True)
im = chla_avg.plot(aspect=2, size=4, cmap="GnBu_r")
```

We can also create a time series of mean values over the whole region.

```{code-cell} ipython3
chla_avg = chla.mean(dim=["lon", "lat"], keep_attrs=True)
im = chla_avg.plot(linestyle="-", marker="o", color="b")
```

[back to top](#Contents)

<div class="alert alert-info" role="alert">

You have completed the notebook on OCI file structure.

</div>
