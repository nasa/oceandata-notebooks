# ---
# jupyter:
#   kernelspec:
#     display_name: Python 3 (ipykernel)
#     language: python
#     name: python3
# ---

# # Matchups of in situ data with satellite data
#
# **Tutorial Leads:** Anna Windle (NASA, SSAI), James Allen (NASA, Morgan State University)
#
# ## Summary
# In this example we will conduct matchups of in situ AERONET-OC Rrs data with PACE OCI Rrs data. The Aerosol Robotic Network (AERONET) was developed to sustain atmospheric studies at various scales with measurements from worldwide distributed autonomous sun-photometers. This has been extended to support marine applications, called AERONET – Ocean Color [(AERONET-OC)](https://aeronet.gsfc.nasa.gov/new_web/ocean_levels_versions.html), and provides the additional capability of measuring the radiance emerging from the sea (i.e., water-leaving radiance) with modified sun-photometers installed on offshore platforms like lighthouses, oceanographic and oil towers. AERONET-OC is instrumental in satellite ocean color validation activities. 
#
# In this tutorial, we will be collecting Rrs data from the Chesapeake Bay AERONET-OC site located at 39.1N, 76.3W in the upper Chesapeake Bay, Maryland, USA. The instrument is located 30m high on a USCG-controlled navigational range-light tower surrounded by highly turbid, optically deep 6-8 m depth waters. 
#
# We will be collecting PACE OCI Rrs data in a 5x5 pixel window around the AERONET-OC Rrs data to compare to the AERONET-OC data. 
#
# ## Learning Objectives
#
# At the end of this notebook you will know:
#
# * How to access Rrs data from a specific AERONET-OC site and time
# * How to access PACE OCI Rrs data from a specific location and time
# * How to match in situ and satellite data
# * How to apply statistics and plot matchup data
#
# ## Contents
#
# 1. [Setup](#1.-Setup)
# 2. [Process AERONET-OC data](#2.-Process-AERONET-OC-data)
#

# ## 1. Setup
#
# We begin by importing the packages used in this notebook.
# We will import `matchup_utils`, a .py file that hosts all the functions needed for this tutorial. 

from matchup_utils import *

# ## 2. Process AERONET-OC data
#
# We will use the function `process_aeronet` to download and process AERONET-OC data from the 'Chesapeake_Bay' site. We will filter Level 1.5 data from the dates June 1, 2024 to July 31, 2024. This function will output a pandas dataframe of every AERONET-OC record between the dates. 
#
# Level 1.5 data is ______. More information on AERONET-OC levels can be found in [Zibordi et al., 2009](https://doi.org/10.1175/2009JTECHO654.1)

aoc_cb = process_aeronet(aoc_site="Chesapeake_Bay", 
                start_date="2024-06-01", end_date="2024-07-31",
                data_level=15)
aoc_cb              

# ## 3. Process PACE OCI data 
#
# We will use the function `process_aeronet` to search for `PACE_OCI_L2_AOP_NRT` data using `earthaccess` within the specified time range and at the (lat,lon) coordinate of the Chesapeake_Bay AERONET-OC site. This function finds the closest pixel and extracts all data within a 5x5 pixel window, excludes pixels based on L2 flags, calculates the mean to retrive a single Rrs spectra, and computes matchup statistics. The function outputs a pandas dataframe of every `PACE_OCI_L2_AOP_NRT` Rrs spectra for the specified time range.

# +
aaot_lat = 45.3139
aaot_lon = 12.5083

cb_lat = 39.12351
cb_lon = -76.3489

sat_cb = process_satellite(start_date="2024-06-01", end_date="2024-07-31",
                  latitude=cb_lat, longitude=cb_lon, sat="PACE")
sat_cb
# -

# ## 3. Apply matchup code 
#
# We will use the function `match_data` to create a matchup dataframe based on selection criteria. This function __

matchups = match_data(sat_cb, aoc_cb, cv_max=0.60, senz_max=60.0, 
                      min_percent_valid=55.0, max_time_diff=180, std_max=1.5)
matchups

# Pull out wavelengths and Rrs data from matchups

# +
dict_aoc = get_column_prods(matchups, "aoc")
waves_aoc = np.array(dict_aoc["rrs"]["wavelengths"])
rrs_aoc = matchups[dict_aoc["rrs"]["columns"]].to_numpy()

dict_sat = get_column_prods(matchups, "oci")
waves_sat = np.array(dict_sat["rrs"]["wavelengths"])
rrs_sat = matchups[dict_sat["rrs"]["columns"]].to_numpy()

# -

# ## 4. Make plots
#
# We will use the function `plot_BAvsScat` to plot the paired matchup data as Bland_Altman and scatter plots as well as calculate statistics 

# +
MATCH_WAVES = np.array([400, 412, 443, 490, 510, 560, 620, 667])

# Loop through matchup wavelengths
stats_list = []

for idx, match_wave in enumerate(MATCH_WAVES):
    # Find matching OCI columns
    idx_sat = np.where(np.abs(waves_sat - match_wave) <= 5)[0]
    match_sat = np.nanmean(rrs_sat[:, idx_sat], axis=1)

    # Find matching AOC columns
    idx_aoc = np.where(np.abs(waves_aoc - match_wave) <= 5)[0]
    match_aoc = np.nanmean(rrs_aoc[:, idx_aoc], axis=1)

    valid_indices = np.isfinite(match_sat) & np.isfinite(match_aoc)
    if np.sum(valid_indices) > 5:
        fig_label = f"Rrs({match_wave}), sr" + r"$\mathregular{^{-1}}$"
        stats = plot_BAvsScat(match_aoc[valid_indices],
                                    match_sat[valid_indices],
                                    label=fig_label,
                                    saveplot=None,
                                    x_label="AERONET", y_label="PACE",
                                    is_type2=True)
        stats["wavelength"] = match_wave
        stats_list.append(stats)

# Organize stats DataFrame
df_stats = pd.DataFrame(stats_list)
#df_stats.set_index('wavelength', inplace=True)
#df_stats = df_stats.fillna(-999)

stats_list
# -


