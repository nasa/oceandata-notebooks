# ---
# jupyter:
#   jupytext:
#     text_representation:
#       extension: .py
#       format_name: light
#       format_version: '1.5'
#       jupytext_version: 1.16.1
#   kernelspec:
#     display_name: Bash
#     language: bash
#     name: bash
# ---

# # Using OCSSW functions (l2gen) using Jupyter notebooks
#
# **Authors:** Carina Poulin (NASA, SSAI), Ian Carroll (NASA, UMBC), Anna Windle (NASA, SSAI)
#
# > **PREREQUISITES**
# >
# > This notebook has the following prerequisites:
# > - An **<a href="https://urs.earthdata.nasa.gov/" target="_blank">Earthdata Login</a>**
# >   account is required to access data from the NASA Earthdata system, including NASA ocean color data.
# > - There are no prerequisite notebooks for this module.
#
# ## Summary
# ***
# [SeaDAS][seadas] is the official data analysis sofware of NASA's Ocean Biology Distributed Active Archive Center (OB. DAAC), used to process, display and analyse ocean color data. A GUI-based SeaDAS application is available, and it can be used through command line. SeaDAS's processing components found in the OCSSW package. 
#
# This tutorial will show you how to install OCSSW in a JupyterHub server and how to start doing data processing by processing a Level 1b (L1B) file from PACE OCI to a Level 2 (L2) file using L2gen.  
#
# ## Learning Objectives
# ***
# <a name="toc"></a>
# At the end of this notebok you will know:
# * How to install OCSSW on your server
# * How to set up your OCSSW session
# * How to download a L1B file to your server
# * How to process a L1B file to L2 using l2gen
#
# ## Contents
# ***
# 1. [Initial Setup](#setup)
# 2. [Install OCSSW](#ocssw)
# 3. [Get L1B data](#data)
# 4. [Process data with l2gen](#l2gen)
#      
# ## 1. Setup <a name="setup"></a> 
# *** 
#
# <div class="alert alert-warning" role="alert"> Important! This tutorial requires a Bash kernel. 
#     
#     OCSSW uses the Bash language. If there is not already a Bash kernel in your JupyterHub launcher, you need to install it before doing anything *every time you launch the notebook.* Thankfully, it is easy to do with the instructions below. 
# </div>
#
# ### Install a Bash Kernel
#
# Open a terminal window and make sure you are working in the notebook. Install the bask kernel with:
#
# ```conda install bash_kernel```
#
# If the terminal asks you to update conda, type Y to accept.
#
# Confirm the bash kernel is installed by starting a new Launcher. You should see the bash kernel along with Python, the Terminal and other kernels installed in your Hub.
#
# ### Change you notebook kernel to Bash
#
# You should now change the kernel of the notebook by clicking on the kernel name in the upper-right corner of the window and selecting the Bash kernel before moving on to the rest of the tutorial. 
#
# [seadas]: https://seadas.gsfc.nasa.gov/

# ## 2. Install OCSSW <a name="ocssw"></a>
# ***
#
# <div class="alert alert-info" role="alert"> 
# You should only need to install OCSSW on your server once. Once installed, you will see the ocssw folder in your files and it will remain there when you relaunch the notebook. 
# </div>
#
# You first need to indicate the directory where you want to install ocssw:

cd /home/jovyan/ocssw

# Then download the OCSSW installer to your server

wget https://oceandata.sci.gsfc.nasa.gov/manifest/install_ocssw

# and the manifest script

wget https://oceandata.sci.gsfc.nasa.gov/manifest/manifest.py

# Then you need to change permissions to the files (chmod). Take a look at the different OCSSW tags you can install. It is recommended to use the most recent one for the installation, which is T2024.16 at the time of writing this tutorial. 

chmod +x install_ocssw
./install_ocssw --list_tags

# Install OCSSW using the tag you chose above. Choose the sensors you will be working with. In this case, we will be using OCI. A list of optional arguments can be found on the OCSSW webpage. 
#
# It may take some time to install all the packages. *Tip:* The process is not finished as long as the brackets on the left of the cell show [ * ]. 

./install_ocssw --install_dir ocssw --tag T2024.16 --seadas --oci

# <div class="alert alert-info" role="alert">
# You have installed OCSSW! You won't need to redo this step as long as you keep the OCSSW folder on your server. 
# </div>
#

# ## 3. Get OCI Level 1B data <a name="data"></a>
# ***

# Create a file called .netrc by **substituting LOGIN and PASSWORD** below for your own login and password before running the cell.

echo "machine urs.earthdata.nasa.gov login LOGIN password PASSWORD" > ~/.netrc ; > ~/.urs_cookies 
chmod  0600 ~/.netrc

# Download a Level 1B file using the cookies from the previous step for your earthdata credentials.

wget --load-cookies ~/.urs_cookies \
--save-cookies ~/.urs_cookies \
--auth-no-challenge=on \
--content-disposition 'https://oceandata.sci.gsfc.nasa.gov/getfile/PACE_OCI.20240427T161654.L1B.nc'

# ## 4. Process L1B data with l2gen <a name="l2gen"></a>
# ***
# ### Set up OCSSW's l2gen

# Define an environmental variable called OCSSWROOT that points to your OCSSW software installation using the export command.

export OCSSWROOT=ocssw

# Confirm the installation. You should see the path to OCSSSW. 

# +

printenv OCSSWROOT
# -

# Finish setting up the command line environment by sourcing the data processing environmental variable file. This file defines the locations of all files required by OCSSW. 

source $OCSSWROOT/OCSSW_bash.env

# Confirm the environment has been set. You should see the path to l2gen. 

which l2gen

# You are now ready to run l2gen, the Level-2 processing function for all ocean color instruments under the auspices of the GSFC Ocean Biology Processing Group!

# ### Run l2gen

# Run l2gen by itself to view the extensive list of options available. You can find more information [on the seadas website](https://seadas.gsfc.nasa.gov/help-8.3.0/processors/ProcessL2gen.html)

l2gen

# To process a L1B file using L2gen, at a minimum, you need to set an infile name (ifile) and an outfile name (ofile). You can indicate a data suite, in this example, we will proceed with the Surface Reflectance suite used to make true color images (SFREFL). We are turning off the atmospheric correction here to save processing time. 
#
# Feel free to explore l2gen options to produce the level 2 dataset you need. 

l2gen ifile=/home/jovyan/ocssw_test/PACE_OCI.20240427T161654.L1B.nc \
ofile=/home/jovyan/ocssw_test/PACE_OCI.20240427T161654_test.L2.nc \
suite=SFREFL \
atmocor=0

# <div class="alert alert-info" role="alert">
# <p>You have completed the notebook on using OCCSW to process PACE data in Jupyter notebooks. More notebooks are comming soon!</p>
# </div>


