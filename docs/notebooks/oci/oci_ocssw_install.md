---
jupytext:
  text_representation:
    extension: .md
    format_name: myst
    format_version: 0.13
    jupytext_version: 1.17.2
kernelspec:
  name: bash
  display_name: Bash
  language: bash
---

# Installing and Running OCSSW Command-line Tools

**Author(s):** Carina Poulin (NASA, SSAI), Ian Carroll (NASA, UMBC), Anna Windle (NASA, SSAI)

Last updated: August 3, 2025

<div class="alert alert-success" role="alert">

The following notebooks are **prerequisites** for this tutorial.

- Learn with OCI: [Data Access][oci-data-access]

</div>

<div class="alert alert-info" role="alert">

An [Earthdata Login][edl] account is required to access data from the NASA Earthdata system, including NASA ocean color data.

</div>

[edl]: https://urs.earthdata.nasa.gov/
[oci-data-access]: https://oceancolor.gsfc.nasa.gov/resources/docs/tutorials/notebooks/oci_data_access/

## Summary

[SeaDAS][seadas] is the official data analysis sofware of NASA's Ocean Biology Distributed Active Archive Center (OB.DAAC); used to process, display and analyse ocean color data. SeaDAS is a dektop application that includes the Ocean Color Science Software (OCSSW) libraries. There are also command line programs for the OCSSW libraries, which we can use to write processing scripts or notebooks. This tutorial will show you how to install OCSSW and test it by processing a Level-1B (L1B) file from PACE OCI to a Level-2 (L2) file using `l2gen`. The installation can find OCSSW tools that work on modern Linux and macOS operating systems but not Windows.

[seadas]: https://seadas.gsfc.nasa.gov/

## Learning Objectives

At the end of this notebok you will know:
* How to install OCSSW on your server
* How to set up your OCSSW session
* How to process a L1B file to L2 using l2gen

+++

## 1. Setup

<div class="alert alert-info" role="alert">

This tutorial is written in a Jupyter notebook connected to a Bash kernel. If you have downloaded this Jupyter notebook and want to run it, you also need to connected it to a Bash kernel. Alternatively, you can copy the code cells to the Terminal application found in the JupyterLab Launcher, which speaks Bash or something close enough.

</div>

### (Optional) Use a Bash Kernel

<div class="alert alert-danger" role="alert">

Conda uses a lot of memory while configuring your environment. Choose an option with more than about 5GB of RAM from the JupyterHub Control Panel, or your install will fail.

</div>

Convert the following cell from type "Raw" to "Code", using the notebook menu, and run it. If the terminal prompts you, enter "Y" to accept.

```{raw-cell}
:scrolled: true
:tags: [scroll-output]

%conda install bash_kernel
```

Follow the prompts from conda to proceed with any installs and updates. If prompted, enter "y" to accept.

Confirm the bash kernel is installed by starting a new Launcher. You should see the bash kernel along with Python and other kernels installed in your JupyterHub. You should now **change the kernel of the notebook** by clicking on the kernel name in the upper-right corner of the window and selecting the Bash kernel before moving on to the rest of the tutorial.

+++

## 2. Install OCSSW

The OCSSW software is not a Python package and not available from `conda` or any other repository. To install it, we begin by aquiring an installer script from the OB.DAAC. This script is actually part of OCSSW, but we can use it independently to download and install the OCSSW binaries suitable for our system.

```{code-cell}
wget --quiet --no-clobber https://oceandata.sci.gsfc.nasa.gov/manifest/install_ocssw
```

Similarly, we'll need the manifest module imported by the installer.

```{code-cell}
wget --quiet --no-clobber https://oceandata.sci.gsfc.nasa.gov/manifest/manifest.py
```

Before you can use a downloaded script, you need to change its mode to be executable.

```{code-cell}
chmod +x install_ocssw
```

Take a look at the different OCSSW "tags" you can install. It is recommended to use the most recent one for the installation, which is T2024.16 at the time of writing this tutorial. Tags starting with "V" are operational versions, and tags starting with "T" are test versions. Use "T" to process the latest data products, but keep in mind that processing can change a lot between tags. Other tags are deprecated, including those starting with "R".

```{code-cell}
:scrolled: true
:tags: [scroll-output]

./install_ocssw --list_tags
```

```{code-cell}
export TAG="$(./install_ocssw --list_tags | grep '^V' | tail -n 1)"
printenv TAG
```

Define an environmental variable called "OCSSWROOT" that specifies a directory for your OCSSW installation. Environment variables are persisted in Bash using the `export` command, but we are carefull not to overwrite any existing value for `OCSSWROOT`.

```{code-cell}
export OCSSWROOT=${OCSSWROOT:-/tmp/ocssw}
```

<div class="alert alert-warning" role="alert">

You will need to repeat these installation steps (see below) if your OCSSWROOT directory does not persist between sessions.

</div>

The `/tmp/ocssw` folder, for instance, will not be present the next time JupyterHub creates a server. Consider the trade off between installation time, speed, and storage costs when choosing your `OCSSWROOT`. With the arguments below, the installation takes 11GB of storage space. We use the quick and cheap location for this tutorial.

Install OCSSW using the `--tag` argument to pick from the list above. Also provide optional arguments for sensors you will be working with. In this case, we will only be using OCI. A list of optional arguments can be found on the OCSSW webpage or with `./install_ocssw --help`.

*Tip:* The process is not finished as long as the counter to the left of the cell shows `[*]`. It will take some time to install all the tools (7 of 7 installations).

```{code-cell}
:tags: [skip-execution]

./install_ocssw --tag=$TAG --seadas --oci
```

Finish up by calling `source` on the "OCSSW_bash.env" file, which exports additional environment variables. This environment file specifies the locations of all files required by OCSSW, and must be exported in every Terminal or Bash kernel before you run `l2gen` or any other OCSSW command.

```{code-cell}
source $OCSSWROOT/OCSSW_bash.env
```

Confirm the environment has been set by checking whether `l2gen` is now discoverable by Bash.
If the following creates an error, check for [instructions] that might be specific to your operating system.

[instructions]: https://seadas.gsfc.nasa.gov/downloads/

```{code-cell}
l2gen --version
```

You are now ready to run `l2gen`, the Level-2 processing function for all ocean color instruments under the auspices of the GSFC Ocean Biology Processing Group!

+++

## 3. All-in-One

In case you need to run the sequence above in a terminal regularly, here are all the commands
to run together.

If you are starting from scratch ...

```{code-cell}
:tags: [skip-execution]

wget -q -nc https://oceandata.sci.gsfc.nasa.gov/manifest/install_ocssw
wget -q -nc https://oceandata.sci.gsfc.nasa.gov/manifest/manifest.py
chmod +x install_ocssw
export OCSSWROOT=${OCSSWROOT:-/tmp/ocssw}
export TAG="$(./install_ocssw --list_tags | grep '^V' | tail -n 1)"
./install_ocssw --tag=$TAG --seadas --oci
```

If you have already installed OCSSW and want to update ...

```{code-cell}
:tags: [skip-execution]

export OCSSWROOT=${OCSSWROOT:-/tmp/ocssw}
export TAG="$(install_ocssw --list_tags | grep '^V' | tail -n 1)"
install_ocssw --tag=$TAG --seadas --oci
```

<div class="alert alert-info" role="alert">

You have completed the notebook on installing OCCSW. Check out the notebook on Processing with OCSSW Tools.

</div>
