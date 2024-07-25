# Oceandata Notebooks

A repository for notebooks published as [oceandata tutorials and data recipes][tutorials].

## For Contributors

> [!IMPORTANT]
> - Edit notebooks in JupyterLab so Jupytext can do its magic.
> - Create new notebooks within the `notebooks/` folder, starting from a a copy of "COPYME.ipynb".
> - If a notebook is missing from the `notebooks/` folder, but its paired ".py" file is present in
>   the `src/` folder, open a terminal from the project root and run `jupytext --sync src/**/*.py`.
> - Nothing in the `docs/` folder should be manually edited.

Keeping notebooks in a code repository presents challenges for collaboration and curation,
because notebooks can contain very large blobs of binary outputs and they also include
constantly changing metadata. This repository contains ".py" files that the [Jupytext extension][jupytext]
synchronizes with notebooks (".ipynb" files). The ".py" files live
in the `src/` folder and are commited to the repository. The paired ".ipynb" files live
in the `notebooks/` folder and are ignored by the repository. Other than the steps above,
just work on the ".ipynb" files, save your changes, and commit normally (well, almost ... git
only tracks the paired ".py" files and ignores the ".ipynb" files, so commit the ".py" files).

## For Maintainers

In addition to the ".py" files paired to notebooks, the `src/` folder contains configuration
for a [Jupyter Book][jb]. Building the tutorials as a static website allows for separation
of each tutorial's content from the JavaScript and CSS, unlike standalone HTML files built with `nbconvert`. Run the following commands in an environment with all tutorial dependencies along
with the jupyter-book package.

```
#jb build --path-output=docs/ src
jb build src
```
That populates the top level `docs/` folder. The next one overwrites the evaluated notebooks
in the website `_sources` folder with unevaluated, clean notebooks.
```
#jupytext --to=notebook docs/_build/html/_sources/**/*.py
jupytext --to=notebook src/_build/html/_sources/**/*.py
```

Note that the `src` folder includes a local Sphinx extension that adds the ".ipynb" download button
to the article header. Those are also the (eventual) targets for the "Downloand and Run" links on the [tutorials][tutorials] page. Note that opening those notebooks in Jupyter will dirty them up again, so
do not include the changes introduced by opening the clean notebooks in any commit.

**WIP**:

1. Curating dependencies without duplicating between pyproject.toml and environment.yml
1. Formatting notebooks with black (although black does not format comments)
1. Testing notebooks in isolated environments (e.g. using `jupyter execute ...`)
1. jb building
   - TODO: automate `shopt -s globstar`
   - TODO: fails for oci_install_ocssw because of `%conda` cell.
   - TODO: https://github.com/jupyter/nbconvert/issues/1125

```
notebooks/
src/**/*.py
src/_config.yml
src/_build/html/_sources/**/*.(ipynb|py)
src/_build/jupyter_execute/
```

notebooks/
docs/html/_sources/**/*.(ipynb|py)
docs/jupyter_execute
src/**/*.py
src/_config.yml

## How to Cite

**WIP**:

1. fill in once on Zenodo

## Acknowledgements
This repository has greatly benefited from works of multiple open-science projects, notably [Learn OLCI][learn-olci] and the [NASA EarthData Cloud Cookbook][cookbook].

[tutorials]: https://oceancolor.gsfc.nasa.gov/resources/docs/tutorials
[jupyterlab]: https://jupyter.org
[jb]: https://jupyterbook.org
[hatch]: https://hatch.pypa.io
[learn-olci]: https://github.com/wekeo/learn-olci/blob/main/README.md
[cookbook]: https://nasa-openscapes.github.io/earthdata-cloud-cookbook