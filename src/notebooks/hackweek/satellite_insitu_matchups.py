# # Matchups of ocean color products with OCI
#
# **Authors:** Anna Windle (NASA, SSAI)
#
# <div class="alert alert-success" role="alert">
#
# The following notebooks are **prerequisites** for this tutorial.
#
# - Learn with OCI: [Data Access][oci-data-access]
#
# </div>
#
# <div class="alert alert-info" role="alert">
#
# An [Earthdata Login][edl] account is required to access data from the NASA Earthdata system, including NASA ocean color data.
#
# </div>
#
# [edl]: https://urs.earthdata.nasa.gov/
# [oci-data-access]: https://oceancolor.gsfc.nasa.gov/resources/docs/tutorials/notebooks/oci_data_access/
#
# ## Summary
#
# In this example we will conduct matchups of in situ data with OCI satellite data using the ThoMaS (Tool to generate Matchups for OC products with Sentinel-3/OLCI) package. This package provides a comprehensive set of tools to help with the validation of satellite products, supporting many common workflows including:
#
# * satellite data acquisition
# * mini file extraction
# * in situ data management
# * BRDF correction
#
# ThoMaS is written in Python and is made available through a [EUMETSAT Gitlab repository](https://gitlab.eumetsat.int/eumetlab/oceans/ocean-science-studies/ThoMaS). The package can be used from the command line, or imported as a Python library, as done here. This notebook contains 3 examples of how to use ThoMaS in various ways, but the capability shown is not exhaustive. Many more command-line examples are included in the repository, and we encourage users to familiarise themselves with both the [project README](https://gitlab.eumetsat.int/eumetlab/oceans/ocean-science-studies/ThoMaS/-/blob/main/README.md) and  [example README](https://gitlab.eumetsat.int/eumetlab/oceans/ocean-science-studies/ThoMaS/-/blob/main/README_examples.md) for more information.
#
# ## Learning Objectives
#
# At the end of this notebook you will know:
# * How to use thte ThoMaS toolkit to perform OCI match-up validation extractions and analyses. 
# * X
# * X
#
# ## Contents 
#
# 1. [Setup](#setup)
# 1. [XX]
#
# <a name="setup"></a>

# ## 1. Setup
#
# Begin by importing all of the packages used in this notebook. If your kernel uses an environment defined following the guidance on the [tutorials] page, then the imports will be successful.
#
# [tutorials]: https://oceancolor.gsfc.nasa.gov/resources/docs/tutorials

# +
import earthaccess

import os
import sys
import pandas as pd
import shutil
import numpy as np
# -

# The first thing we need to do is retrieve the tool kit itself. We can do this using the external ! git clone command. This will create a directory called ThoMaS in this path and make the code available for import.

pwd

os.path.join("shared", "pace-hackweek-2024", "ThoMaS", "main.py")


if os.path.exists(os.path.join("shared", "pace-hackweek-2024", "ThoMaS", "main.py")):
    print("ThoMaS is already installed.")
else:
    # ! git clone https://gitlab.eumetsat.int/eumetlab/oceans/ocean-science-studies/ThoMaS.git

# Before you use ThoMas, you must ensure that you have have completed the following two steps:
# 1. Ensure that you have all the Python dependencies you need to run ThoMaS. If you have installed and activated the **cmts_learn_olci** environment then you are all set.
# 2. Ensure that ThoMaS can access the EUMETSAT Data Store, which you can do by completing the **"EUMDAC"** section of the set credentials notebook.
#
# ThoMaS can be used from the [command line](https://gitlab.eumetsat.int/eumetlab/oceans/ocean-science-studies/ThoMaS/-/blob/main/README_examples.md), but here we will use it as a Python library. Lets import ThoMaS into our notebook.

sys.path.append("ThoMaS")
from main import ThoMaS_main as ThoMaS

# Set (and persist to your user profile on the host, if needed) your Earthdata Login credentials.

auth = earthaccess.login(persist=True)

# [back to top](#contents) <a name="l1b"></a>

# ## 2. Open L2 OCI file
#
# Let's use `xarray` to open up a OCI L2 NetCDF file using `earthaccess`. We will use the same search method used in <a href="oci_file_structure.html">OCI File Structure</a>. Note that L2 files do not include cloud coverage metadata, so we cannot use that filter.

# +
tspan = ("2024-06-01", "2024-06-16")
bbox = (-76.75, 36.97, -75.74, 39.01)
clouds = (0, 50)

results = earthaccess.search_data(
    short_name="PACE_OCI_L2_AOP_NRT",
    temporal=tspan,
    bounding_box=bbox,
    cloud_cover=clouds,
)
# -

paths = earthaccess.open(results)


