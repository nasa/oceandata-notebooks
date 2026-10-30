---
jupyter:
  jupytext:
    cell_metadata_filter: all,-trusted
    notebook_metadata_filter: -jupytext.text_representation.jupytext_version
    text_representation:
      extension: .md
      format_name: markdown
      format_version: '1.3'
  kernelspec:
    display_name: Python 3 (ipykernel)
    language: python
    name: python3
---

[![DOI](https://zenodo.org/badge/DOI/10.5281/zenodo.17642133.svg)](https://doi.org/10.5281/zenodo.17642133)

# Oceandata Notebooks

Welcome to the repository of tutorials for users of the [Ocean Biology Distributed Active Archive Center (OB.DAAC)][OB].

[OB]: https://www.earthdata.nasa.gov/centers/ob-daac

## For Data Users

Head over to our [Help Hub] to access the website published from this repository.

[Help Hub]: https://nasa.github.io/oceandata-notebooks/

## For Notebook Authors and Reviewers

The Help Hub [team] supports development of these resources by authoring or updating content as well as reviewing contributions from the public.
We welcome contributions in the form of new notebooks or suggestions from anyone, but ask all to observe our [Code of Conduct](CODE_OF_CONDUCT.md).
Please also take a minute to familiarize yourself with the following information about our notebooks, which are formatted as MyST Markdown rather than as Jupyter Notebooks.
Note that our [Contributing](CONTRIBUTING.md) guide is primarily of use to team members.

[team]: https://nasa.github.io/oceandata-notebooks/team.html

### Create a New Notebook

> [!NOTE]
> 
> - Create new notebooks by copying `COPYME.ipynb` into a suitable location within the top-level `notebooks` folder.
> - `COPYME.ipynb` also serves as a detailed style guide, maintaining consistency between notebooks
> - When you save your new notebook, watch for a new markdown file (.md) to appear in the `docs/notebooks` folder and add that file to a commit.

Notebooks submitted to the Help Hub should follow the `COPYME.ipynb` style guide as closely as possible to ensure a polished and consistent look for all published material. Reviewers should also reference the guide when editing submitted content. The timeline for reviews is expected to be around 2 weeks. 

If your new saved notebook does not appear as a markdown file in the appropriate `docs/notebooks` folder, see the section below on how to sync Jupyter Notebook and MyST markdown files.

### Editing MyST Markdown

> [!IMPORTANT]
> 
> - Edit notebooks in JupyterLab so Jupytext can do its magic.
> - The entire `notebooks` folder is ignored by Git, so it's not present on GitHub.

Jupyter Notebooks (.ipynb) can be challenging to manage in a collaborative code repositories because their outputs and metadata often create noisy diffs that make changes difficult to review and merge. 
The [Jupytext] extension for JupyterLab allows MyST Markdown (.md) files to be opened and edited as notebooks while preserving a human-readable, plain-text format that works well with version control.
Jupytext also supports pairing a Jupyter Notebook (.ipynb) with a MyST Markdown file, combining the benefits of interactive notebooks with the advantages of plain-text source files. By storing only the MyST Markdown file in the repository, teams can retain a clean, reviewable record of code and narrative while keeping notebook outputs and metadata out of version control.

What does this mean for authors and reviewers?
You can use Jupyter Notebooks in the `notebooks` folder normally, but you must commit the synchronous changes to the paired MyST Markdown files within the `docs/notebooks` folder.
To create the `notebooks` folder after cloning the repository, or to add a paired Jupyter Notebook when a new MyST Markdown file is pulled, run the following Terminal command.
It tells Jupytext to synchronize, creating if necessary, the paired Jupyter Notebook files with the MyST Markdown files tracked by Git.

```shell
jupytext --sync $(git ls-files docs/notebooks)
```

[Jupytext]: https://jupytext.readthedocs.io/

## How to Cite

If you reference the tutorials in a publication, or report on work performed using the [oceandata-jupyterlab] container image, please cite as follows:

```
Carroll, I., Windle, A., Wang, G., Poulin, C., Foley, S., Gray, P., Holmes, E., Caplan, S., Allen, J., Gao, M., Danenhower, M., Chase, A., Aryal, K., Fu, G., Fasnacht, Z., Werdell, J., & Knowles, D. (2025). Tutorials using data produced by NASA's Ocean Biology Distributed Active Archive Center. Zenodo. https://doi.org/10.5281/zenodo.17642133
```

[oceandata-jupyterlab]: https://github.com/nasa/oceandata-notebooks/pkgs/container/oceandata-jupyterlab

## Acknowledgements

This repository has greatly benefited from works of multiple open-science projects, notably [Learn OLCI] and the [NASA Earthdata Cloud Cookbook].

[Learn OLCI]: https://github.com/wekeo/learn-olci
[NASA Earthdata Cloud Cookbook]: https://nasa-openscapes.github.io/earthdata-cloud-cookbook

```python

```
