
[![DOI](https://zenodo.org/badge/DOI/10.5281/zenodo.17642133.svg)](https://doi.org/10.5281/zenodo.17642133)

# Oceandata Notebooks

Welcome to the repository of tutorials for users of the [Ocean Biology Distributed Active Archive Center (OB.DAAC)][OB].

[OB]: https://www.earthdata.nasa.gov/centers/ob-daac

## For Data Users

Head over to our [Help Hub] to access the website published from this repository.

[Help Hub]: https://nasa.github.io/oceandata-notebooks/

## For Tutorial Authors, Editors, and Reviewers

The Help Hub [team] supports development of these resources by authoring or updating content and reviewing contributions from the public.
We welcome contributions in the form of notebook additions or edits from anyone, but we ask all to observe our [code of conduct](CODE_OF_CONDUCT.md).
Please also read the tips below about our notebooks, which are stored in the repository as MyST Markdown rather than as Jupyter Notebooks.
Note that our [CONTRIBUTING.md](CONTRIBUTING.md) doc is written for project maintainers.

> [!IMPORTANT]
> 
> Before you can edit or create notebooks, call the following in a Terminal to create the notebooks folder.
> ```shell
> jupytext --sync $(git ls-files docs/notebooks)
> ```

[team]: https://nasa.github.io/oceandata-notebooks/team.html

### Edit Existing Notebooks

- The [COPYME.ipynb](COPYME.ipynb) notebook is a template **and** a style guide. Follow the guide to maintain consistency between notebooks!
- Edit Jupyter Notebooks (.ipynb files under `notebooks/`) using a JupyterLab with the Jupytext extension.
- When you save changes to a notebook, commit and push the changes to its paired markdown file (.md files under `docs/notebooks/`).

### Create a New Notebook

In addition to the above guidance about editing notebooks:

- Create a new notebook by copying the [COPYME.ipynb](COPYMY.ipynb) template into a suitable location under `notebooks/` (not under `docs/notebooks/`).
- When you save your new notebook, watch for a new markdown file (.md) to appear in the `docs/notebooks/` folder and add that file to a commit.

Notebooks submitted to the Help Hub should follow our style guide as closely as possible to ensure a polished and consistent look for all published material. Reviewers should also reference the guide when editing submitted content. The timeline for reviews of new notebooks should be around 2 weeks.

## Why MyST Markdown?

Jupyter Notebooks (.ipynb) can be challenging to manage in a collaborative code repositories because their outputs and metadata often create noisy diffs that make edits difficult to review and merge.
The MyST Markdown (.md) files we use to store notebooks do not include these outputs or metadata, which works better for collaboration via Git repositories.
By storing only the MyST Markdown file in the repository, contributos can retain a clean, reviewable record of code and narrative while keeping outputs and metadata out of version control.
MyST Markdown can also be edited in any text editor, including directly on GitHub.

What does this mean for authors and reviewers?
You can use Jupyter Notebooks in the `notebooks/` folder normally, but you must commit the synchronous changes to the paired MyST Markdown files within the `docs/notebooks/` folder.
The [Jupytext] extension pairs each Jupyter Notebook with a MyST Markdown "source" file, combining the benefits of the .ipynb format with the advantages of the .md format.

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
