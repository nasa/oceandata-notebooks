---
jupytext:
  notebook_metadata_filter: -all,kernelspec,jupytext
  cell_metadata_filter: all,-trusted
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

# Access and analyze PACE-PAX Data

**Authors:** Anna Windle (NASA, SSAI), Ivona Cetinić (NASA, MSU), Kirk Knobelspiesse (NASA)

Last updated: September 2, 2026

<div class="alert alert-success" role="alert">

The following notebooks are **prerequisites** for this tutorial.

- Learn with OCI: [Data Access](oci-data-access)
- SeaBASS? when its ready
</div>

<div class="alert alert-info" role="alert">

An [Earthdata Login][edl] account is required to access data from the NASA Earthdata system, including NASA ocean color data.

</div>

[edl]: https://urs.earthdata.nasa.gov/

## Summary

The PACE Postlaunch Airborne eXperiment ([PACE-PAX](https://pace.oceansciences.org/pace-pax.htm)) was a field campaign conducted in September 2024 in California and adjacent coastal areas. PACE-PAX brought together airborne and ship-based in situ observations to collect complementary atmospheric and oceanic measurements for the validation of observations from NASA's PACE mission.

All [PACE-PAX datasets](https://www.earthdata.nasa.gov/data/projects/pace-pax) are publicly available through the NASA Earthdata Cloud. This tutorial demonstrates how to access multiple PACE-PAX datasets, combine observations from different platforms, and create integrated visualizations to explore coupled atmosphere–ocean processes.

## Learning Objectives

At the end of this notebook you will be able to:

- Access PACE-PAX datasets from the NASA Earthdata Cloud.
- Read and explore PACE-PAX datasets using SeaBASS Python tools.
- Combine observations from multiple platforms into a single data fusion visualization.
- Explore coupled atmosphere–ocean observations collected during PACE-PAX.

+++

## 1. Setup

+++

Begin by importing all of the packages used in this notebook. If you followed the guidance on the [Getting-Started](/getting-started) page, then the imports will be successful.

```{code-cell} ipython3
import cartopy.crs as ccrs
import earthaccess
import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
import xarray as xr

# import plotly
#import plotly.graph_objects as go
#import plotly.io as pio

plt.rcdefaults()
```

```{code-cell} ipython3
!pip install plotly
```

```{code-cell} ipython3
import plotly.graph_objects as go
import plotly.io as pio
```

Set your Earthdata Login credentials. You can add persist=True to save your credentials in a .netrc file, allowing you to authenticate automatically in the future sessions without re-entering your Earthdata credentials.

```{code-cell} ipython3
auth = earthaccess.login()
```

Now, we'll import the SeaBASS Utilities python package. The sb_utilities package is a collection of Python functions developed to assist with SeaBASS data processing, file manipulation, and mapping tasks, originally developed at NASA Goddard Space Flight Center (GSFC). We will use a `pip install` to install the Python package.

```{code-cell} ipython3
---
collapsed: true
jupyter:
  outputs_hidden: true
---
!pip install "sb_utilities[all] @ https://seabass.gsfc.nasa.gov/wiki/seabass_tools/sb_utilities-0.0.5-py3-none-any.whl"
```

```{code-cell} ipython3
import sb_utilities as sb
```

## 2. Access PACE OCI ocean particulate backscattering data

+++

Let's find a PACE OCI Level-2 IOP granule acquired during the PACE-PAX campaign over the Santa Barbara Channel, California.

```{code-cell} ipython3
tspan = ("2024-09-26", "2024-09-26")
bbox = (-120, 33, -110, 35)

results = earthaccess.search_data(
    short_name="PACE_OCI_L2_IOP",
    temporal=tspan,
    bounding_box=bbox,
)
print(len(results))

oci_paths = earthaccess.open(results)
oci_paths
```

We can open this file up using `xarray` and retrieve particulate backscattering at 442 nm data (`bbp_442`):

```{code-cell} ipython3
oci_dt = xr.open_datatree(oci_paths[-1])
oci_ds = oci_dt["geophysical_data"]["bbp_442"]
for item in ("longitude", "latitude"):
    oci_ds[item] = oci_dt["navigation_data"][item]
oci_ds
```

Let's subset the PACE OCI bbp_442 data to a smaller geographical region:

```{code-cell} ipython3
subset = (
    (oci_ds.longitude >= -120.5)
    & (oci_ds.longitude <= -119.0)
    & (oci_ds.latitude >= 33.8)
    & (oci_ds.latitude <= 34.5)
)

oci_bbp = oci_ds.where(subset & (oci_ds > 0))
oci_bbp
```

```{code-cell} ipython3
fig, ax = plt.subplots(figsize=(8, 6), subplot_kw={"projection": ccrs.PlateCarree()})

oci_bbp.plot(
    ax=ax,
    x="longitude",
    y="latitude",
    transform=ccrs.PlateCarree(),
    cmap="viridis",
    vmax=0.015,
    cbar_kwargs={"shrink": 0.6},
)

ax.coastlines(resolution="10m", linewidth=1)

ax.set_extent([-120.5, -119.0, 33.8, 34.5], crs=ccrs.PlateCarree())

gl = ax.gridlines(
    draw_labels={"bottom": True, "left": True, "top": False, "right": False},
    xlocs=plt.MaxNLocator(5),
    ylocs=plt.MaxNLocator(5),
    linewidth=0,
)

plt.tight_layout()
plt.show()
```

# 2. Access aircraft aerosol particle backscattering data

Now let's access data collected from one of the aircraft flown during PACE-PAX. A Twin Otter airplane from the Center for Interdisciplinary Remotely Piloted Aircraft Studies (CIRPAS) at the Naval Postgraduate School in Monterey, CA, collected data on aerosol particles in the atmosphere. We will use the aerosol backscattering coefficient at 532 nm, measured under ambient relative humidity, temperature, and pressure, represented by the variable `fine_amb_back_coef`.

```{code-cell} ipython3
results = earthaccess.search_data(
    temporal=tspan,
    short_name='PACE-PAX_Analysis_ISARA_Data')
print(len(results))

twinotter_paths = earthaccess.open(results)
twinotter_paths
```

```{code-cell} ipython3
twinotter_dt = xr.open_datatree(twinotter_paths[-1])
twinotter_ds = xr.merge(twinotter_dt.to_dict().values())
twinotter_ds
```

Let's filter out the data collected when the aircraft was flying in a spiral:

```{code-cell} ipython3
twinotter_lat = twinotter_ds["Latitude_BUCHOLTZ"].values
twinotter_lon = twinotter_ds["Longitude_BUCHOLTZ"].values
twinotter_alt = (
    twinotter_ds["GPS_Altitude_BUCHOLTZ"].values / 10)  # Scale altitude for plotting

twinotter_bbp = np.where(
    np.isfinite(twinotter_ds["fine_amb_back_coef"].values),
    twinotter_ds["fine_amb_back_coef"].values,
    np.nan,
)

wv_idx = np.where(twinotter_ds["wavelength"].values == 532)[0][0]

track = (
    (twinotter_lon >= -120.5)
    & (twinotter_lon <= -119.0)
    & (twinotter_lat >= 34.1)
    & (twinotter_lat <= 34.5)
)

twinotter_bbp = twinotter_bbp[track, wv_idx]

valid = np.isfinite(twinotter_bbp) & (twinotter_bbp > 0) & (twinotter_bbp < 1e-2)

twinotter_lon_track = twinotter_lon[track][valid]
twinotter_lat_track = twinotter_lat[track][valid]
twinotter_alt_track = twinotter_alt[track][valid]
twinotter_bbp = twinotter_bbp[valid] * 1e6  # Mm⁻¹ sr⁻¹
twinotter_bbp.shape
```

```{code-cell} ipython3
fig, axs = plt.subplots(
    1, 2,
    figsize=(10, 4)
)

sc1 = axs[0].scatter(
    twinotter_lon_track,
    twinotter_lat_track,
    c=twinotter_bbp,
    s=20,
    cmap="plasma_r"
)

axs[0].set_xlabel("Longitude")
axs[0].set_ylabel("Latitude")
axs[0].set_title("Twin Otter Flight Track")
axs[0].axis("equal")


sc2 = axs[1].scatter(
    twinotter_lon_track,
    twinotter_alt_track,
    c=twinotter_bbp,
    s=20,
    cmap="plasma_r"
)

axs[1].set_xlabel("Longitude")
axs[1].set_ylabel("Altitude")
axs[1].set_title("Twin Otter Vertical Profile")

fig.colorbar(
    sc2,
    ax=axs,
    label=r"532 nm aerosol backscatter (Mm$^{-1}$ sr$^{-1}$)"
)

plt.show()
```

# 3. Access Aircraft High Spectral Resolution Lidar 2 (HSRL-2) data

The High Spectral Resolution Lidar 2 (HSRL-2) instrument was flown aboard NASA's high altitude Earth Resources 2 (ER-2) aircraft to characterize atmospheric aerosol particles. We will use the aerosol backscatter coefficient measured at 532 nm.

TODO: figure out difference between R0 and R1 data.

```{code-cell} ipython3
results = earthaccess.search_data(
    temporal=tspan,
    short_name='PACE-PAX_AircraftRemoteSensing_ER2_HSRL2_Data',
    granule_name="*.h5*"
)
print(len(results))

hsrl_paths = earthaccess.open(results)
hsrl_paths
```

```{code-cell} ipython3
hslr_dt = xr.open_datatree(hsrl_paths[1])
hslr_dt
```

Let's filter the data to a specific geographic location and time:

```{code-cell} ipython3
lidar_lat = hslr_dt["lat"]
lidar_lon = hslr_dt["lon"]
lidar_alt = hslr_dt["z"]
lidar_time = hslr_dt["time"]
lidar_bbp = hslr_dt["DataProducts"]["532_bsc_cloud_screened"]

track = (
    (lidar_time >= np.datetime64("2024-09-26T19:32:24"))
    & (lidar_time <= np.datetime64("2024-09-26T19:38:24"))
    & (lidar_lon >= -120.2)
    & (lidar_lon <= -119.0)
    & (lidar_lat >= 34.1)
    & (lidar_lat <= 34.5)
)

lidar_lon = lidar_lon[track]
lidar_lat = lidar_lat[track]

# Convert to Mm⁻¹ sr⁻¹ and mask invalid values
lidar_bbp = lidar_bbp[track, :] * 1000
lidar_bbp = np.where(lidar_bbp > -0.01, lidar_bbp, np.nan)

# Restrict to lowest 1 km (scaled by 10 for plotting)
alt_mask = (lidar_alt > 0) & (lidar_alt <= 1000)
lidar_alt = lidar_alt[alt_mask] / 10
lidar_bbp = lidar_bbp[:, alt_mask]

# Build 3D curtain
X_lidar, Z_lidar = np.meshgrid(lidar_lon, lidar_alt)
Y_lidar, _ = np.meshgrid(lidar_lat, lidar_alt)

lidar_bbp = lidar_bbp.T
Z_lidar = np.where(np.isnan(lidar_bbp), np.nan, Z_lidar)

lidar_cmin = np.nanmin(lidar_bbp)
lidar_cmax = np.nanmax(lidar_bbp)
```

And plot the lidar aerosol backscatter curtain:

```{code-cell} ipython3
fig, ax = plt.subplots(figsize=(8, 4))

pcm = ax.pcolormesh(
    lidar_lon,
    lidar_alt,
    lidar_bbp,
    shading="auto",
    cmap="inferno_r",
    vmin=lidar_cmin,
    vmax=lidar_cmax,
)

cbar = fig.colorbar(pcm, ax=ax)
cbar.set_label(r"532 nm Backscatter (Mm$^{-1}$ sr$^{-1}$)")

ax.set_xlabel("Longitude")
ax.set_ylabel("Altitude (×10 m)")
ax.set_title("HSRL-2 Aerosol Backscatter Curtain")

plt.tight_layout()
plt.show()
```

# 4. Access in situ ocean particle backscattering data

In situ oceanic observations were collected aboard the NOAA R/V Shearwater. Particulate backscattering was measured using an SC6 backscattering sensor.

Let's open particulate backscattering at 440 nm (`bbp440`) collected on Sep 26th.

```{code-cell} ipython3
results = earthaccess.search_data(
    temporal=tspan,
    short_name='PACE-PAX',
    granule_name='*Shearwater*SC6026*',
)
print(len(results))

shearwater_paths = earthaccess.open(results)
shearwater_paths
```

```{code-cell} ipython3
profiles = []
cruise_title = ""

for file in shearwater_paths:
    file_path = file.path if hasattr(file, "path") else str(file)

    if file_path.endswith(".sb") and not file_path.endswith(".tgz.sb"):
        sb_data = sb.sb_read(file, no_warn=True)
        df = pd.DataFrame(sb_data.data)
        header = sb_data.headers

        # Extract station location from header metadata
        station_lat = float(header["north_latitude"].split("[")[0])
        station_lon = float(header["east_longitude"].split("[")[0])
        cruise_title = header.get("cruise", "Map")

        # Add metadata columns to each profile measurement
        profile = pd.DataFrame(
            {
                "latitude": station_lat,
                "longitude": station_lon,
                "depth": df["depth"].values,
                "bbp440": df["bbp440"].values,
            }
        )

        profiles.append(profile)

shearwater_df = pd.concat(profiles, ignore_index=True)

shearwater_lat = shearwater_df["latitude"].values
shearwater_lon = shearwater_df["longitude"].values
shearwater_depths = shearwater_df["depth"].values

shearwater_df.head()
```

And we can now plot the vertical profiles of particulate backscattering at 440 nm:

```{code-cell} ipython3
fig, ax = plt.subplots(figsize=(5, 6))

for (lat, lon), group in shearwater_df.groupby(["latitude", "longitude"]):

    sc = ax.scatter(
        np.full(len(group), lon),  
        group["depth"],
        c=group["bbp440"],
        s=35,
        cmap="viridis",
    )

ax.invert_yaxis()

ax.set_xlabel("Longitude")
ax.set_ylabel("Depth (m)")
ax.set_title(r"R/V Shearwater SC6 $b_{bp}(440)$ profiles")

# Colorbar
cbar = plt.colorbar(sc, ax=ax)
cbar.set_label(r"$b_{bp}(440)$ (m$^{-1}$)")

plt.tight_layout()
plt.show()
```

# 5. Access glider backscattering data

An autonomous ocean glider was also deployed along a 10-km transect for 25 days. The glider was equipped with optical sensors that measured particulate backscatter at 532 nm.

```{code-cell} ipython3
results = earthaccess.search_data(
    temporal=tspan,
    short_name='PACE-PAX',
    granule_name='*glider*bbp*')
print(len(results))

glider_paths = earthaccess.open(results)
glider_paths
```

```{code-cell} ipython3
glider_data = sb.sb_read(glider_paths[0], no_warn=True)
glider_df = pd.DataFrame(glider_data.data)
glider_df.head()
```

Let's filter out glider data from a specified date and location:

```{code-cell} ipython3
glider_subset = glider_df[
    (glider_df["date"] == 20240926)
    & (glider_df["lon"] >= -120.5)
    & (glider_df["lon"] <= -119.0)
    & (glider_df["lat"] >= 33.8)
    & (glider_df["lat"] <= 34.5)
]

glider_lon = glider_subset["lon"].values
glider_lat = glider_subset["lat"].values

glider_depth = -np.abs(glider_subset["depth"].values)
glider_bbp = glider_subset["bbp532"].values

valid = (glider_bbp > 0)

glider_lon = glider_lon[valid]
glider_lat = glider_lat[valid]
glider_depth = glider_depth[valid]
glider_bbp = glider_bbp[valid]

glider_bbp.shape
```

And we can plot `bbp(532)` along the glider's track as it descended and ascended throughout the day:

```{code-cell} ipython3
fig, ax = plt.subplots(figsize=(8, 5))

sc = ax.scatter(
    glider_lon, glider_depth, c=glider_bbp, s=15, cmap="viridis", vmax=0.004
)

ax.set_xlabel("Longitude")
ax.set_ylabel("Depth (m)")
ax.set_title("PACE-PAX Glider $b_{bp}(532)$ on Sept 26 2024")

# Colorbar
cbar = plt.colorbar(sc, ax=ax)
cbar.set_label(r"$b_{bp}(532)$ (m$^{-1}$)")

plt.tight_layout()
plt.show()
```

# 6 Multidimensional plot 

Now, let's plot all this data together in a multi-dimensional plot

```{code-cell} ipython3
pio.renderers.default = "notebook"

fig = go.Figure()

ocean_cmin = 0
ocean_cmax = 0.01

# --- PACE OCI bbp ---
fig.add_trace(
    go.Surface(
        x=oci_bbp.longitude,
        y=oci_bbp.latitude,
        z=oci_bbp,
        surfacecolor=oci_bbp,
        colorscale="viridis",
        name="PACE OCI surface bbp",
        showscale=True,
        opacity=0.8,
        cmin=ocean_cmin,
        cmax=ocean_cmax,
        colorbar=dict(
            title=dict(
                text="Ocean b<sub>bp</sub>(λ) (m⁻¹)",
                side="right",
                font=dict(size=10),
            ),
            tickfont=dict(size=9),
            x=0.84,
            y=0.20,
            len=0.25,
            tickvals=[0, 0.002, 0.004, 0.006, 0.008, 0.01],
            ticktext=["0", "0.002", "0.004", "0.006", "0.008", "0.01"],
        ),
    )
)

# --- Shearwater Profile ---
fig.add_trace(
    go.Scatter3d(
        x=shearwater_lon,
        y=shearwater_lat,
        z=-np.abs(shearwater_depths),
        mode="markers",
        marker=dict(
            size=3,
            color=shearwater_df["bbp440"],
            colorscale="viridis",
            showscale=False,
            cmin=ocean_cmin,
            cmax=ocean_cmax,
        ),
        name="Shearwater Profile",
    )
)

# --- Glider Track ---
fig.add_trace(
    go.Scatter3d(
        x=glider_lon,
        y=glider_lat,
        z=glider_depth,
        mode="markers",
        marker=dict(
            symbol="square",
            size=3,
            color=glider_bbp,
            colorscale="Viridis",
            showscale=False,
            cmin=ocean_cmin,
            cmax=np.nanmax(glider_bbp),
        ),
        line=dict(color="lightgray", width=2),
        name="Glider Track",
    )
)

# --- HSRL Lidar Curtain ---
fig.add_trace(
    go.Surface(
        x=X_lidar,
        y=Y_lidar,
        z=Z_lidar,
        surfacecolor=lidar_bbp,
        colorscale="Inferno_r",
        name="HSRL-2 Lidar Curtain",
        showscale=True,
        cmin=-0.009,
        cmax=4.5,
        colorbar=dict(
            title=dict(
                text="ER2 HSRL-2 aerosol <br> bbp(532) (Mm⁻¹sr⁻¹)",
                side="right",
                font=dict(size=10),
            ),
            tickfont=dict(size=9),
            x=0.84,
            y=0.70,
            len=0.25,
        ),
    )
)

# --- Twin Otter Flight Path ---
fig.add_trace(
    go.Scatter3d(
        x=twinotter_lon_track,
        y=twinotter_lat_track,
        z=twinotter_alt_track,
        mode="markers",
        marker=dict(
            size=4,
            color=twinotter_bbp,
            colorscale="Plasma_r",
            showscale=True,
            cmin=0.15,
            cmax=0.4,
            line=dict(color="black", width=1.5),
            colorbar=dict(
                title=dict(
                    text=f"Twin otter aerosol <br> bbp(532) (Mm⁻¹sr⁻¹)",
                    side="right",
                    font=dict(size=10),
                ),
                tickfont=dict(size=9),
                x=0.84,
                y=0.45,
                len=0.25,
            ),
        ),
        name=f"Twin Otter",
    )
)

fig.update_layout(
    title=dict(text="Multi-Platform 3D Ocean/Atmosphere Visualization (Santa Barbara)",
        y=0.995, yanchor="top", x=0.4, xanchor="center",
    ),
    scene=dict(
        aspectmode="manual",
        aspectratio=dict(x=1, y=1, z=0.8),
        xaxis=dict(title="Longitude", range=[-120.2, -119.2]),
        yaxis=dict(title="Latitude", range=[34.15, 34.45]),
        zaxis=dict(
            title="Depth (m) / Altitude (m)",
            range=[-50, 100],
            autorange=False,
            tickvals=[-50, -40, -30, -20, -10, 0, 20, 40, 60, 80, 100],
            ticktext=[
                "-50",
                "-40",
                "-30",
                "-20",
                "-10",
                "0",
                "200",
                "400",
                "600",
                "800",
                "1000",
            ],
        ),

        camera=dict(
            eye=dict(
                x=-1.3,
                y=-1.3,
                z=0.2
            )
        ), 
    ),
    width=1100,
    height=800,
    margin=dict(l=0, r=100, b=200, t=0), 
    showlegend=False,
)
  
annotations_3d = [
    dict(
        x=-120.1,
        y=34.4,
        z=5,
        text="<b>PACE OCI bbp</b>",
        showarrow=False,
        font=dict(size=12, color="white"),
        bgcolor="rgba(0,0,0,0.7)",
        borderpad=4,
    ),
    dict(
        x=-119.35,
        y=34.22,
        z=-45,
        text="<b>Shearwater Profiles</b>",
        showarrow=False,
        font=dict(size=12, color="blue"),
        bgcolor="rgba(255,255,255,0.85)",
        borderpad=4,
    ),
    dict(
        x=-120.05,
        y=34.4,
        z=-30,
        text="<b>Glider profiles</b>",
        showarrow=False,
        font=dict(size=12, color="green"),
        bgcolor="rgba(255,255,255,0.85)",
        borderpad=4,
    ),
    dict(
        x=-119.6,
        y=34.2,
        z=80,
        text="<b>Twin Otter Spiral</b>",
        showarrow=False,
        font=dict(size=12, color="purple"),
        bgcolor="rgba(255,255,255,0.85)",
        borderpad=4,
    ),
    dict(
        x=-120.07,
        y=34.41,
        z=90,
        text="<b>ER2 HSRL-2 Curtain</b>",
        showarrow=False,
        font=dict(size=12, color="orange"),
        bgcolor="rgba(255,255,255,0.85)",
        borderpad=4,
    ),
]

fig.update_layout(scene=dict(annotations=annotations_3d))
fig.show()
```

<div class="alert alert-info" role="alert">

You have completed the notebook on accessing and analyzing PACE-PAX data!

</div>
