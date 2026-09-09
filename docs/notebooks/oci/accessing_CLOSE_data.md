---
jupytext:
  text_representation:
    extension: .md
    format_name: myst
    format_version: 0.13
    jupytext_version: 1.19.5
kernelspec:
  name: python3
  display_name: Python 3 (ipykernel)
  language: python
---

# Accessing the CLOSE dataset

**Author:** Anna Windle (NASA GSFC, SSAI)

Last updated: August 12, 2026

<div class="alert alert-info" role="alert">

An [Earthdata Login][edl] account is required to access data from the NASA Earthdata system, including NASA ocean color data.

</div>

[edl]: https://urs.earthdata.nasa.gov/

## Summary

Accurate evaluation of satellite ocean color algorithms is fundamentally limited by the absence of comprehensive datasets in which the true ocean state is fully known. Here we present **CLOSE**: a **C**losed-**L**oop **O**cean **S**imulation for **E**valuation. The CLOSE dataset is provided in a realistic satellite instrument coordinate framework to support the development and assessment of retrieval algorithms for NASA’s Plankton, Aerosol, Cloud, ocean Ecosystem (PACE) mission. 

The input data includes remote sensing reflectance (Rrs(λ)), inherent optical properties (IOPs), phytoplankton community composition (PCC), and associated environmental variables derived from the NASA Ocean Biogeochemical Model (NOBM) coupled to the Ocean-Atmosphere Spectral Irradiance Model (OASIM). 

These data are used as input to the Python Top-Of-Atmosphere Simulation Tool (PyTOAST) to simulate Level-1B top-of-atmosphere radiances, which are subsequently processed to Level-2 ocean color products. This framework provides end-to-end traceability from modeled ocean variables to retrieved geophysical retrievals, providing a unique resource for robust algorithm development, validation, and uncertainty quantification. 

This openly available dataset represents the first fully closed, spatially explicit simulation of PACE-like measurements, establishing a foundation for evaluation of atmospheric correction and bio-optical (empirical and semi-analytical) methods. It is designed to accelerate algorithm development, enhance confidence in satellite-derived products, and ultimately advance global ocean biogeochemical observing capabilities. More information on the CLOSE dataset can be found in this manuscript. (link to be added)

The entire CLOSE dataset is hosted and provided free of charge through NASA Earthdata. The dataset can be accessed via the [DOI landing page](https://doi.org/10.5067/PACE/OCISIM/CLOSE) which provides links to the corresponding NASA Earthdata dataset landing pages. This tutorial will demonstrate how to access the CLOSE dataset using `earthaccess`.

## Learning Objectives

At the end of this notebook, you will know how to:
- Discover and access the CLOSE dataset using `earthaccess`
- Open CLOSE data as an `xarray` dataset
- Explore and visualize CLOSE dataset variables through plots

+++

## 1. Setup

+++

Begin by importing all of the packages used in this notebook.

```{code-cell} ipython3
import earthaccess
import matplotlib.pyplot as plt
import xarray as xr
```

Set your Earthdata Login credentials. You can add `persist=True` to save your credentials in a `.netrc` file, allowing you to authenticate automatically in the future sessions without re-entering your Earthdata credentials.

```{code-cell} ipython3
auth = earthaccess.login()
```

## 2. Availability

+++

The CLOSE dataset is available for four months: Sep 2024, Jan 2025, Mar 2025, and Jun 2025. Let's start by counting how many files exist for each month.

```{code-cell} ipython3
months = ("2024-09", "2025-01", "2025-03", "2025-06")
datasets = {
    "Model Inputs": "PACE_OCI_MI_CLOSE",
    "L1B": "PACE_OCI_L1B_CLOSE",
    "L2": "PACE_OCI_L2_CLOSE",
    "L3M": "PACE_OCI_L3M_CLOSE",
}

for m in months:
    print(m)
    for label, short_name in datasets.items():
        results = earthaccess.search_data(
            short_name=short_name,
            temporal=(m, m),
        )
        print(f"  {label}: {len(results)} files")
    print()
```

## 3. Search and access

+++

Let's search for files corresponding to a date and granule discussed in the manuscript: Granule B in Figure 1.

```{code-cell} ipython3
target = "2025-03-15 15:26:16"
files = {}
for label, short_name in datasets.items():
    results = earthaccess.search_data(
        short_name=short_name,
        temporal=(target, target),
        count=1,
    )
    files[label] = results[0]
    print(f"{label}: {files[label].data_links()[0] if files[label] else 'Not found'}")
```

```{code-cell} ipython3
paths = earthaccess.open(list(files.values()))
```

## 4. Open and plot

+++

Let's open the data using `xarray` and prepare it for subsequent analysis.

```{code-cell} ipython3
model_inputs = xr.open_dataset(paths[0])
model_inputs = model_inputs.set_coords(("longitude", "latitude"))

l1b = xr.open_datatree(paths[1])
l1b = xr.merge(l1b.to_dict().values())
l1b = l1b.set_coords(("longitude", "latitude"))

l2 = xr.open_datatree(paths[2])
l2 = xr.merge(l2.to_dict().values())
l2 = l2.set_coords(("longitude", "latitude"))

l3m = xr.open_dataset(paths[3])
```

We can plot either remote sensing reflectance (Rrs) or top-of-atmopshere reflectance (rhot) from each file:

```{code-cell} ipython3
fig = plt.figure(figsize=(10, 4), constrained_layout=True)
gs = fig.add_gridspec(2, 3)

ax1 = fig.add_subplot(gs[0, 0])
ax2 = fig.add_subplot(gs[0, 1])
ax3 = fig.add_subplot(gs[0, 2])
ax4 = fig.add_subplot(gs[1, 0:3])

m1 = (
    model_inputs["Rrs"]
    .sel({"wavelength": 442}, method="nearest")
    .plot(ax=ax1, x="longitude", y="latitude", add_colorbar=True)
)
ax1.set_title("MODEL_INPUTS")

m2 = (
    l1b["rhot_blue"]
    .sel({"blue_bands": 53})
    .plot(ax=ax2, x="longitude", y="latitude", add_colorbar=True)
)
ax2.set_title("L1B")

m3 = (
    l2["Rrs"]
    .sel({"wavelength_3d": 442}, method="nearest")
    .plot(ax=ax3, x="longitude", y="latitude", add_colorbar=True)
)
ax3.set_title("L2")

m4 = (
    l3m["Rrs"]
    .sel({"wavelength": 442}, method="nearest")
    .plot(ax=ax4, x="lon", y="lat", add_colorbar=True)
)
ax4.set_title("L3M")

m1.colorbar.set_label("Rrs(442) (sr⁻¹)")
m2.colorbar.set_label("Rhot(442)")
m3.colorbar.set_label("Rrs(442) (sr⁻¹)")
m4.colorbar.set_label("Rrs(442) (sr⁻¹)")

for ax in [ax1, ax2, ax3, ax4]:
    ax.set_xlabel("")
    ax.set_ylabel("")
    ax.tick_params(length=0)
    for spine in ax.spines.values():
        spine.set_visible(False)

pos = ax4.get_position()
ax4.set_position([pos.x0 + 0.05, pos.y0 - 0.07, pos.width, pos.height])

# shift colorbar
cbar = m4.colorbar
cbar.ax.set_position(
    [
        cbar.ax.get_position().x0 + 0.05,
        cbar.ax.get_position().y0 - 0.07,
        cbar.ax.get_position().width,
        cbar.ax.get_position().height,
    ]
)

plt.show()
```

## 5. Closing the loop on chlorophyll a

+++

By providing known “truth” fields in native satellite geometry, CLOSE offers a powerful testbed for atmospheric correction, bio-optical inversion, and emerging machine learning approaches.

Here is an example of comparing input `chlor_a` (derived mechanistically from NOBM) to output `chlor_a` derived from NASA OB.DAAC ([Chl a ATBD](https://oceancolor.gsfc.nasa.gov/files/atbd/atbd-obdaac-chlorophyll-a.pdf)).

```{code-cell} ipython3
plot = model_inputs["chlor_a"].plot.hist(
    bins=50,
    range=[0.007, 0.4],
    alpha=0.4,
    label="MODEL_INPUTS",
    color="blue",
)

plot = l2["chlor_a"].plot.hist(
    bins=50,
    range=[0.007, 0.4],
    alpha=0.4,
    label="L2",
    color="red",
)

median_model_inputs_chl = model_inputs["chlor_a"].median()
median_l2_chl = l2["chlor_a"].median()

plt.axvline(
    median_model_inputs_chl,
    color="blue",
    linewidth=2,
    label=f"MODEL_INPUTS median = {median_model_inputs_chl:.2f}",
)
plt.axvline(
    median_l2_chl,
    color="red",
    linestyle="--",
    linewidth=2,
    label=f"L2 median = {median_l2_chl:.2f}",
)

plt.xlabel("chlorophyll a (mg m$^{-3}$)", fontsize=10)
plt.ylabel("Frequency", fontsize=10)

plt.legend(frameon=False)
plt.show()
```

Overall, Chl a distributions are similar, with only slight differences in their medians. This example evaluates the standard Chl a algorithm, but it could be replaced with any alternative algorithm to assess how well its output compares to the input (“truth”) Chl a. The same approach can be applied to other data products as well.

+++

<div class="alert alert-info" role="alert">

You have completed the notebook on "Accessing the CLOSE Dataset"!

</div>
