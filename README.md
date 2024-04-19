# Oceandata Notebooks

A repository for notebooks delivered as [oceandata tutorials and data recipes][tutorials].

## For Contributors

> [!IMPORTANT]
> - Edit notebooks in JupyterLab so Jupytext can do its magic.
> - Create new notebooks in the `notebooks/` folder.
> - Open notebooks found only in the `src/` folder with **Open With** -> **Notebook** from the "right-click"
>    menu. Save and close the notebook. The notebook will now exist in the `notebooks/` folder.

Keeping notebooks in a code repository presents challenges for collaboration and curation,
because notebooks can contain very large blobs of binary outputs and they also include
constantly changing metadata. This repository contains ".py" files that the [Jupytext extension][jupytext]
synchronizes with notebooks (".ipynb" files) in your working tree. The ".py" files live
in the `src/` folder and are commited to the repository. The paired ".ipynb" files live
in the `notebooks/` folder and are ignored by the repository. Other than the steps above,
just work on the ".ipynb" files, save your changes, and commit normally (well, almost ... git
only tracks the paired ".py" files and ignores the ".ipynb" files, so commit the ".py" files).

## For Users

> [!NOTE]
> This section should be treated as source material displayed on the [webpage][tutorials] as the first section.

### Getting Started

This collection of Jupyter notebooks is meant to help you get started accessing, visualizing, and analyzing
our data products with Python. You can learn from these notebooks either by viewing them on this site
(which includes code cell outputs) or by downloading (without code cell outputs) and using them with a suitable
editor (e.g. [JupyterLab][jupyterlab]). If you want to execute the code cells, please read on about two considerations
for the environment or runtime the notebooks expect.

First, notebooks with a **Earthdata Cloud** banner are written to run on a host in the AWS "us-west-2" region, which
is the region where the data are stored. You may already have access to such a host, for instance through a JupyterHub
maintained by [Openscapes][openscapes-hub], [Cryo in the Cloud][cryocloud], or [NASA SMCE][smce]. If you are new to
using NASA Earthdata Cloud, the [Cloud Cookbook][cookbook] provides a lot of background and resources and is constantly
being improved by the [NASA-Openscapes][openscapes] community. 

Second, the notebooks import Python packages that must be installed and discoverable on the host. 

## For Maintainers

**WIP**: Resolve a number of maintenance tasks:

1. Curating environment lock files for both conda and python virtual environments
2. Formatting notebooks with black
3. Testing notebooks in isolated environments (using `jupyter execute ...`)

[tutorials]: https://oceancolor.gsfc.nasa.gov/resources/docs/tutorials/
[jupytext]: https://jupytext.readthedocs.io/
[cookbook]: https://nasa-openscapes.github.io/earthdata-cloud-cookbook/
[openscapes]: https://nasa-openscapes.github.io/
[openscapes-hub]: https://openscapes.2i2c.cloud/
[cryocloud]: https://hub.cryointhecloud.com/
[smce]: https://oss.smce.nasa.gov/
[jupyterlab]: https://jupyter.org/
