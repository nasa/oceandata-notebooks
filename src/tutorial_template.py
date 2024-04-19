# ---
# jupyter:
#   jupytext:
#     text_representation:
#       extension: .py
#       format_name: light
#       format_version: '1.5'
#       jupytext_version: 1.16.1
#   kernelspec:
#     display_name: Python 3 (ipykernel)
#     language: python
#     name: python3
# ---

# <table><tr>
#
#
# <td> <img src="https://oceancolor.gsfc.nasa.gov/images/ob-logo-svg-2.svg" alt="Drawing" align='right', style="width: 240px;"/> </td>
#
# <td> <img src="https://www.nasa.gov/wp-content/uploads/2023/04/nasa-logo-web-rgb.png" align='right', alt="Drawing" style="width: 70px;"/> </td>
#
# </tr></table>

# <font color="dodgerblue">**Ocean Biology Processing Group**</font> <br>
# **Copyright:** 2024 NASA OBPG <br>
# **License:** MIT <br>
# **Authors:** Anna Windle (NASA/SSAI), Ian Carroll (NASA/UMBC)

# <div class="alert alert-block alert-warning">
#     
# **PREREQUISITES** 
#     
# This notebook has the following prerequisites:
# - **<a href="XX">XX.ipynb</a>**
# </div>
#
# <hr>

# # Title

# ## Learning objectives
#
# At the end of this notebok you will know:
# * X
# * X
# * X
#
# ## Outline
# In this example we will ....
#
#
# <div class="alert alert-info" role="alert">
#
# ## <a id='TOC_TOP'>Contents
#
# </div>
#     
#  1. [X](#section2)
#  2. [X](#section3)
#  3. [X](#section4)
#
# <hr>

# We begin by importing all of the libraries that we need to run this notebook. If you have built your python using the environment file provided in this repository, then you should have everything you need. For more information on building environment, please see the repository README.

import X as X
import X as X

# ## `earthaccess` authentication

auth = earthaccess.login()
# are we authenticated?
if not auth.authenticated:
    # ask for credentials and persist them in a .netrc file
    auth.login(strategy="interactive", persist=True)

# <div class="alert alert-info" role="alert">
#
# ## <a id='section1'>1. "Content title 1"
# [Back to top](#TOC_TOP)
#
# </div>

# <div class="alert alert-info" role="alert">
#
# ## <a id='section2'>2. Content title 2
# [Back to top](#TOC_TOP)
#
# </div>

# <div class="alert alert-info" role="alert">
#
# ## <a id='section2'>2. Content title 3
# [Back to top](#TOC_TOP)
#
# </div>

#
# <a href="https://oceancolor.gsfc.nasa.gov/" target="_blank">NASA Ocean Color website</a> | <a href="https://oceancolor.gsfc.nasa.gov/resources/docs/tutorials/" target="_blank">NASA Ocean Color Tutorials</a></span></p>


