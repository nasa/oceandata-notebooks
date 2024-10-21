# ---
# jupyter:
#   jupytext:
#     cell_metadata_filter: all,-trusted
#     notebook_metadata_filter: all,-kernelspec
#     text_representation:
#       extension: .py
#       format_name: light
#       format_version: '1.5'
#       jupytext_version: 1.16.4
#   language_info:
#     codemirror_mode: shell
#     file_extension: .sh
#     mimetype: text/x-sh
#     name: bash
# ---

# # Installing and Running OCSSW Command-line Tools
#
# **Authors:** Carina Poulin (NASA, SSAI), Ian Carroll (NASA, UMBC), Anna Windle (NASA, SSAI)
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
# [SeaDAS][seadas] is the official data analysis sofware of NASA's Ocean Biology Distributed Active Archive Center (OB.DAAC); used to process, display and analyse ocean color data. SeaDAS is a dektop application that includes the Ocean Color Science Software (OCSSW) libraries. There are also command line programs for the OCSSW libraries, which we can use to write processing scripts or notebooks. This tutorial will show you how to install OCSSW and test it by processing a Level-1B (L1B) file from PACE OCI to a Level-2 (L2) file using `l2gen`. The installation can find OCSSW tools that work on modern Linux and macOS operating systems but not Windows.
#
# [seadas]: https://seadas.gsfc.nasa.gov/
#
# ## Learning Objectives
#
# At the end of this notebok you will know:
# * How to install OCSSW on your server
# * How to set up your OCSSW session
# * How to process a L1B file to L2 using l2gen
#
# ## Contents
#
# 1. [Setup](#1.-Setup)
# 2. [Install OCSSW](#2.-Install-OCSSW)
# 3. [Process Data with `l2gen`](#3.-Process-Data-with-`l2gen`)
# 4. [All-in-One](#4.-All-in-One)

# ## 1. Setup
#
# <div class="alert alert-info" role="alert">
#
# This tutorial is written in a Jupyter notebook connected to a Bash kernel. If you have downloaded this Jupyter notebook and want to run it, you also need to connected it to a Bash kernel. Alternatively, you can copy the code cells to the Terminal application found in the JupyterLab Launcher, which speaks Bash or something close enough.
#
# </div>
#
# ### (Optional) Use a Bash Kernel
#
# <div class="alert alert-danger" role="alert">
#
# Conda uses a lot of memory while configuring your environment. Choose an option with more than about 5GB of RAM from the JupyterHub Control Panel, or your install will fail.
#
# </div>
#
# Convert the following cell from type "Raw" to "Code", using the notebook menu, and run it. If the terminal prompts you, enter "Y" to accept.

# + scrolled=true tags=["scroll-output"] active=""
# %conda install bash_kernel
# -

# Follow the prompts from conda to proceed with any installs and updates. If prompted, enter "y" to accept.
#
# Confirm the bash kernel is installed by starting a new Launcher. You should see the bash kernel along with Python and other kernels installed in your JupyterHub. You should now **change the kernel of the notebook** by clicking on the kernel name in the upper-right corner of the window and selecting the Bash kernel before moving on to the rest of the tutorial.
#
# [back to top](#Contents)

# ## 2. Install OCSSW
#
# The OCSSW software is not a Python package and not available from `conda` or any other repository. To install it, we begin by aquiring an installer script from the OB.DAAC. This script is actually part of OCSSW, but we can use it independently to download and install the OCSSW binaries suitable for our system.

wget https://oceandata.sci.gsfc.nasa.gov/manifest/install_ocssw

# Similarly, we'll need the manifest module imported by the installer.

wget https://oceandata.sci.gsfc.nasa.gov/manifest/manifest.py

# Before you can use a downloaded script, you need to change its mode to be executable.

chmod +x install_ocssw

# Take a look at the different OCSSW "tags" you can install. It is recommended to use the most recent one for the installation, which is T2024.16 at the time of writing this tutorial. Tags starting with "V" are operational versions, and tags starting with "T" are test versions. Use "T" to process the latest data products, but keep in mind that processing can change a lot between tags. Other tags are deprecated, including those starting with "R".

# + scrolled=true tags=["scroll-output"]
./install_ocssw --list_tags
# -

# Define an environmental variable called "OCSSWROOT" that specifies a directory for your OCSSW installation. Environment variables are set in Bash using the `export` command, and displayed with `printenv`

export OCSSWROOT=/tmp/ocssw

printenv OCSSWROOT

# <div class="alert alert-warning" role="alert">
#
# You will need to [repeat these installation steps](#all) if your OCSSWROOT directory does not persist between sessions.
#
# </div>
#
# The `/tmp/ocssw` folder, for instance, will not be present the next time JupyterHub creates a server. Consider the trade off between installation time, speed, and storage costs when choosing your OCSSWROOT. With the arguments below, the installation takes 11GB of storage space. We use the quick and cheap location for this tutorial.
#
# Install OCSSW using the `--tag` argument to pick from the list above. Also provide optional arguments for sensors you will be working with. In this case, we will only be using OCI. A list of optional arguments can be found on the OCSSW webpage or with `./install_ocssw --help`.
#
# *Tip:* The process is not finished as long as the counter to the left of the cell shows `[*]`. It will take some time to install all the tools (7 of 7 installations).

./install_ocssw --tag=T2024.19 --seadas --oci

# Finish up by calling `source` on the "OCSSW_bash.env" file, which exports additional environment variables. This environment file specifies the locations of all files required by OCSSW, and must be exported in every Terminal or Bash kernel before you run `l2gen` or any other OCSSW command.

source $OCSSWROOT/OCSSW_bash.env

# Confirm the environment has been set by checking that *another* `install_ocssw` script is now discoverable by Bash at the newly installed location.

which install_ocssw

# You are now ready to run `l2gen`, the Level-2 processing function for all ocean color instruments under the auspices of the GSFC Ocean Biology Processing Group!
#
# [back to top](#Contents)

# ## 3. Process L1B Data with `l2gen`
#
# Run `l2gen` by itself to view the extensive list of options available. You can find more information [on the Seadas website][docs].
#
# [docs]: https://seadas.gsfc.nasa.gov/help-8.3.0/processors/ProcessL2gen.html

# + scrolled=true tags=["scroll-output"]
l2gen
# -

# Feel free to explore all of `l2gen` options to produce a highly customized Level-2 dataset for your research. Here we just scratch the surface.
#
# To process a L1B file using `l2gen` you need, at a minimum, to set an input file name (`ifile`) and an output file name (`ofile`). You can also indicate a data suite; in this example, we will proceed with the Surface Reflectance suite used to make true color images (`SFREFL`). We turn off the atmospheric correction with `atmocor=0` to save processing time.
#
# For this example, we will be using the L1B file downloaded in the OCI Data Access notebook. Confirm that the L1B file to process is at the expected location by listing (with `ls`) the directory contents. If the directory is empty, check that you've completed the prerequiste notebooks for this tutorial!

# ls L1B

# Create a directory for output files.

# mkdir L2

# And run! Note, this may take several minutes.

# + scrolled=true tags=["scroll-output"]
l2gen \
  ifile=L1B/PACE_OCI.20240501T165311.L1B.nc \
  ofile=L2/PACE_OCI.20240501T165311.L2.SFREFL.nc \
  suite=SFREFL \
  atmocor=0
# -

# <div class="alert alert-success" role="alert">
#
# Scroll down in the output above to see updates on processing. Upon completion, you should have a new processed L2 file in your L2 folder.
#
# </div>
#
# [back to top](#Contents)

# ## 4. All-in-One
#
# In case you need to run the sequence above in a terminal regularly, here are all the commands
# to copy and run together. This assumes you already used `wget` to persist the install script
# and `manifest.json` in the current directory.

export OCSSWROOT=/tmp/ocssw
./install_ocssw --tag=T2024.19 --seadas --oci
source $OCSSWROOT/OCSSW_bash.env

# Or, if that assumption is wrong and you also need to `wget` those files, copy and run the following.

wget https://oceandata.sci.gsfc.nasa.gov/manifest/install_ocssw
wget https://oceandata.sci.gsfc.nasa.gov/manifest/manifest.py
chmod +x install_ocssw
export OCSSWROOT=/tmp/ocssw
./install_ocssw --tag=T2024.19 --seadas --oci
source $OCSSWROOT/OCSSW_bash.env

# [back to top](#Contents)
#
# <div class="alert alert-info" role="alert">
#
# You have completed the notebook on installing OCCSW. Check out the notebook on Processing with OCSSW Tools.
#
# </div>
