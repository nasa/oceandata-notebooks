[![DOI](https://zenodo.org/badge/769139779.svg)](https://doi.org/10.5281/zenodo.17642133)

# Oceandata Notebooks

Welcome to the repository of tutorials for users of the [Ocean Biology Distributed Active Archive Center (OB.DAAC)][OB].

[OB]: https://www.earthdata.nasa.gov/centers/ob-daac

## For Data Users

Head over to our [Help Hub] to access the published tutorials.

[Help Hub]: https://nasa.github.io/oceandata-notebooks/

## For Notebook Authors and Reviewers

Please take a minute to familiarize yourself with the following information about our tutorials, which are stored as MyST Markdown rather than as Jupyter Notebooks.

### Edit Notebooks & Commit Markdown

> [!IMPORTANT]
> 
> - Edit notebooks in JupyterLab so Jupytext can do its magic.
> - The entire `notebooks` folder is ignored by Git, so it's not present on GitHub.

Keeping Jupyter Notebooks (.ipynb) in a code repository is tough for collaboration because Jupyter Notebooks contain large, binary outputs and metadata that frequently change.
By means of the [Jupytext] extension to JupyterLab, MyST Markdown (.md) files can be opened like notebooks without saving content troublesome for collaboration.
Going one step further, Jupytext can pair an actual Jupyter Notebook file with a MyST Markdown file.
That lets us enjoy the benefits of Jupyter Notebooks (e.g. saved outputs and metadata) while only storing MyST Markdown in the repository.

What does this mean for authors and reviewers?
You can use Jupyter Notebooks in the `notebooks` folder normally, but you must commit the synchronous changes to the paired MyST Markdown files within the `docs/notebooks` folder.
To create the `notebooks` folder after cloning the repository, or to add a paired Jupyter Notebook when a new MyST Markdown file is pulled, run the following Terminal command.
It tells Jupytext to synchronize, creating if necessary, the paired Jupyter Notebook files with the MyST Markdown files tracked by Git.

```shell
jupytext --sync $(git ls-files docs/notebooks)
```

[Jupytext]: https://jupytext.readthedocs.io/

### Create a New Notebook

> [!NOTE]
> 
> Create new notebooks by copying `COPYME.ipynb` into a suitable location within the top-level `notebooks` folder.

When you save your new notebook, watch for a new markdown file to appear in the `docs/notebooks` folder and add that file to a commit.

## Acknowledgements

This repository has greatly benefited from works of multiple open-science projects, notably [Learn OLCI] and the [NASA Earthdata Cloud Cookbook].

[Learn OLCI]: https://github.com/wekeo/learn-olci
[NASA Earthdata Cloud Cookbook]: https://nasa-openscapes.github.io/earthdata-cloud-cookbook
