# # Access Data from the Ocean Color Instrument (OCI)
#
# **Authors:** Anna Windle (NASA, SSAI), Ian Carroll (NASA, UMBC), Carina Poulin (NASA, SSAI)
#
# > **PREREQUISITES**
# >
# > This notebook has the following prerequisites:
# > - An **<a href="https://urs.earthdata.nasa.gov/" target="_blank">Earthdata Login</a>**
# >   account is required to access data from the NASA Earthdata system, including NASA ocean color data.
# > - ...
#
# ## Summary
#
# Lorem ipsum dolor sit amet ...
#
# ## Learning Objectives
#
# At the end of this notebook you will know:
#
# * ...
#
# <a name="toc"></a>
# ## Contents
#
# 1. [Setup](#setup)
# 1. [Section Title](#slug)
#
# <a name="setup"></a>
# ## 1. Setup
#
# [tutorials]: https://oceancolor.gsfc.nasa.gov/resources/docs/tutorials
# [conda]: https://anaconda.org/conda-forge/earthaccess
# [pypi]: https://pypi.org/project/earthaccess/

import earthaccess

# [Back to top](#toc)
# <a name="slug"></a>
# ## 2. Section Title
#
# Lorem ipsum dolor sit amet ...
#
# <div class="alert alert-info" role="alert">
# The <code>persist=True</code> argument ensures any discovered credentials are
# stored in a <code>.netrc</code> file, so the argument is not necessary (but
# it's also harmless) for subsequent calls to <code>earthaccess.login</code>.
# </div>

auth = earthaccess.login(persist=True)

# <div class="alert alert-info" role="alert">
# <p>You have completed the notebook on downloading and opening datasets. We now suggest starting the notebook on ...</p>
# </div>


