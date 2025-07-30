---
kernelspec:
  display_name: Python 3 (ipykernel)
  language: python
  name: python3
---

# Applying L-S Periodogram Analysis to Ocean Color Data

**Authors:** Riley Blocker (NASA, SSAI)

<div class="alert alert-success" role="alert">

The following are **prerequisites** for this tutorial

- A NASA Ocean Color Validation Data .csv file, which can also be downloaded from: https://seabass.gsfc.nasa.gov/search#val

</div>

## Summary

This notebook follows the astropy documentation for [timeseries analysis] to generate a [Lomb-Scargle periodograms] for Ocean Color (OC) data.

[timeseries analysis]: https://docs.astropy.org/en/stable/timeseries/index.html
[Lomb-Scargle periodograms]: https://docs.astropy.org/en/stable/timeseries/lombscargle.html

## Learning Objectives

At the end of this notebook you will know how to:

- Generate a Lomb-Scargle periodogram for ocean color data time series 
- Calculate the False-Alarm-Probability to estimate the significance of a peak in the periodogram

+++

## Setup

```{code-cell} ipython3
import matplotlib as mpl
import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
from astropy import units as u
from astropy.timeseries import LombScargle, TimeSeries

mpl.rcParams["lines.markersize"] = 5
mpl.rcParams["scatter.marker"] = "."
```

## Validation Data

NASA Ocean Color Validation Data can be extracted from https://seabass.gsfc.nasa.gov/search#val.
This example uses Moby validation data called "ModisA_Moby.csv".
To begin, we load the validation data as pandas dataframe and set the index to `datetime`.

```{code-cell} ipython3
df = pd.read_csv(
    "ModisA_Moby.csv",
    header=33,
    skiprows=(35, 34),
)
df["date_time"] = pd.to_datetime(
    df["date_time"],
    format="%Y-%m-%d %H:%M:%S",
)
df = df.set_index("date_time")
```

Add a $\Delta R_{rs}(\lambda)$ column for the difference between the remote-sensing and in-situ observations.

```{code-cell} ipython3
df["Delta_rrs412"] = df["aqua_rrs412"] - df["insitu_rrs412"]
```

Convert the pandas data frame to an astropy time series.

```{code-cell} ipython3
ts = TimeSeries.from_pandas(df)
```

Plot MODIS-Aqua solar zenith angle versus time.

```{code-cell} ipython3
fig, ax = plt.subplots(figsize=(10, 3))

ax.scatter(ts.time.decimalyear, ts["aqua_solz"])
ax.set_xlabel("Year")
ax.set_ylabel(r"Degrees")
ax.set_title("Solar Zenith Angle")

plt.show()
```

Periodicity clearly exists.

+++

Plot $\Delta\ R_{rs}(\lambda)$, Modis-Aqua $R_{rs}(\lambda)$, and MOBY $R_{rs}(\lambda)$ versus time

```{code-cell} ipython3
fig, axs = plt.subplots(3, 1, figsize=(10, 6), sharex=True)
year = ts.time.decimalyear

axs[0].scatter(year, ts["Delta_rrs412"])
axs[0].set_ylabel(r"$\Delta\ R_{rs}(412\ \mathrm{nm})$")
axs[0].set_title(r"MODIS-Aqua - MOBY")
axs[1].scatter(year, ts["insitu_rrs412"])
axs[1].set_ylabel(r"$R_{rs}(412\ \mathrm{nm})$")
axs[1].set_title(r"MOBY")
axs[2].scatter(year, ts["aqua_rrs412"])
axs[2].set_ylabel(r"$R_{rs}(412\ \mathrm{nm})$")
axs[2].set_title(r"MODIS-Aqua")
axs[2].set_xlabel("Year")

fig.tight_layout()
fig.show()
```

Unlike SZA versus time (and to a lesser extent the $R_{rs}(\lambda)$ time series), the periodicity the $\Delta R_{rs}(\lambda)$ time series is hader to determine from the scatter plots

+++

## Lomb-Scargle Periodogram

+++

Generate Lomb-Scargle periodogram from the time series data.
Specify parameters to use in the periodogram generation (see https://docs.astropy.org/en/stable/timeseries/lombscargle.html for descriptions).

```{code-cell} ipython3
ls_kwargs = {
    "nterms": 1,
    "normalization": "standard",
}
power_kwargs = {
    "minimum_frequency": 1 / (365.25 * 2.5) * (1 / u.day),
    "maximum_frequency": 1 / (7) * (1 / u.day),
    "samples_per_peak": 50,
    "method": "cython",
}
```

Generate L-S periodogram.

```{code-cell} ipython3
ls = LombScargle.from_timeseries(ts, "aqua_solz", **ls_kwargs)
frequency, power = ls.autopower(**power_kwargs)
period = (1 / frequency).to("year")
```

```{code-cell} ipython3
fig, ax = plt.subplots(figsize=(4, 3))

ax.plot(period, power)
ax.set_title("Solar Zenith Angle")
ax.set_xlabel("Period [yr]")
ax.set_ylabel("Power")

fig.show()
```

Generate Perdiograms for $R_{rs}(\lambda)$

```{code-cell} ipython3
uncertainty = ts["Delta_rrs412"].std()
```

```{code-cell} ipython3
DeltaRrs412_ls = LombScargle.from_timeseries(
    ts, "Delta_rrs412", uncertainty, **ls_kwargs
)
frequency, DeltaRrs412_power = DeltaRrs412_ls.autopower(**power_kwargs)
```

```{code-cell} ipython3
MobyRrs412_ls = LombScargle.from_timeseries(
    ts, "insitu_rrs412", 0.5 * uncertainty, **ls_kwargs
)
frequency, MobyRrs412_power = MobyRrs412_ls.autopower(**power_kwargs)
```

```{code-cell} ipython3
AquaRrs412_ls = LombScargle.from_timeseries(
    ts, "aqua_rrs412", 0.5 * uncertainty, **ls_kwargs
)
frequency, AquaRrs412_power = AquaRrs412_ls.autopower(**power_kwargs)
```

```{code-cell} ipython3
fig, axs = plt.subplots(1, 3, figsize=(10, 3), sharex=True, sharey=True)

axs[0].plot(period, DeltaRrs412_power)
axs[0].set_xlabel("Period [yr]")
axs[0].set_ylabel("Power")
axs[0].set_title(r"$\Delta\ R_{rs}(412\ \mathrm{nm})$")

axs[1].plot(period, MobyRrs412_power)
axs[1].set_xlabel("Period [yr]")
axs[1].set_title(r"MOBY $R_{rs}(412\ \mathrm{nm})$")

axs[2].plot(period, AquaRrs412_power)
axs[2].set_xlabel("Period [yr]")
axs[2].set_title(r"MODIS-Aqua $R_{rs}(412\ \mathrm{nm})$")

fig.show()
```

Find "best" periodicity.

```{code-cell} ipython3
period = period.round(3)
best_DeltaRrs412_period = period[np.argmax(DeltaRrs412_power)]
best_MobyRrs412_period = period[np.argmax(MobyRrs412_power)]
best_AquaRrs412_period = period[np.argmax(AquaRrs412_power)]
```

```{code-cell} ipython3
table = pd.DataFrame(
    index=[
        r"$\Delta R_{rs}(\lambda)$",
        r"MOBY $R_{rs}(\lambda)$",
        r"MODIS-Aqua  $R_{rs}(\lambda)$",
    ],
    data={
        "best_period": [
            best_DeltaRrs412_period,
            best_MobyRrs412_period,
            best_AquaRrs412_period,
        ]
    },
)
table[["best_period"]]
```

The "best" periods are all close to the annual period, which is within the precision uncertainity when the width of the peaks are considered.

+++

## False Alarm Probability

+++

A more useful metric for computing the uncertainty associated with the peak is the false alarm probablity (FAP)

Get the position of the period closest to the annual period.

```{code-cell} ipython3
i = np.argmin(np.abs(period - 1 * u.year))
```

```{code-cell} ipython3
annual_power = DeltaRrs412_power[i]
DeltaRrs412_fap = DeltaRrs412_ls.false_alarm_probability(
    annual_power, method="bootstrap"
)
```

```{code-cell} ipython3
annual_power = MobyRrs412_power[i]
MobyRrs412_fap = MobyRrs412_ls.false_alarm_probability(annual_power, method="bootstrap")
```

```{code-cell} ipython3
annual_power = AquaRrs412_power[i]
AquaRrs412_fap = AquaRrs412_ls.false_alarm_probability(annual_power, method="bootstrap")
```

```{code-cell} ipython3
table["FAP"] = [
    DeltaRrs412_fap,
    MobyRrs412_fap,
    AquaRrs412_fap,
]
table[["FAP"]]
```

The FAPs at the annual period for for all the time series are zero, strongly indicating that the annual frequency is contained in the time series.

+++

## Folding Time Series

+++

Folding time series to the annual peridocity. A day in the middle of the year is chosen so that the x-axis begins with Jan 1st (-182.56 days) and ends with Dec 31st (182.5).

```{code-cell} ipython3
folded_ts = ts.fold(period=1 * u.year, epoch_time="2000-07-02")
```

```{code-cell} ipython3
fig, axs = plt.subplots(1, 3, figsize=(10, 3), sharex=True, sharey=True)

x = folded_ts.time.jd
y = folded_ts["Delta_rrs412"]
axs[0].scatter(x, y)
axs[0].set_ylabel(r"$\Delta\ R_{rs}(412\ \mathrm{nm})$")
axs[0].set_title(r"MODIS-Aqua - MOBY")
axs[0].axhline(y=0, color="black", linewidth=2)

y = folded_ts["insitu_rrs412"]
axs[1].scatter(x, y)
axs[1].set_xlabel("Day of Year [day]")
axs[1].set_ylabel(r"$R_{rs}(412\ \mathrm{nm})$")
axs[1].set_title(r"MOBY")
axs[1].axhline(y=y.mean(), color="black", linewidth=2)

y = folded_ts["aqua_rrs412"]
axs[2].scatter(x, y)
axs[2].set_ylabel(r"$R_{rs}(412\ \mathrm{nm})$")
axs[2].set_title(r"MODIS-Aqua")
axs[2].axhline(y=y.mean(), color="black", linewidth=2)

fig.tight_layout()
fig.show()
```

When folded, the annual perodicity is clearly contained in the time series.
