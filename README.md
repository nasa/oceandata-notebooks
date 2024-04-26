# Oceandata Notebooks

A repository for notebooks delivered as [oceandata tutorials and data recipes][tutorials].

## For Users

> [!NOTE]
> This "For Users" section should be delivered as content displayed on the [webpage][tutorials] as the first section.
> That page will (eventually) have notebook download links targeting the [docs](docs/) folder.

### About

This collection of Jupyter notebooks is meant to help you get started accessing, visualizing, and analyzing
OB.DAAC data products with Python. You can learn from these notebooks either by viewing the code and results on this
webpage or by downloading the notebook files and running them with [JupyterLab][jupyterlab]. If you
plan to run any of these notebooks, please continue reading for information about notebook dependencies.

### Before you Start

#### 1. The Cloud

The **Earthdata Cloud** icon next to some notebooks indicates they are meant to be run using Amazon Web Services (AWS), which is the cloud provider used for NASA Earthdata Cloud. If you are not set up on AWS, you can still use those notebooks, but will need to download data as descibed below in the Data Access notebook. If you are new to using NASA Earthdata Cloud, the [Cloud Cookbook][cookbook] provides a lot of background and resources that are constantly being improved by the [NASA-Openscapes][openscapes] community.

**How do I know if I have AWS cloud access?**

You may already have access to the AWS platform through your institution or research community. For example, JupyterHubs maintained by [Openscapes][openscapes-hub], [Cryo in the Cloud][cryocloud], and NASA Goddard's [Open Science Studio][oss] are running on AWS in the same "us-west-2" region that hosts the NASA Earthdata Cloud. If that is not the case, you may want to learn about [getting started with AWS for NASA Earthdata Cloud][edcloud].

#### 2. Python environment setup

The notebooks import Python packages that must be installed and discoverable on the host. Please use our
[environment.yml](./environment.yml) file to [create a Conda environment][conda-env] that satisfies all the dependencies,
or otherwise ensure your environment satisifes these dependencies. Note that the environment includes
the `ipykernel` package in case your JupyterLab includes [nb_conda_kernels][nb_conda_kernels] or you want
to manually [make the environment available to JupyterLab as a kernel][conda-kernel].

### Notebooks

#### Learn with OCI

1. Data Access
1. **Earthdata Cloud** File Structure at Three Processing Levels
1. more comming soon!

#### Learn with HARP2

1. under construction

#### Learn with SpexONE

1. under construction

#### Learn with MODIS

1. Map Level-2 Chlorophyll using `netcdf4`
1. Map Level-2 Chlorophyll using `xarray`
1. Map Level-3 Chlorophyll and Rrs using `xarray`

### How to Cite

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

## For Maintainers

**WIP**: Resolve a number of maintenance tasks:

1. Curating dependencies for virtualenv without duplicating environment.yml
2. Formatting notebooks with black
3. Testing notebooks in isolated environments (using `jupyter execute ...`)
4. Auto populate `docs/` using:
   ```
   jupyter nbconvert --ClearOutputPreprocessor.enabled=True --ClearMetadataPreprocessor.enabled=True --to=notebook --output-dir=docs
   ```
5. Auto populate somewhere using:
   ```
   jupyter nbconvert --ClearMetadataPreprocessor.enabled=True --to=html --output-dir=
   ```

### Acknowledgements
This repository has greatly benefited from works of multiple open-science projects, notably [Learn OLCI](https://github.com/wekeo/learn-olci/blob/main/README.md) and the [NASA EarthData Cloud Cookbook](https://nasa-openscapes.github.io/earthdata-cloud-cookbook/).


[edcloud]: https://www.earthdata.nasa.gov/learn/webinars-and-tutorials/cloud-primer-amazon-web-services
[nb_conda_kernels]: https://github.com/anaconda/nb_conda_kernels
[conda-kernel]: https://ipython.readthedocs.io/en/stable/install/kernel_install.html#kernels-for-different-environments
[conda-env]: https://conda.io/projects/conda/en/latest/user-guide/tasks/manage-environments.html#creating-an-environment-from-an-environment-yml-file
[tutorials]: https://oceancolor.gsfc.nasa.gov/resources/docs/tutorials/
[jupytext]: https://jupytext.readthedocs.io/
[cookbook]: https://nasa-openscapes.github.io/earthdata-cloud-cookbook/
[openscapes]: https://nasa-openscapes.github.io/
[openscapes-hub]: https://openscapes.2i2c.cloud/
[cryocloud]: https://hub.cryointhecloud.com/
[oss]: https://oss.smce.nasa.gov/
[jupyterlab]: https://jupyter.org/
