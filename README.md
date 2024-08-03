# Oceandata Notebooks

A repository for notebooks published as [oceandata tutorials and data recipes][tutorials].

## For Contributors

> [!IMPORTANT]
> - Edit notebooks in JupyterLab so Jupytext can do its magic.
> - Create new notebooks under the `notebooks` folder, starting from a a copy of `COPYME.ipynb`.
> - If a notebook is missing from the `notebooks` folder, but its paired ".py" file is present under
>   the `src/notebooks` folder, open a terminal from the project root and run `jupytext --sync src/notebooks/**/*.py`.

Keeping notebooks in a code repository presents challenges for collaboration and curation,
because notebooks can contain very large blobs of binary outputs and they also include
constantly changing metadata. This repository contains ".py" files that the [Jupytext extension][jupytext]
synchronizes with notebooks (".ipynb" files). The ".py" files live
in the `src/notebooks` folder and are commited to the repository. The paired ".ipynb" files live
in the `notebooks` folder and are ignored by the repository. Other than the steps above,
just work on the ".ipynb" files, save your changes, and commit normally (well, almost ... git
only tracks the paired ".py" files and ignores the ".ipynb" files, so commit the ".py" files).

## For Maintainers

In addition to the ".py" files paired to notebooks, the `src` folder contains configuration
for a [Jupyter Book][jb]. Building the notebooks as one book allows for separation
of content from the JavaScript and CSS, unlike standalone HTML files built with `nbconvert`. It also provides
a way to test that all notebook are free of errors. Run the following commands in an environment with
all dependencies along with the jupyter-book and jupytext packages.

```
jb build src
```
That populates the `src/_build` folder. The folder is (mostly) ignored by git.

The second step needs globstar (a.k.a. `**` patterns) enabled in bash, so we do that first and then call jupytext.
```
shopt -s globstar
jupytext --to=notebook src/_build/**/*.py  # TODO: with metadata filter?
```
That writes an unpaired ".ipynb" format to the ".py" format sources under `src/_build`. These files are not
ignored by git. They are (will be, eventually) targets for the "Downloand and Run" links on the [tutorials][tutorials]
page. Note that opening those notebooks in Jupyter will dirty them up again, so
do not include the changes introduced by opening the clean notebooks in any commit.

The `src/_ext` folder includes a local Sphinx extension that adds the ".ipynb" download
button to the article header buttons. It has no effect, however, when the `_templates` configration
is uncommented, because the provided template removes all the buttons. TODO: keep desired buttons.

**WIP**:

1. Curating dependencies without duplicating between pyproject.toml and environment.yml
1. Formatting notebooks with black (although black does not format markdown)
1. Building notebooks in an isolated environment
1. Automate `shopt -s globstar`
1. Fails for oci_install_ocssw because of `%conda` cell.
1. https://github.com/jupyter/nbconvert/issues/1125
1. random cell ids, preserved id metadata from notebooks? (https://github.com/mwouts/jupytext/issues/1263)
1. stop doing manual copy of animation to ../../img 

## How to Cite

**WIP**:

1. fill in once on Zenodo

## Acknowledgements
This repository has greatly benefited from works of multiple open-science projects, notably [Learn OLCI][learn-olci] and the [NASA EarthData Cloud Cookbook][cookbook].

[tutorials]: https://oceancolor.gsfc.nasa.gov/resources/docs/tutorials
[jupytext]: https://jupytext.readthedocs.io/
[jupyterlab]: https://jupyter.org
[jb]: https://jupyterbook.org
[learn-olci]: https://github.com/wekeo/learn-olci/blob/main/README.md
[cookbook]: https://nasa-openscapes.github.io/earthdata-cloud-cookbook
