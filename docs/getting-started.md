---
jupyter:
  jupytext:
    cell_metadata_filter: all,-trusted
    notebook_metadata_filter: -all,kernelspec,jupytext
    text_representation:
      extension: .md
      format_name: markdown
      format_version: '1.3'
      jupytext_version: 1.18.1
  kernelspec:
    display_name: Python 3 (ipykernel)
    language: python
    name: python3
---

TODO: 
- Will we still have Earthdata cloud icons? If not, should edit this paragraph.
- Should we include instructions (or a link) on how to get a running JupyterLab? (Or Jupyter interface)
- Maybe we say “execute the following from a terminal inside your Jupyter interface”?


# Get Started

## Earthdata Cloud

The **Earthdata Cloud** icon next to some notebooks indicates they are meant to be run using Amazon Web Services (AWS), which is the cloud provider used for NASA Earthdata Cloud. If you are not set up on AWS, you can still use those notebooks, but will need to download data as descibed below in the Data Access notebook. If you are new to using NASA Earthdata Cloud, the [Cloud Cookbook][cookbook] provides a lot of background and resources that are constantly being improved by the [NASA-Openscapes][openscapes] community.

**Can I use an existing AWS platform?** You may already have access to the AWS platform through your institution or research community. For example, JupyterHubs maintained by [Openscapes][openscapes-hub], [Cryo in the Cloud][cryocloud], [MAAP][maap], and NASA Goddard's [Open Science Studio][oss] are running on AWS in the same "us-west-2" region that hosts the NASA Earthdata Cloud. If that is not the case, you may want to learn about [getting started with AWS for NASA Earthdata Cloud][edcloud].

## Jupyter Kernel

If you have a running Jupyter Lab, download our setup script ({download}`setup.py`) and
run it under either `pipx` or `uv` to create a Jupyter kernel ready for use with the notebooks. For
example, if you have `uv` installed, execute the following from a Terminal.
```
uv run setup.py --user --name oceandata
```
Alternatively, if you have `pipx` installed:
```
pipx run setup.py --user --name oceandata
```
Your JupyterLab should soon include "oc" and "bash" as kernel choices for notebooks and
consoles. For more on the provided arguments, which customize the kernel location and name,
execute `pipx run setup.py --help`. The `pipx` documenation provides
[install instructions](https://pipx.pypa.io/stable/installation/) that include the
simple approach of `pip install --user pipx`. Uninstall kernels with `jupyter kernelspec`.

# Help

Have a question or an idea? Share it with us on the Earthdata Forum using the tags OB.DAAC under DAAC and Data Recipes under Services/Usage. 
