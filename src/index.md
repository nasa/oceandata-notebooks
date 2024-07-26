# Jupyter Notebooks

## About

This collection of Jupyter notebooks is meant to help you get started accessing, visualizing, and analyzing
OB.DAAC data products with Python. You can learn from these notebooks either by viewing the code and results on this
webpage or by downloading the notebook files and running them with [JupyterLab][jupyterlab]. If you
plan to run any of these notebooks, please continue reading for information about the Earthdata Cloud and environments in Python.

### Earthdata Cloud

The **Earthdata Cloud** icon next to some notebooks indicates they are meant to be run using Amazon Web Services (AWS), which is the cloud provider used for NASA Earthdata Cloud. If you are not set up on AWS, you can still use those notebooks, but will need to download data as descibed below in the Data Access notebook. If you are new to using NASA Earthdata Cloud, the [Cloud Cookbook][cookbook] provides a lot of background and resources that are constantly being improved by the [NASA-Openscapes][openscapes] community.

**Can I use an existing AWS platform?** You may already have access to the AWS platform through your institution or research community. For example, JupyterHubs maintained by [Openscapes][openscapes-hub], [Cryo in the Cloud][cryocloud], [MAAP][maap], and NASA Goddard's [Open Science Studio][oss] are running on AWS in the same "us-west-2" region that hosts the NASA Earthdata Cloud. If that is not the case, you may want to learn about [getting started with AWS for NASA Earthdata Cloud][edcloud].

### Python Environments

The notebooks import Python packages that must be installed and discoverable on the host. Please use our
[environment.yml](../environment.yml) file to [create a Conda environment][conda-env] that satisfies all the dependencies,
or otherwise ensure your environment satisifes these dependencies. Note that the environment includes
the `ipykernel` package in case your JupyterLab includes [nb_conda_kernels][nb_conda_kernels] or you want
to manually [make the environment available to JupyterLab as a kernel][conda-kernel].

## Notebooks

### Learn with OCI

1. Data Access
1. **Earthdata Cloud** File Structure at Three Processing Levels
1. Installing and Running OCSSW Command-line Tools
1. Processing with OCSSW Tools: l2gen, l2bin, and l3mapgen
1. More comming soon!

### Learn with HARP2

1. **Earthdata Cloud** Data Visualization

### Learn with SpexONE

1. Coming soon!

### Learn with MODIS

1. Explore Level-2 Ocean Color Data
1. Explore Level-3 Ocean Color Data

[tutorials]: https://oceancolor.gsfc.nasa.gov/resources/docs/tutorials/
[jupyterlab]: https://jupyter.org/
[cookbook]: https://nasa-openscapes.github.io/earthdata-cloud-cookbook/
[openscapes]: https://nasa-openscapes.github.io/
[openscapes-hub]: https://openscapes.2i2c.cloud/
[cryocloud]: https://hub.cryointhecloud.com/
[maap]: https://scimaap.net/
[oss]: https://oss.smce.nasa.gov/
[edcloud]: https://www.earthdata.nasa.gov/learn/webinars-and-tutorials/cloud-primer-amazon-web-services
[conda-env]: https://conda.io/projects/conda/en/latest/user-guide/tasks/manage-environments.html#creating-an-environment-from-an-environment-yml-file
[nb_conda_kernels]: https://github.com/anaconda/nb_conda_kernels
[conda-kernel]: https://ipython.readthedocs.io/en/stable/install/kernel_install.html#kernels-for-different-environments
