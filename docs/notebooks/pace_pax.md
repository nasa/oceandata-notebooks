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

# Visualize PACE-PAX Data

+++

**Authors:** Anna Windle (NASA, SSAI) <br>
Adapted from code developed by: Ivona Cetinić (NASA, MSU), Kirk Knobelspiesse (NASA)

Last updated: October 28, 2026

<div class="alert alert-success" role="alert">

The following notebooks are **prerequisites** for this tutorial.

- Learn with OCI: [Data Access](oci-data-access)
</div>

<div class="alert alert-info" role="alert">

An [Earthdata Login][edl] account is required to access data from the NASA Earthdata system, including NASA ocean color data.

</div>

[edl]: https://urs.earthdata.nasa.gov/

## Summary

The PACE Postlaunch Airborne eXperiment ([PACE-PAX](https://pace.oceansciences.org/pace-pax.htm)) was a field campaign conducted in September 2024 in California and adjacent coastal areas. PACE-PAX brought together airborne and ship-based in situ observations to collect complementary atmospheric and oceanic measurements for the validation of observations from NASA's PACE mission.

All [PACE-PAX datasets](https://www.earthdata.nasa.gov/data/projects/pace-pax) are publicly available through the NASA Earthdata Cloud. This tutorial demonstrates how to access multiple PACE-PAX datasets, combine observations from different platforms, and create integrated visualizations to explore coupled atmosphere–ocean processes. This tutorial generates a multi-platform figure corresponding to Figure 9 in [Knobelspiesse et al. (in review)](https://doi.org/10.5194/essd-2026-541).

We will use the `seabass-utils` Python library to read in some of the PACE-PAX data. The SeaWiFS Bio-optical Archive and Storage System [(SeaBASS)](sb) is a public archive of in situ oceanographic and atmospheric data maintained by the Ocean Biology Processing Group (OBPG) at NASA Goddard Space Flight Center (GSFC). `seabass-utils` is a collection of Python functions, also developed by the OBPG, to assist with SeaBASS data processing, file manipulation, and mapping tasks.

[sb]: https://seabass.gsfc.nasa.gov/

## Learning Objectives

At the end of this notebook you will be able to:

- Access PACE-PAX datasets from the NASA Earthdata Cloud
- Read and explore PACE-PAX datasets from SeaBASS
- Combine observations from multiple platforms into a single data fusion visualization
- Explore coupled atmosphere–ocean observations collected during PACE-PAX

+++

## 1. Setup

+++

Begin by importing all of the packages used in this notebook. If you followed the guidance on the [Getting-Started](/getting-started) page, then the imports will be successful.

```{code-cell} ipython3
import cartopy.crs as ccrs
import earthaccess
import matplotlib.pyplot as plt
import pandas as pd
import plotly.graph_objects as go
import plotly.io as pio
import seabass_utils as sb
import xarray as xr
```

Set your Earthdata Login credentials. You can add `persist=True` to save your credentials in plain text in a netrc file, allowing you to authenticate automatically in the future sessions without re-entering your Earthdata credentials.

```{code-cell} ipython3
auth = earthaccess.login()
```

## 2. Access PACE-OCI data

+++

Let's find a PACE-OCI Level-2 Inherent Optical Property (IOP) granule acquired during the PACE-PAX campaign over the Santa Barbara Channel, California. The IOP suite contains particulate backscattering data.

```{code-cell} ipython3
tspan = ("2024-09-26", "2024-09-26")
bbox = (-120, 33, -110, 35)
results = earthaccess.search_data(
    short_name="PACE_OCI_L2_IOP",
    temporal=tspan,
    bounding_box=bbox,
)
len(results)
```

```{code-cell} ipython3
oci_paths = earthaccess.open(results)
```

We can open this file up using `xarray` and retrieve particulate backscattering at 442 nm data (`bbp_442`):

```{code-cell} ipython3
oci_dt = xr.open_datatree(oci_paths[-1])
oci_bbp = oci_dt["geophysical_data"]["bbp_442"]
for item in ("longitude", "latitude"):
    oci_bbp[item] = oci_dt["navigation_data"][item]
oci_bbp
```

Let's subset the PACE-OCI `bbp_442` data to a smaller geographical region in the Santa Barbara Channel, retain only positive values, and plot it:

```{code-cell} ipython3
subset = (
    (oci_bbp["longitude"] >= -120.5)
    & (oci_bbp["longitude"] <= -119.0)
    & (oci_bbp["latitude"] >= 33.8)
    & (oci_bbp["latitude"] <= 34.5)
)
oci_bbp = oci_bbp.where(subset & (oci_bbp >= 0), drop=True)
oci_bbp.sizes
```

```{code-cell} ipython3
crs = ccrs.PlateCarree()
fig, ax = plt.subplots(figsize=(8, 6), subplot_kw={"projection": crs})

oci_bbp.plot(
    x="longitude",
    y="latitude",
    cmap="viridis",
    vmax=0.015,
    cbar_kwargs={"shrink": 0.65},
    ax=ax,
)

ax.coastlines(resolution="10m", linewidth=1)
ax.gridlines(
    draw_labels={"bottom": True, "left": True, "top": False, "right": False},
    xlocs=plt.MaxNLocator(5),
    ylocs=plt.MaxNLocator(5),
    linewidth=0,
)

plt.tight_layout()
plt.show()
```

Higher `bbp_442` values are observed along the coast, indicating greater particulate backscattering and potentially higher particle concentrations.

+++

## 3. Access airborne optical data

+++

Now let's access data collected from one of the aircraft flown during PACE-PAX. A Twin Otter airplane from the Center for Interdisciplinary Remotely Piloted Aircraft Studies (CIRPAS) at the Naval Postgraduate School in Monterey, CA, collected data on aerosol particles in the atmosphere. We will use the aerosol backscattering coefficient at 532 nm, measured under ambient relative humidity, temperature, and pressure, represented by the variable `fine_amb_back_coef`, produced by the In Situ Aerosol Retrieval Algorithm (ISARA).

```{code-cell} ipython3
results = earthaccess.search_data(
    short_name="PACE-PAX_Analysis_ISARA_Data",
    temporal=tspan,
)
len(results)
```

```{code-cell} ipython3
isara_paths = earthaccess.open(results)
```

```{code-cell} ipython3
isara_dt = xr.open_datatree(isara_paths[-1])
isara_bbp = isara_dt["derived"]["fine_amb_back_coef"].sel({"wavelength": 532})
for item in ("longitude", "latitude", "altitude"):
    source_name = "GPS_Altitude_BUCHOLTZ" if item == "altitude" else f"{item.capitalize()}_BUCHOLTZ"
    isara_bbp[item] = isara_dt["source"][source_name]    
isara_bbp
```

Let's subset the data collected when the aircraft was flying in a spiral below 1 km:

```{code-cell} ipython3
subset = (
    (isara_bbp["longitude"] >= -120.5)
    & (isara_bbp["longitude"] <= -119.0)
    & (isara_bbp["latitude"] >= 34.1)
    & (isara_bbp["latitude"] <= 34.5)
    & (isara_bbp["altitude"] <= 1000)
)
isara_bbp = isara_bbp.where(subset, drop=True)
isara_bbp.sizes
```

And use this to plot the flight track and vertical profile:

```{code-cell} ipython3
fig, axs = plt.subplots(1, 2, figsize=(10, 4))

cmap = plt.colormaps["plasma_r"].copy()
cmap.set_bad("gray")

sc1 = axs[0].scatter(
    isara_bbp["longitude"],
    isara_bbp["latitude"],
    c=isara_bbp,
    s=20,
    cmap=cmap,
    plotnonfinite=True,
)

axs[0].set_xlabel("Longitude")
axs[0].set_ylabel("Latitude")
axs[0].set_title("Twin Otter Flight Track")
axs[0].axis("equal")

sc2 = axs[1].scatter(
    isara_bbp["longitude"],
    isara_bbp["altitude"],
    c=isara_bbp,
    s=20,
    cmap=cmap,
    plotnonfinite=True,
)

axs[1].set_xlabel("Longitude")
axs[1].set_ylabel("Altitude")
axs[1].set_title("Twin Otter Vertical Profile")

fig.colorbar(
    sc2,
    ax=axs,
    label=r"532 nm aerosol backscatter (Mm$^{-1}$ sr$^{-1}$)",
)

plt.show()
```

Note that the ISARA data are still being reprocessed, and ongoing changes may affect data validity and availability.

+++

## 4. Access airborne lidar data

+++

The High Spectral Resolution Lidar 2 (HSRL-2) instrument was flown aboard NASA's high altitude Earth Resources 2 (ER-2) aircraft to characterize atmospheric aerosol particles. We will use the aerosol backscatter coefficient measured at 532 nm.

We'll open the file containing 'R1' indicating 'Revision 1', which contains the most up-to-date data.

```{code-cell} ipython3
results = earthaccess.search_data(
    short_name="PACE-PAX_AircraftRemoteSensing_ER2_HSRL2_Data",
    temporal=tspan,
    granule_name="*R1*.h5",
)
len(results)
```

```{code-cell} ipython3
hsrl2_paths = earthaccess.open(results)
```

We will open this file using `phony_dims='sort'`. This is due to the NetCDF file containing groups or variables that reference dimensions that are not explicitly defined in the file. `phony_dims='sort'` creates phony dimensions in a sorted, more deterministic way to better reproduce NetCDF dimension behavior.

```{code-cell} ipython3
hsrl2_dt = xr.open_datatree(hsrl2_paths[-1], phony_dims='sort')
hsrl2_dt
```

We select the `532_bsc_cloud_screened` variable and manually merge the auxiliary coordinates for longitude and latitude with the `xarray.DataArray` holding the backscatter coefficient.

```{code-cell} ipython3
hsrl2_bbp = hsrl2_dt["DataProducts"]["532_bsc_cloud_screened"]
for item in ("lon", "lat"):
    hsrl2_bbp[item] = hsrl2_dt[item]
hsrl2_bbp
```

We need to subset the data to a specific geographic location, altitude, and time.
Both altitude and time are dimension coordinates, so we can extract the subset by slicing these coordinates. We restrict altitude from the surface to 1 km, and times within our time span of interest. This is a much reduced slice of the original data.

```{code-cell} ipython3
hsrl2_bbp = hsrl2_bbp.sel(
    {
        "time": slice("2024-09-26T19:32:24", "2024-09-26T19:38:24"),
        "z": slice(0, 1000),
    },
)
hsrl2_bbp.sizes
```

Since we cannot slice on any auxiliary coordinates lacking an index, we must mask the backscatter coefficients for our geographic subsetting.

```{code-cell} ipython3
subset = (
    (hsrl2_bbp["lon"] >= -120.2)
    & (hsrl2_bbp["lon"] <= -119.0)
    & (hsrl2_bbp["lat"] >= 34.1)
    & (hsrl2_bbp["lat"] <= 34.5)
)
hsrl2_bbp = hsrl2_bbp.where(subset, drop=True)
hsrl2_bbp.sizes
```

Now we are ready to visualize the lidar curtain as seen by the ER-2!

```{code-cell} ipython3
fig, ax = plt.subplots(figsize=(8, 4))

pcm = hsrl2_bbp.plot.imshow(
    x="lon",
    y="z",
    cmap="inferno_r",
    vmin=hsrl2_bbp.min(),
    vmax=hsrl2_bbp.max(),
    ax=ax,
    cbar_kwargs={"label": "532 nm Backscatter [Mm$^{-1}$ sr$^{-1}$]"}
)

ax.set_xlabel("Longitude")
ax.set_title("HSRL-2 Aerosol Backscatter Curtain")

plt.show()
```

Notice higher aerosol backscatter at lower altitudes.

+++

## 5. Access ship cast data

+++

In situ oceanic observations were collected aboard the NOAA R/V Shearwater. Particulate backscattering was measured using an SC6 backscattering sensor.

Let's open the SC6 data collected on Sep 26th:

```{code-cell} ipython3
results = earthaccess.search_data(
    short_name="PACE-PAX",
    temporal=tspan,
    granule_name="*Shearwater*SC6026*",
)
len(results)
```

These granules each reference multiple files containing data for that granule. At least one file for each granule is a plain `.sb`, rather than a `.tgz.sb`, indicating that it is a SeaBASS file.

```{code-cell} ipython3
urls = []
for item in results:
    urls += [i for i in item.data_links() if not i.endswith(".tgz.sb")]
urls
```

```{code-cell} ipython3
sc6_paths = earthaccess.open(urls)
```

SeaBASS files can be read using the `seabass_utils` library, which we imported above as `sb`. The `sb_read()` function reads the SeaBASS file into a dictionary that `pandas` converts into a `DataFrame`.

Station information is extracted from header metadata and added as `pandas.DataFrame` columns:

```{code-cell} ipython3
sc6_bbp = []

for file in sc6_paths:
    data = sb.sb_read(file, no_warn=True)
    df = pd.DataFrame(data.data)
    headers = data.headers

    lat = float(headers["north_latitude"].split("[")[0])
    lon = float(headers["east_longitude"].split("[")[0])
    date = headers["start_date"]
    time = headers["start_time"].split("[")[0]

    bbp = df[["depth", "bbp440"]].assign(
        **{
            "date": date,
            "time": time,
            "latitude": lat,
            "longitude": lon,
        }
    )
    sc6_bbp.append(bbp)

sc6_bbp = pd.concat(sc6_bbp, ignore_index=True)
sc6_bbp.head()
```

And we can now plot the vertical profiles of particulate backscattering at 440 nm (`bbp440`):

```{code-cell} ipython3
fig, ax = plt.subplots(figsize=(5, 6))

sc = ax.scatter(
    sc6_bbp["longitude"],
    sc6_bbp["depth"],
    c=sc6_bbp["bbp440"],
    s=35,
    cmap="viridis",
)

ax.invert_yaxis()
ax.set_xlabel("Longitude")
ax.set_ylabel("Depth (m)")
ax.set_title("R/V Shearwater SC6 $b_{bp}(440)$ profiles")

cbar = plt.colorbar(sc, ax=ax)
cbar.set_label("$b_{bp}(440)$ (m$^{-1}$)")

plt.tight_layout()
plt.show()
```

## 6. Access ocean glider data

+++

An autonomous ocean glider was also deployed along a 10 km transect for 25 days. The glider was equipped with a Seabird ECO Triplet optical sensor that measured particulate backscatter at 532 nm.

```{code-cell} ipython3
results = earthaccess.search_data(
    short_name="PACE-PAX",
    temporal=tspan,
    granule_name="*glider*bbp*",
)
len(results)
```

```{code-cell} ipython3
eco_paths = earthaccess.open(results)
```

We will use `sb.read()` to open this data as well:

```{code-cell} ipython3
eco_data = sb.sb_read(eco_paths[0], no_warn=True)
eco_df = pd.DataFrame(eco_data.data)
eco_df.head()
```

Let's filter out glider data for a specified date and location and keep only positive `bbp532` values:

```{code-cell} ipython3
subset = (
    (eco_df["date"] == 20240926)
    & eco_df["lon"].between(-120.5, -119.0)
    & eco_df["lat"].between(33.8, 34.5)
)

eco_bbp = eco_df.loc[subset & (eco_df["bbp532"] > 0)]
eco_bbp.shape
```

And we can plot `bbp(532)` along the glider's track as it descended and ascended throughout the day:

```{code-cell} ipython3
fig, ax = plt.subplots(figsize=(8, 5))

sc = ax.scatter(
    eco_bbp["lon"],
    eco_bbp["depth"],
    c=eco_bbp["bbp532"],
    s=15,
    cmap="viridis",
    vmax=0.004,
)

ax.invert_yaxis()
ax.set_xlabel("Longitude")
ax.set_ylabel("Depth [m]")
ax.set_title("PACE-PAX Glider $b_{bp}(532)$ on Sept 26 2024")

cbar = plt.colorbar(sc, ax=ax)
cbar.set_label("$b_{bp}(532)$ [m$^{-1}$]")

plt.tight_layout()
plt.show()
```

## 7. Muli-platform Visualization

+++

In order to make all these data visually comparable, there are couple units discrepancies to smooth out. Ocean data use depth, which we'll standardize to a "z" variable consistent with the altitude as used by airborne platforms. Both are in meters, just different conventions for positive.

```{code-cell} ipython3
sc6_bbp["z"] = -sc6_bbp["depth"]
eco_bbp["z"] = -eco_bbp["depth"]
```

The backscattering coefficients from the Twin Otter and ER-2 platforms are not the same units. We can convert the ER-2 platform's data to units of Mm$^{-1}$ sr$^{-1}$ for plotting together.

```{code-cell} ipython3
hsrl2_bbp = hsrl2_bbp * 1000
hsrl2_bbp.attrs["units"] = "Mm-1.sr-1"
```

Now, we are able to show all this data together in one 3-dimensional plot:

```{code-cell} ipython3
pio.renderers.default = "notebook"

fig = go.Figure()

ocean_cmin = 0
ocean_cmax = 0.015
atmos_cmin = 0
atmos_cmax = 4

# --- PACE ---
fig.add_trace(
    go.Surface(
        x=oci_bbp["longitude"],
        y=oci_bbp["latitude"],
        z=oci_bbp.where(oci_bbp.isnull(), 0),
        surfacecolor=oci_bbp,
        colorscale="viridis",
        showscale=True,
        opacity=0.8,
        cmin=ocean_cmin,
        cmax=ocean_cmax,
        colorbar={
            "title": {
                "text": "Ocean b<sub>bp</sub>(λ) [m⁻¹]",
                "side": "right",
                "font": {"size": 10},
            },
            "tickfont": {"size": 9},
            "x": 0.8,
            "y": 0.2,
            "len": 0.4,
            "tickvals": [0, 0.002, 0.004, 0.006, 0.008, 0.01],
            "ticktext": ["0", "0.002", "0.004", "0.006", "0.008", "0.01"],
        },
    )
)

# --- Shearwater ---
fig.add_trace(
    go.Scatter3d(
        x=sc6_bbp["longitude"],
        y=sc6_bbp["latitude"],
        z=sc6_bbp["z"],
        mode="markers",
        marker={
            "size": 3,
            "color": sc6_bbp["bbp440"],
            "colorscale": "viridis",
            "showscale": False,
            "cmin": ocean_cmin,
            "cmax": ocean_cmax,
        },
    )
)

# --- Glider ---
fig.add_trace(
    go.Scatter3d(
        x=eco_bbp["lon"],
        y=eco_bbp["lat"],
        z=eco_bbp["z"],
        mode="markers",
        marker={
            "symbol": "square",
            "size": 3,
            "color": eco_bbp["bbp532"],
            "colorscale": "viridis",
            "showscale": False,
            "cmin": ocean_cmin,
            "cmax": ocean_cmax,
        },
        line={"color": "lightgray", "width": 2},
    )
)

# --- ER-2 ---
x, y, z, c = xr.broadcast(hsrl2_bbp["lon"], hsrl2_bbp["lat"], hsrl2_bbp["z"], hsrl2_bbp)
fig.add_trace(
    go.Surface(
        x=x,
        y=y,
        z=z.where(c.notnull()),
        surfacecolor=c,
        colorscale="inferno_r",
        showscale=True,
        cmin=atmos_cmin,
        cmax=atmos_cmax,
        colorbar={
            "title": {
                "text": "Aerosol b<sub>bp</sub>(532) [Mm⁻¹sr⁻¹]",
                "side": "right",
                "font": {"size": 10},
            },
            "tickfont": {"size": 9},
            "x": 0.8,
            "y": 0.6,
            "len": 0.4,
        },
    )
)


# --- Twin Otter ---
fig.add_trace(
    go.Scatter3d(
        x=isara_bbp["longitude"],
        y=isara_bbp["latitude"],
        z=isara_bbp["altitude"],
        mode="markers",
        marker={
            "size": 3,
            "color": isara_bbp,
            "colorscale": "plasma_r",
            "showscale": False,
            "cmin": atmos_cmin,
            "cmax": atmos_cmax,
            "line": {
                "color": "black",
                "width": 1,
            },
        },
    )
)

fig.update_layout(
    title={
        "text": "Multi-Platform 3D Ocean/Atmosphere Visualization (Santa Barbara)",
        "y": 0.995,
        "yanchor": "top",
        "x": 0.4,
        "xanchor": "center",
    },
    scene={
        "aspectmode": "manual",
        "aspectratio": {"x": 1, "y": 1, "z": 0.8},
        "xaxis": {"title": "Longitude", "range": [-120.2, -119.2]},
        "yaxis": {"title": "Latitude", "range": [34.15, 34.45]},
        "zaxis": {"title": "Height [m]", "range": [-400, 1000]},
        "camera": {
            "eye": {"x": -1.5, "y": -1.5, "z": 0.1}
        },
    },
    width=1100,
    height=800,
    margin={"l": 0, "r": 100, "b": 200, "t": 0},
    showlegend=False,
)

annotations_3d = [
    {
        "x": -120.1,
        "y": 34.4,
        "z": 5,
        "text": "<b>PACE</b>",
        "showarrow": False,
        "font": {"size": 12, "color": "white"},
        "bgcolor": "rgba(0,0,0,0.7)",
        "borderpad": 4,
    },
    {
        "x": -119.6,
        "y": 34.22,
        "z": -100,
        "text": "<b>Shearwater</b>",
        "showarrow": False,
        "font": {"size": 12, "color": "blue"},
        "bgcolor": "rgba(255,255,255,0.85)",
        "borderpad": 4,
    },
    {
        "x": -120.05,
        "y": 34.3,
        "z": -300,
        "text": "<b>Glider</b>",
        "showarrow": False,
        "font": {"size": 12, "color": "green"},
        "bgcolor": "rgba(255,255,255,0.85)",
        "borderpad": 4,
    },
    {
        "x": -119.6,
        "y": 34.2,
        "z": 800,
        "text": "<b>Twin Otter</b>",
        "showarrow": False,
        "font": {"size": 12, "color": "purple"},
        "bgcolor": "rgba(255,255,255,0.85)",
        "borderpad": 4,
    },
    {
        "x": -120.07,
        "y": 34.41,
        "z": 900,
        "text": "<b>ER-2</b>",
        "showarrow": False,
        "font": {"size": 12, "color": "orange"},
        "bgcolor": "rgba(255,255,255,0.85)",
        "borderpad": 4,
    },
]

fig.update_layout(scene={"annotations": annotations_3d})
fig.show()
```

<div class="alert alert-info" role="alert">

You have completed the notebook on accessing and analyzing PACE-PAX data!

</div>
