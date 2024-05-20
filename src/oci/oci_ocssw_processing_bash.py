# # Installing and Running the OCSSW Command Line Interface (CLI)
#
# **Authors:** Carina Poulin (NASA, SSAI), Ian Carroll (NASA, UMBC), Anna Windle (NASA, SSAI)
#
# > **PREREQUISITES**
# >
# > This notebook has the following prerequisites:
# > - An **<a href="https://urs.earthdata.nasa.gov/" target="_blank">Earthdata Login</a>**
# >   account is required to access data from the NASA Earthdata system, including NASA ocean color data.
# > - "Learn with OCI"/"Data Access"
#
# ## Summary
#
# [SeaDAS][seadas] is the official data analysis sofware of NASA's Ocean Biology Distributed Active Archive Center (OB. DAAC); used to process, display and analyse ocean color data. SeaDAS is a dektop application that includes SeaDAS-OCSSW, the core libraries or data processing components. There is a CLI for the SeaDAS-OCSSW data processing components, known simply as OCSSW, which we can use on a remote host without a desktop.
#
# This tutorial will show you how to install OCSSW on a JupyterHub server and how to start doing data processing by processing a Level 1b (L1B) file from PACE OCI to a Level 2 (L2) file using `l2gen`.
#
# ## Learning Objectives
#
# At the end of this notebok you will know:
# * How to install OCSSW on your server
# * How to set up your OCSSW session
# * How to process a L1B file to L2 using l2gen
#
# <a name="toc"></a>
# ## Contents
#
# 1. [Setup](#setup)
# 1. [Install OCSSW](#ocssw)
# 1. [Process Data with `l2gen`](#l2gen)
#      
# <a name="setup"></a> 
# ## 1. Setup
#
# <div class="alert alert-warning" role="alert">
# This tutorial is written in a Jupyter notebook connected to a Bash kernel. If you have downloaded this Jupyter notebook and want to run it, you also need to connected it to a Bash kernel. Alternatively, you can copy the code cells to the Terminal application found in the JupyterLab Launcher, which speaks Bash or something close enough.
# </div>
#
# ### (Optional) Use a Bash Kernel
#
# Run the following command. If the terminal asks you to update conda, type Y to accept.
#
#
# [seadas]: https://seadas.gsfc.nasa.gov/

# %conda install bash_kernel

# Follow the prompts from conda to proceed with any installs and updates by entering "y" to accept.
#
# Confirm the bash kernel is installed by starting a new Launcher. You should see the bash kernel along with Python and other kernels installed in your JupyterHub.
#
# Restart the kernel (refresh button on the upper-right of the kernel window).
#
# ### Change your notebook kernel to Bash
#
# You should now change the kernel of the notebook by clicking on the kernel name in the upper-right corner of the window and selecting the Bash kernel before moving on to the rest of the tutorial. 

# [Back to top](#toc)
# <a name="ocssw"></a>
# ## 2. Install OCSSW
#
# The OCSSW software is not a Python package and not available from `conda` or any other repository. To install it, we begin by aquiring an installer script from the Ocean Biology DAAC. This script is actually part of OCSSW, but we can use it independently to download and install the OCSSW binaries suitable for our system.

wget https://oceandata.sci.gsfc.nasa.gov/manifest/install_ocssw

# Similarly, we'll need the manifest module imported by the installer.

wget https://oceandata.sci.gsfc.nasa.gov/manifest/manifest.py

# Before you can use a downloaded script, you need to change its mode to be executable.

chmod +x install_ocssw

# Take a look at the different OCSSW "tags" you can install. It is recommended to use the most recent one for the installation, which is T2024.16 at the time of writing this tutorial. 

# + scrolled=true
./install_ocssw --list_tags
# -

# Define an environmental variable called "OCSSWROOT" that specifies a directory for your OCSSW installation. Environment variables are set in Bash using the `export` command, and displayed with `printenv`

export OCSSWROOT=/tmp/ocssw

printenv OCSSWROOT

# <div class="alert alert-info" role="alert">
# You will need to repeat these installation steps if your OCSSWROOT directory does not persist between sessions. The `/tmp/ocssw` folder, for instance, will not be present the next time JupyterHub creates a server. Consider the trade off between installation time, speed, and storage costs when choosing your OCSSWROOT. We use the quick and cheap location for this tutorial.
# </div>

# Install OCSSW using the `--tag` argument to pick from the list above. Also provide optional arguments for sensors you will be working with. In this case, we will only be using OCI. A list of optional arguments can be found on the OCSSW webpage or with `./install_ocssw --help`.
#
# *Tip:* The process is not finished as long as the counter to the left of the cell shows `[*]`. It may take some time to install all the tools.

./install_ocssw --tag=T2024.16 --seadas --oci

# Finish up by calling `source` on the "OCSSW_bash.env" file, which exports additional environment variables. This environment file specifies the locations of all files required by OCSSW, and must be exported in every Terminal or Bash kernel before you run `l2gen` or any other OCSSW command.

source $OCSSWROOT/OCSSW_bash.env

# Confirm the environment has been set by checking that *another* `install_ocssw` script is now discoverable by Bash at the newly installed location.

which install_ocssw

# You are now ready to run `l2gen`, the Level-2 processing function for all ocean color instruments under the auspices of the GSFC Ocean Biology Processing Group!

# [Back to top](#toc)
# <a name="l2gen"></a>
# ## 3. Process L1B Data with `l2gen`
#
# Run `l2gen` by itself to view the extensive list of options available. You can find more information [on the seadas website][docs].
#
# [docs]: https://seadas.gsfc.nasa.gov/help-8.3.0/processors/ProcessL2gen.html

# + scrolled=true
l2gen
# -

# Feel free to explore all of `l2gen` options to produce a highly customized Level-2 dataset for your research. Here we just scratch the surface.
#
# To process a L1B file using `l2gen` you need, at a minimum, to set an input file name (`ifile`) and an output file name (`ofile`). You can also indicate a data suite; in this example, we will proceed with the Surface Reflectance suite used to make true color images (SFREFL). We turn off the atmospheric correction with the `atmocor` to save processing time.
#
# Confirm that the L1B file to process is at the expected location by listing (with `ls`) the directory contents. If the directory is empty, check that you've completed the prerequiste notebooks for this tutorial!

# ls L1B

# Create a directory for output files.

# mkdir L2

# + scrolled=true
l2gen \
  ifile=L1B/PACE_OCI.20240501T165311.L1B.nc \
  ofile=L2/PACE_OCI.20240501T165311.L2.SFREFL.nc \
  suite=SFREFL \
  atmocor=0
# -

# <div class="alert alert-info" role="alert">
# <p>You have completed the notebook on installing OCCSW to process PACE data. More notebooks are comming soon!</p>
# </div>
