---
jupytext:
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

# Science Data Reprocessing and Product Versions

**Authors:** Anna Windle (NASA, SSAI), Ian Carroll (NASA, UMBC)

<div class="alert alert-success" role="alert">

The following notebooks are **prerequisites** for this tutorial.

- Learn with OCI: [Data Access](oci-data-access)

</div>

<div class="alert alert-info" role="alert">

An [Earthdata Login][edl] account is required to access data from the NASA Earthdata system, including NASA ocean color data.

</div>

[edl]: https://urs.earthdata.nasa.gov/

## Summary

Satellite data are periodically [reprocessed](https://oceancolor.gsfc.nasa.gov/data/reprocessing/) to incorporate improvements in sensor calibration, atmospheric correction, retrieval algorithms, and ancillary datasets, as well as to correct known processing issues. Reprocessing produces a more accurate and internally consistent data record, ensuring that changes over time reflect real environmental variability rather than differences in processing methods.

The initial public release of PACE science data products (**Version 1**) began on 11 April 2024,
and provided the science and applications user community with access to the Level-1 data
and a limited suite of derived products from the OCI, HARP2, and SPEXone instruments,
with the caveat that the data were in a highly preliminary state and should be used with
caution. Reprocessing **Version 2** was the first full mission reprocessing, and primarily
served to incorporate improved calibration knowledge from on-orbit measurements
collected by the three PACE instruments. Reprocessing **Version 3** included a further
refinement of the calibration for the three instruments, as well as various algorithm
refinements, bug fixes, data format improvements, and expanded product suites. 

In April 2026, PACE OCI **Version 3.2** was released. This reprocessing primarily corrected an implementation error in the bidirectional reflectance distribution function (BRDF) correction applied to spectral remote-sensing reflectance (Rrs), and also included updated vicarious calibration and several minor processing improvements. The NetCDF file structure was also updated as part of this release.

**This tutorial highlights the key file structure changes introduced in Version 3.2 and demonstrates how to update existing workflows developed for Version 3.1. As Version 3.1 data are phased out, these approaches will become the standard for accessing and analyzing PACE OCI data. Future reprocessing campaigns, including Version 4, are expected to introduce additional file structure changes, which will be communicated to the PACE user community.**


## Learning Objectives

At the end of this notebook you will know:

- The differences in OCI L2 file structure between Version 3.1 and 3.2
- How to open v3.1 and v3.2 data with `xarray`
- Updates to OCI v3.2 L3M file names
- Status of PACE OCI land data products

+++

## 1. Setup

+++

Begin by importing all of the packages used in this notebook. If you followed the guidance on the [Getting Started](/getting-started) page, then the imports will be successful.

```{code-cell} ipython3
from collections import defaultdict

import earthaccess
import pandas
import xarray as xr
```

To organize the collection information we'll retrieve from NASA Earthdata CMR, we need a dictionary that can automatically create nested levels as needed. We'll create a `recursivedict` that extends Python's `defaultdict` to support unlimited nesting.

```{code-cell} ipython3
recursivedict = lambda: defaultdict(recursivedict)
```

## 2. Checking Data Versions

+++

At any time, you can search for all the collections in the Earthdata Cloud distributed by the OB.DAAC
to discover the version of each one available for analysis. For short periods of time close to a reprocessing, there may be multiple versions of the same collection available simultaneously. This is always a temporary situation, but may last for a few weeks.

```{code-cell} ipython3
results = earthaccess.search_datasets(
    data_center="OBDAAC",
    cloud_hosted=True,
)
```

These results can be grouped according to their level, version, platform, and short-name.
If we build the dictionary in a particular way, then it will be simple to cast the results as a `pandas.DataFrame` for easy filtering and to display.

```{code-cell} ipython3
collections = recursivedict()
for item in results:
    metadata = item["umm"]
    level = metadata["ProcessingLevel"]["Id"]
    version = metadata["Version"]
    short_name = metadata["ShortName"]
    platform = metadata["Platforms"][0]["ShortName"]
    collections[level][version][(platform, short_name)] = "✅"

level1 = pandas.DataFrame.from_dict(collections["1"])
level2 = pandas.DataFrame.from_dict(collections["2"])
```

### Level-1

+++

The Level-1 collections, the least processed data observed at the top-of-atmosphere, only have a major version number.
Reprocessings that increase a version number at Level-1 will lead to reprocessings for higher processing levels.

```{code-cell} ipython3
level1.fillna("").sort_index(axis=0).sort_index(axis=1)
```

### Level-2

+++

Subset the `level2` data frame to display level-2 data collections for a single platform, e.g. PACE.

```{code-cell} ipython3
level2_pace = level2.loc[("PACE", ...)].dropna(axis=1, how="all").fillna("")
level2_pace.sort_index(axis=0).sort_index(axis=1)
```

## 3. Release Note Highlights

+++

### Version 3

+++

Note that all product suites are not necessarily at the same version. This is because a reprocessing will only be performed on the products actually impacted by improvements to processing algorithms.

For instance, the surface reflectance (SRFEFL) and land surface indices (LANDVI) products remained at version 3.1 while the ocean color suites were upgraded to version 3.2

+++

#### Version 3.2

+++

Read the [April 2026 release notes for Version 3][3.2], and note the following highlights.

[3.2]: https://oceancolor.gsfc.nasa.gov/files/data/reprocessing/V3/PACE_OCI_V3_Release_Notes.pdf

+++

<div class="alert alert-warning" role="alert">

Starting with version 3.2, NASA now packages all ocean color measurements (like RRS, nFLH, and AVW) together in a single Level-3 data product called AOP, instead of distributing each measurement type as a separate download.

</div>

+++

The NASA Earthdata CMR `short_names` changed for Level-3 products. The new `short_names` for PACE OCI Level-3 mapped products are:
- `PACE_OCI_L3M_AOP`
- `PACE_OCI_L3M_IOP`
- `PACE_OCI_L3M_BGC`
- `PACE_OCI_L3M_KD`
- `PACE_OCI_L3M_PAR`

You can use the following dictionary to replace non-existent short names with the consolidated products:

```{code-cell} ipython3
# FIXME: get all of these if useful?
rename = {
    "PACE_OCI_L3M_CHL": "PACE_OCI_L3M_BGC",
    "PACE_OCI_L3M_RRS": "PACE_OCI_L3M_AOP",
    "PACE_OCI_L3M_AVW": "PACE_OCI_L3M_AOP",
    "PACE_OCI_L3M_FLH": "PACE_OCI_L3M_AOP",
    "PACE_OCI_L3M_CARBON": "PACE_OCI_L3M_BGC",
}
rename["PACE_OCI_L3M_RRS"]
```

<div class="alert alert-warning" role="alert">

The wavelength coordinate variables have been adjusted to better distinguish between the nominal wavelengths that use integer values and the actual wavelengths used for the geophysical variables. However, running some code that works for previous versions may generate erros or even crash your notebook kernel.

</div>

+++

<!---
earthaccess.login()
results = earthaccess.search_data(
    short_name="PACE_OCI_L2_AOP",
    version="3.2",
    count=1,
)
path = earthaccess.open(results).pop()
datatree = xr.open_datatree(path)
print(datatree)
-->

If you have a `datatree` returned by `xarray.open_datatree` applied to a level-2 collection at version 3.2, then an (abridged) output from `print(datatree)` would look like:
```python
<xarray.DataTree>
Group: /
│   Attributes: (12/47)
│       title:                             OCI Level-2 Data AOP
│       processing_version:                3.2
├── Group: /geophysical_data
│       Dimensions:     (wavelength: 172, number_of_lines: 1710, pixels_per_line: 1272)
│       Coordinates:
│         * wavelength  (wavelength) float32 688B 346.0 348.5 350.9 ... 716.8 719.3
│       Data variables:
│           band_index  (wavelength) float64 1kB ...
│           Rrs         (number_of_lines, pixels_per_line, wavelength) float32 1GB ...
│           Rrs_unc     (number_of_lines, pixels_per_line, wavelength) float32 1GB ...
│           aot_865     (number_of_lines, pixels_per_line) float32 9MB ...
│           angstrom    (number_of_lines, pixels_per_line) float32 9MB ...
│           avw         (number_of_lines, pixels_per_line) float32 9MB ...
│           nflh        (number_of_lines, pixels_per_line) float32 9MB ...
│           l2_flags    (number_of_lines, pixels_per_line) int32 9MB ...
├── Group: /navigation_data
│       Dimensions:    (number_of_lines: 1710, pixels_per_line: 1272)
│       Data variables:
│           longitude  (number_of_lines, pixels_per_line) float32 9MB ...
│           latitude   (number_of_lines, pixels_per_line) float32 9MB ...
│           tilt       (number_of_lines) float32 7kB ...
├── Group: /sensor_band_parameters
│       Dimensions:        (wavelength: 286, number_of_reflective_bands: 286, wavelength_3d: 172)
│       Coordinates:
│         * wavelength     (wavelength) float64 2kB 315.0 316.0 ... 2.131e+03 2.258e+03
│         * wavelength_3d  (wavelength_3d) float64 1kB 346.0 348.0 351.0 ... 717.0 719.0
├── Group: /scan_line_attributes
└── Group: /processing_control
```

The `geophysical_data` group includes `wavelength` as a coordinate. The addition of `wavelength` as a coordinate within the same group makes it easier to select and work with spectrally resolved variables. Although the same length, the array of values in `/geophysical_data/wavelength` differs from that in `/sensor_band_parameters/wavelength_3d`. The latter, integer valued, variable gives the nominal wavelengths associated with each band pre-launch.

To work with a variable from the `geophysical_data` group, since it already contains a `wavelength` coordinate, we only need to add the "latitude" and longitude variables from the `navigation_data` group.

<!--
dataarray = datatree["geophysical_data"]["Rrs"]
for variable in ("longitude", "latitude"):
    dataarray[variable] = datatree["navigation_data"][variable]
print(dataarray)
-->
```python
dataarray = datatree["geophysical_data"]["Rrs"]
for variable in ("longitude", "latitude"):
    dataarray[variable] = datatree["navigation_data"][variable]
```

Now `print(dataarray)` will show the "Rrs" variable has coordinates associated with all three dimensions, although only "wavelength" is an indexed dimension.
```
<xarray.DataArray 'Rrs' (number_of_lines: 1709, pixels_per_line: 1272, wavelength: 172)>
[373901856 values with dtype=float32]
Coordinates:
    longitude   (number_of_lines, pixels_per_line) float32 9MB ...
    latitude    (number_of_lines, pixels_per_line) float32 9MB ...
  * wavelength  (wavelength) float32 688B 346.0 348.5 350.9 ... 716.8 719.3
```

Alternatively, you can "revert" to something that may work with code writted for a version 3.1 dataset.
You can drop the `wavelength` dimension from the `sensor_band_parameters` group on a `datatree` created
from a version 3.2 products:

```python
datatree["sensor_band_parameters"] = datatree["sensor_band_parameters"].ds.drop_dims("wavelength")
```

Code previously developed for the version 3.1 structure, such as `xr.merge(datatree.to_dict().values())` will now work and yield the same `wavelength_3d` coordinate.

+++

#### Version 3.1

+++

Read the [full release notes](https://oceancolor.gsfc.nasa.gov/files/data/reprocessing/V3/PACE_Reprocessing_V3.x_notes.pdf), and check out these highlights.

+++

<!---
results = earthaccess.search_data(
    short_name="PACE_OCI_L2_SFREFL",
    version="3.1",
    count=1,
)
path = earthaccess.open(results).pop()
datatree = xr.open_datatree(path)
print(datatree)
-->

If you have a `datatree` returned by `xarray.open_datatree` applied to a level-2 collection at version 3.1, then an (abridged) output from `print(datatree)` would look like:
```
<xarray.DataTree>
Group: /
│   Attributes: (12/47)
│       title:                             OCI Level-2 Data SFREFL
│       processing_version:                3.1
├── Group: /geophysical_data
│       Dimensions:   (number_of_lines: 1709, pixels_per_line: 1272, wavelength_3d: 122)
│       Dimensions without coordinates: number_of_lines, pixels_per_line, wavelength_3d
│       Data variables:
│           rhos      (number_of_lines, pixels_per_line, wavelength_3d) float32 1GB ...
│           l2_flags  (number_of_lines, pixels_per_line) int32 9MB ...
├── Group: /navigation_data
│       Dimensions:    (number_of_lines: 1709, pixels_per_line: 1272)
│       Dimensions without coordinates: number_of_lines, pixels_per_line
│       Data variables:
│           longitude  (number_of_lines, pixels_per_line) float32 9MB ...
│           latitude   (number_of_lines, pixels_per_line) float32 9MB ...
│           tilt       (number_of_lines) float32 7kB ...
│       Attributes:
│           gringpointlongitude:  [ 172.73434 -158.38428 -158.936    162.20712]
│           gringpointlatitude:   [32.255096 37.779976 55.533276 48.957504]
│           gringpointsequence:   [1 2 3 4]
├── Group: /sensor_band_parameters
│       Dimensions:        (number_of_bands: 286, number_of_reflective_bands: 286, wavelength_3d: 122)
│       Coordinates:
│         * wavelength_3d  (wavelength_3d) float64 976B 346.0 351.0 ... 2.258e+03
│       Data variables:
│           wavelength     (number_of_bands) float64 2kB ...
│           vcal_gain      (number_of_reflective_bands) float32 1kB ...
│           vcal_offset    (number_of_reflective_bands) float32 1kB ...
│           F0             (number_of_reflective_bands) float32 1kB ...
│           aw             (number_of_reflective_bands) float32 1kB ...
│           bbw            (number_of_reflective_bands) float32 1kB ...
│           k_oz           (number_of_reflective_bands) float32 1kB ...
│           k_no2          (number_of_reflective_bands) float32 1kB ...
│           Tau_r          (number_of_reflective_bands) float32 1kB ...
├── Group: /scan_line_attributes
└── Group: /processing_control
```

+++

The `sensor_band_parameters` group contains a `wavelegnth_3d` coordinate with the same length as the `wavelength_3d` dimension in the `geophysical_data` group. The groups within the whole `datatree` can be merged, so that this variable becomes the coordinate for everything in the `geophysical_data` group.

```python
dataset = xr.merge(datatree.to_dict().values())
```

We can also then set the latitude and longitude variables as coordinates for mapping.
```python
dataset = dataset.set_coords(("longitude", "latitude"))
```

+++

### Version 2

+++

TODO: anything about V2? can we find release notes?
