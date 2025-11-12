# Getting Started

Many of our Help Hub resources are Jupyter notebooks that demonstrate accessing, visualizing,
and analyzing data products from NASA's {term}`Earthdata Cloud`.
You can learn from these notebooks either by viewing the code and results as displayed here,
or by downloading the notebooks for your own use in a local or cloud-hosted {term}`JupyterLab`.
If you are unfamiliar with the Earthdata Cloud or the {term}`Jupyter` project,
please read the information below for some important background.

:::{important}
Sign up for an [Earthdata Login][edl] acount for access to NASA Earthdata.
:::

## Earthdata Cloud

Data in NASA's Earthdata Cloud are distributed from Amazon Web Services (AWS) simple storage service (S3),
allowing users to freely access Earth observations either by download to their own computer or by direct access from other AWS platforms.
Direct access to the Earthdata Cloud from AWS is an *alternative* to downloading data;
this can benefit workflows that process a large amount of data or that require highly concurrent access to lots of different data.
We recommend the [NASA Earthdata Cloud Cookbook][cookbook], a resource maintained by the [NASA-Openscapes][nasa-openscapes] community,
for in-depth guidance on these topics.

{term}`JupyterHub` instances maintained by {term}`CryoCloud`, [Openscapes][openscapes-hub], [NASA MAAP][maap],
and NASA Goddard's [Open Science Studio][oss] are all examples of platforms operating in AWS with direct access to the Earthdata Cloud.
We encourage you to visit these organizations to learn about options for using these existing platforms.
Alternatively, you may want to learn about [getting started with AWS for Earth data][edcloud].

All tutorials in the Help Hub are applicable whether you plan to download data or access it directly from AWS.
The [Data Access](notebooks/oci/oci_data_access) notebook steps through differences between the two approaches in detail.

## Jupyter Setup

An advantage that comes with community-maintained JupyterHubs is having a complete Jupyter ecosystem at your fingertips.
Even so, the default configuration will not be capable of running all the Help Hub tutorials.
Here are two ways to get a Jupyter ecosystem that's ready to run them all:
  1. **On a bring-your-own-image capable JupyterHub**: run a {term}`container` built for CryoCloud
  1. **Without a JupyterHub**: run JupyterLab from a {term}`Conda` environment

For the first option, login to your JupyterHub and start a server from the `ghcr.io/nasa/oceandata-notebooks:latest` image.

```{image} images/custom-image.png
:alt: Start a server with the image
:width: 80%
:align: center
```

For the second option, download our {download}`conda-lock.yml <../container/conda-lock.yml>` configuration file,
which specifies exact versions of packages on {term}`Conda-Forge` and {term}`PyPI` that must be installed.
You need {term}`Mamba` available to create an environment from this configuration file;
you can use either the `mamba` command that comes with {term}`Conda` (recommended) or the [Micromamba][micromamba] distribution.
With that file in a download folder (denoted by `<DIR>`) and a name you've chosen (denoted by `<NAME>`) for a new environment, run in a Terminal:

```shell
mamba create --name <NAME> --file <DIR>/conda-lock.yml --category notebooks
mamba install --name <NAME> --file <DIR>/conda-lock.yml --category jupyter
```

If you are familiar with creating additional ipython kernels for an existing Jupyter server, you can skip the installs from `--category jupyter` and do that instead.
Otherwise, start JupyterLab from within the new environment as follows, and try out any Help Hub notebook locally.

```shell
mamba run --name <NAME> jupyter lab
```

## Getting Help

Have a question or an idea? Share it with us on the [Earthdata Forum][forum] using tags OBDAAC (under DAAC) and Data Recipes (under Services/Usage).

[cookbook]: https://nasa-openscapes.github.io/earthdata-cloud-cookbook/
[cryocloud]: https://hub.cryointhecloud.com/
[edcloud]: https://www.earthdata.nasa.gov/learn/webinars-and-tutorials/cloud-primer-amazon-web-services
[edl]: https://urs.earthdata.nasa.gov/
[forum]: https://forum.earthdata.nasa.gov/viewforum.php?f=7&DAAC=86&ServicesUsage=16&tagMatch=all
[image]: https://github.com/nasa/oceandata-notebooks/pkgs/container/oceandata-notebooks
[maap]: https://scimaap.net/
[micromamba]: https://mamba.readthedocs.io/en/latest/installation/micromamba-installation.html
[nasa-openscapes]: https://nasa-openscapes.github.io/
[openscapes-hub]: https://openscapes.cloud/
[oss]: https://smce.nasa.gov/overview/
[tutorials]: https://oceancolor.gsfc.nasa.gov/resources/docs/tutorials/
