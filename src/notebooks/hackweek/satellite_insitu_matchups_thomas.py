# ---
# jupyter:
#   kernelspec:
#     display_name: Python 3 (ipykernel)
#     language: python
#     name: python3
# ---

# # Matchups of in situ data with satellite data using the ThoMaS match-up toolkit
# **Authors:** Anna Windle (NASA, SSAI), James Allen (NASA, Morgan State University), Juan Ignacio Gossn (EUMETSAT), Ben Loveday (EUMETSAT)
#
#
# ## Summary
#
# In this example we will conduct matchups of in situ data with PACE OCI satellite data using the ThoMaS (Tool to generate Matchups for OC products with Sentinel-3/OLCI) package. This package provides a comprehensive set of tools to help with the validation of satellite products, supporting many common workflows including:
#
# * satellite data acquisition
# * mini file extraction
# * in situ data management
# * bidirectional reflectance distribution function (BRDF) correction
#
# ThoMaS is written in Python and is made available through a [EUMETSAT Gitlab repository](https://gitlab.eumetsat.int/eumetlab/oceans/ocean-science-studies/ThoMaS). The package can be used from the command line, or imported as a Python library, as done here. This notebook contains an example of how to use ThoMaS, but the capability shown is not exhaustive. Many more command-line examples are included in the repository, and we encourage users to familiarise themselves with both the [project README](https://gitlab.eumetsat.int/eumetlab/oceans/ocean-science-studies/ThoMaS/-/blob/main/README.md) and  [example README](https://gitlab.eumetsat.int/eumetlab/oceans/ocean-science-studies/ThoMaS/-/blob/main/README_examples.md) for more information.
#
# ## Learning Objectives
#
# At the end of this notebook you will know:
#
# * How to create a configuration file for the ThoMaS matchup toolkit
# * How to run ThoMaS for a full matchup exercise: satellite extractions + minifiles + extraction statistics + matchup statistics
# * Use standard matchup protocols to apply statistics and plot matchup data
#
# ## Contents 
#
# 1. [Setup](#1.-Setup)
# 2. [Create configuration file for ThoMaS](#2.-Create configuration file for ThoMaS)
# 3. [Run ThoMaS])(#3.-Run ThoMaS)

# ## 1. Setup
#
# Begin by importing all of the packages used in this notebook. 

# +
import sys
import os

import earthaccess
import pandas as pd
import numpy as np
# -

# The first thing we need to do is retrieve the toolkit itself. For the hackweek, we have already saved the ThoMaS toolkit under `shared/pace-hackweek-2024/lib/ThoMaS`.
#
# ThoMaS can be used from the [command line](https://gitlab.eumetsat.int/eumetlab/oceans/ocean-science-studies/ThoMaS/-/blob/main/README_examples.md), but here we will use it as a Python library. Lets import ThoMaS into our notebook.

sys.path.insert(1, 'shared/pace-hackweek-2024/lib/ThoMaS')
from main import ThoMaS_main as ThoMaS

# We also need to save our Earthdata login credentials in our home directory.
#
# Copy your username and password and store them in a JSON file under
# `~/.obpg_credentials.json` (~ stands for your home directory)" <br>
# {"username": "john.doe", "password": "jd_1234"}

# [back to top](#Contents)

# ## 2. Create configuration file for ThoMaS
#
# In this example we will conduct matchups of in situ AERONET-OC Rrs data with PACE OCI Rrs data. The Aerosol Robotic Network (AERONET) was developed to sustain atmospheric studies at various scales with measurements from worldwide distributed autonomous sun-photometers. This has been extended to support marine applications, called AERONET – Ocean Color [(AERONET-OC)](https://aeronet.gsfc.nasa.gov/new_web/ocean_levels_versions.html), and provides the additional capability of measuring the radiance emerging from the sea (i.e., water-leaving radiance) with modified sun-photometers installed on offshore platforms like lighthouses, oceanographic and oil towers. AERONET-OC is instrumental in satellite ocean color validation activities. 
#
# In this tutorial, we will be collecting Rrs data from the Chesapeake Bay AERONET-OC site located at 39.1N, 76.3W in the upper Chesapeake Bay, Maryland, USA. The instrument is located 30m high on a USCG-controlled navigational range-light tower surrounded by highly turbid, optically deep 6-8 m depth waters. 
#
# Below are our requirements for this workflow:
# 1. I want to test the performance of PACE OCI at the AERONET-OC station Chesapeake_Bay during July 2024.
# 2. I wish to get matchups between this Chesapeake_Bay subset and PACE/OCI Rrs using the standard extraction protocol from [Bailey and Werdell, 2006](https://oceancolor.gsfc.nasa.gov/staff/jeremy/bailey_and_werdell_2006_rse.pdf), using an extraction window of 5x5.
# 3. I want to apply the [Lee et al. ??](link) BRDF correction to both satellite and in situ data.
# 4. Store all outputs in the "Chesapeake_Bay" directory. 
#

# Let's first define and create the pathto our main output directory

output_path = os.path.join(os.getcwd(), "Chesapeake_Bay")
if not os.path.exists(output_path):
    os.mkdir(output_path)

# Let's now define out configuration file.

TODO: change brdf to Lee 

# +
path_to_config_file = os.path.join(output_path, 'config_file.ini')
config_params = {}

# global
config_params['global'] = {}
config_params['global']['path_output'] = output_path
config_params['global']['SetID'] = 'Chesapeake_Bay'
config_params['global']['workflow'] = 'insitu, SatData, minifiles, EDB, MDB'


# AERONETOC
config_params['AERONETOC'] = {}
config_params['AERONETOC']['AERONETOC_pathRaw'] = os.path.join(output_path, 'Chesapeake_Bay', 'AERONET_OC_raw')
config_params['AERONETOC']['AERONETOC_dateStart'] = '2024-07-01T00:00:00'
config_params['AERONETOC']['AERONETOC_dateEnd'] = '2024-07-31T00:00:00'
config_params['AERONETOC']['AERONETOC_dataQuality'] = 1.5
config_params['AERONETOC']['AERONETOC_station'] = 'Chesapeake_Bay'

# insitu
config_params['insitu'] = {}
config_params['insitu']['insitu_data2OCDBfile'] = 'AERONETOC'
config_params['insitu']['insitu_input'] = os.path.join(output_path, 'Chesapeake_Bay_OCDB.csv')
config_params['insitu']['insitu_satelliteTimeToleranceSeconds'] = 3600
config_params['insitu']['insitu_getAncillary'] = False 
config_params['insitu']['insitu_BRDF'] = 'M02' 

# satellite
config_params['satellite'] = {}
config_params['satellite']['satellite_path-to-SatData'] = os.path.join(output_path, 'SatData')
config_params['satellite']['satellite_source'] = 'NASA_OBPG'
config_params['satellite']['satellite_collections'] = 'operational'
config_params['satellite']['satellite_platforms'] = 'PACE'
config_params['satellite']['satellite_resolutions'] = 'FR'
config_params['satellite']['satellite_BRDF'] = 'M02'

# minifiles
config_params['minifiles'] = {}
config_params['minifiles']['minifiles_winSize'] = 5

# EDB
config_params['EDB'] = {}
config_params['EDB']['EDB_protocols_L2'] = 'Bailey_and_Werdell_2006'
config_params['EDB']['EDB_winSizes'] = 5

# MDB
config_params['MDB'] = {}
config_params['MDB']['MDB_time-interpolation'] = 'insitu2satellite_NN'
config_params['MDB']['MDB_stats_plots'] = True
config_params['MDB']['MDB_stats_protocol'] = 'Bailey_and_Werdell_2006'

# Write config_params sections into config_file.ini
write_config_file(path_to_config_file, config_params)
# -

# [back to top](#Contents)

# ## 3. Run ThoMaS

# Now, let's run this configuration and check our outputs

ThoMaS(path_to_config_file)

# If all went well, in our Chesapeake_Bay directory you should now have several folders that contain the outputs from the ThoMaS analysis:
# * SatData contains the full downloaded products
# * SatDataLists contains information on the inventory of downloaded data
# * minifiles contains the extracted minifiles
# * minifilesLists contains information on the inventory of downloaded data
# * EDB, the most important folder, contains the results of the extractions we made from the minifiles.
# * Summary plots of matchups

# [back to top](#Contents)


