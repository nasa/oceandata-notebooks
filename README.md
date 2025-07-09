# Oceandata Notebooks

Welcome to the repository of tutorials for users of the [Ocean Biology Distributed Active Archive Center (OB.DAAC)][OB].

[OB]: https://www.earthdata.nasa.gov/centers/ob-daac

## For Data Users

Head over to our [Help Hub] to access the published tutorials.

[Help Hub]: https://oceancolor.gsfc.nasa.gov/resources/docs/tutorials

## For Notebook Authors and Reviewers

Please take a minute to familiarize yourself with the following information about our tutorials, which are stored as MyST Markdown rather than as Jupyter Notebooks.

### Editing Notebooks & Commiting Markdown

> [!Important]
> - Edit notebooks in JupyterLab so Jupytext can do its magic.
> - When you first clone this repository, the `notebooks` folder will not exist!

Keeping Jupyter Notebooks (.ipynb) in a code repository is tough for collaboration because Jupyter Notebooks contain large, binary outputs and metadata that frequently changes.
By means of the [Jupytext] extension to JupyterLab, MyST Markdown (.md) files can be opened like a notebook but without storing those problematic contents.
Going one step further, Jupytext can pair an actual Jupyter Notebook file with a MyST Markdown file.
That lets us enjoy the benefits of Jupyter Notebooks (e.g. stored outputs) while only storing MyST Markdown in the repository.

What does this mean for authors and reviewers?
You can use the Jupyter Notebooks in the `notebooks` folder, just know that you should commit the synchronous changes to the paired MyST Markdown files within the `book/notebooks` folder.
To create the `notebooks` folder after cloning the repository, or when a new MyST Markdown file is pulled, run the following Terminal command.
The Terminal command will synchronize paried Jupyter Notebook files with all the MyST Markdown files tracked by git.

```shell
jupytext --sync $(git ls-files book/notebooks)
```

[Jupytext]: https://jupytext.readthedocs.io/

### Create a New Notebook

> [!Note]
> Create new notebooks by copying `COPYME.ipynb` into a suitable location within the `notebooks` folder.

When you save your new notebook, watch for a new markdown file to appear in the `book/notebooks` folder and add that file to a commit.

## Acknowledgements

This repository has greatly benefited from works of multiple open-science projects, notably [Learn OLCI] and the [NASA EarthData Cloud Cookbook].

[Learn OLCI]: https://github.com/wekeo/learn-olci
[NASA EarthData Cloud Cookbook]: https://nasa-openscapes.github.io/earthdata-cloud-cookbook
