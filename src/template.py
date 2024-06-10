# # Title of the Tutorial
#
# **Authors:** First Last (NASA, ...), First Last (NASA, ...)
#
# <div class="alert alert-success" role="alert">
#
# **PREREQUISITES**
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
# Succinct description of the tutorial ...
#
# ## Learning Objectives
#
# At the end of this notebook you will know:
#
# - How to ...
# - What ...
#
# ## Contents
#
# 1. [Setup](#setup)
# 1. [Section Title](#section-name)
# 1. [Style Notes](#other-name)
#
# <a name="setup"></a>

# ## 1. Setup
#
# Begin by importing all of the packages used in this notebook. If your kernel uses an environment defined following the guidance on the [tutorials] page, then the imports will be successful.
#
# [tutorials]: https://oceancolor.gsfc.nasa.gov/resources/docs/tutorials/

# +
import os
from pathlib import Path

import earthaccess
# -

# Consider describing anything about the above imports, especially if a package must be installed [conda forge][conda] rather than from [PyPI][pypi].
#
# Also define any functions or classes used in the notebook.
#
# [conda]: https://anaconda.org/conda-forge/earthaccess
# [pypi]: https://pypi.org/project/earthaccess/
#
# [back to top](#contents) <a name="section-name"></a>

# ## 2. Section Title
#
# When using alerts, like the one below, those blank lines are needed.
#
# <div class="alert alert-info" role="alert">
#     
# The `persist=True` argument ensures any discovered credentials are
# stored in a `.netrc` file, so the argument is not necessary (but
# it's also harmless) for subsequent calls to `earthaccess.login`.
#
# </div>

auth = earthaccess.login(persist=True)

# [back to top](#contents) <a name="other-name"></a>

# ## 3. Style Notes
#
# Some recomendations for consistency between notebooks, and a good user experience:
#
# - avoid code cells much longer than twenty lines
# - avoid code cells with blank lines (except where preferred by PEP 8)
# - prefer a whole markdown cell, with full descriptions, over inline code comments
# - avoid splitting markdown cells that are adjacent
# - remove any empty cell at the end of the notebook
#
# Here are the two additional "alert" boxes used in some notebooks to help you choose between "success", "danger", "warning", and "info".
#
# <div class="alert alert-warning" role="alert">
#
# Anywhere in any of [these notebooks][tutorials] where `paths = earthaccess.open(...)` is used to read data directly from the NASA Earthdata Cloud, you need to substitute `paths = earthaccess.download(..., local_path)` before running the notebook on a local host or a remote host that does not have direct access to the NASA Earthdata Cloud.
#
# </div>
#
# <div class="alert alert-danger" role="alert">
#     
# Conda uses a lot of memory while configuring your environment. Choose an option with more than about 5GB of RAM from the JupyterHub Control Panel, or your install will fail.
#
# </div>

# [back to top](#contents)
#
# <div class="alert alert-info" role="alert">
#
# You have completed the notebook on downloading and opening datasets. We now suggest starting the notebook on ...
#
# </div>
