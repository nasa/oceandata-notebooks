# Oceandata Notebooks

Welcome to the repository of data recipes for users of the [Ocean Biology Distributed Active Archive Center (OB.DAAC)][OB].

[OB]: https://www.earthdata.nasa.gov/centers/ob-daac

## For Readers

Head over to our [Help Hub] to access the published notebooks.

[Help Hub]: https://oceancolor.gsfc.nasa.gov/resources/docs/tutorials

## For Authors and Reviewers

Keeping notebooks (.ipynb) in a code repository is tough for collaboration because notebooks contain large, binary outputs and metadata that frequently changes.
By means of the [Jupytext] extension to JupyterLab, MyST Markdown (.md) files can behave like notebooks without these problematic contents.
To get the benefits of having those outputs and metadata in your clone, *while only* storing markdown files in a code repository, we let the Jupytext extension keep a paired markdown file synchronized with each notebook.
Contributors should compose and edit these "local-only" notebooks in the `notebooks` folder and commit the markdown files in the `book/notebooks` folder.

[Jupytext]: https://jupytext.readthedocs.io/

### Edit Notebooks

> [!Important]
> - Edit notebooks in JupyterLab so Jupytext can do its magic.
> - When you first clone this repository, the `notebooks` folder will not exist!

To create the `notebooks` folder, or any time a notebook does not appear under `notebooks`, run the following Terminal command.
It will synchronize your .ipynb files with all the .md files tracked by git.

```shell
jupytext --sync $(git ls-files book/notebooks)
```

### Create a New Notebook

> [!Note]
> Create new notebooks by copying `COPYME.ipynb` into a suitable location within the `notebooks` folder.

When you save your new notebook, watch for a new markdown file to appear in the `book/notebooks` folder and add that file to your commit.

## Acknowledgements

This repository has greatly benefited from works of multiple open-science projects, notably [Learn OLCI] and the [NASA EarthData Cloud Cookbook].

[Learn OLCI]: https://github.com/wekeo/learn-olci
[NASA EarthData Cloud Cookbook]: https://nasa-openscapes.github.io/earthdata-cloud-cookbook
