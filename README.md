# Oceandata Notebooks

A repository for notebooks published as [oceandata tutorials and data recipes][tutorials].

## For Contributors

> [!IMPORTANT]
> - Edit notebooks in JupyterLab so Jupytext can do its magic.
> - Create new notebooks under the `notebooks` folder, starting from a copy of `COPYME.ipynb`.

Keeping notebooks in a code repository presents challenges for collaboration and curation,
because notebooks can contain very large blobs of binary outputs and include
constantly changing metadata. This repository contains ".py" files that the [Jupytext extension][jupytext]
synchronizes with notebooks (".ipynb" files) in your clone. The ".py" files live
in the `src/notebooks` folder and are commited to the repository. The paired ".ipynb" files live
in the `notebooks` folder and are ignored by git. Other than the steps above,
just work on the ".ipynb" files, save your changes, and commit normally (well, almost ... git
only tracks the paired ".py" files and ignores the ".ipynb" files, so commit the ".py" files).

> [!IMPORTANT]
> Right after you clone this repository, the `notebooks` folder will be empty. Any time
> a notebook is missing (i.e. the ".py" file exists but not the ".ipynb" file) open a
> terminal at the project root and do the following.
>
> ```
> $ rm src/jupytext.toml
> $ jupytext --sync src/notebooks/**/*.py
> $ git restore src/jupytext.toml
> ```

## For Maintainers

TODO:
  - PR for L2/L3 notebooks
  - why is thomas notebook different on website?
  - src/jupytext.toml makes manual sync annoying
  - get working on oss
  - notebooks failing in `jb build src/`, see `src/_toc.yml`
  - pre-commit markdown word wrap?
  - index-url for pytorch, but it pre-empts everything
  - apply license to separately downloadable files (setup.py, *.ipynb)
  - changelog
  - random cell ids, preserved id metadata from notebooks? (see https://github.com/mwouts/jupytext/issues/1263)
  - fill in "How to Cite" once on Zenodo
  - CodeQL static code analyzer

### Dependencies

For every `import` statement, or if a notebook requires a package to be installed
for a backend (e.g. h5netcdf), make sure the package is listed in the `project.dependencies`
array in `pyproject.toml`. You can add entries manually or using `uv`, as in:
```
$ uv add scipy
```

### Repo2Docker Image

The `hub` folder has configuration files that `repo2docker` uses to build an image suitable
for use with a JupyterHub platform. The following command builds and runs the image locally,
while the `jupyterhub/repo2docker-action` delivers built images to the GitHub registry.

```
$ uv sync --extra dev
$ repo2docker --appendix="$(< hub/appendix)" -p 8889:8888 hub jupyter lab --no-browser --ip 0.0.0.0
```

The configuration files are a bit complicated, but automated by `pre-commit` to trigger
on manual updates to `pyproject.toml` and `hub/environment.yml` (no `requirements`
file in this repository needs to be manually edited). The `hub/environment.yml` is there
for non-Python packages we prefer from conda-forge.
1. `requirements.txt` are the locked dependencies needed in `src/setup.py`
1. `hub/requirements.in` are the (locked) packages from repo2docker and `hub/environment.yml`
1. `hub/requirements.txt` are a merge of our (locked) dependencies `hub/requirements.in`

### Building Notebooks as HTML

In addition to the ".py" files paired to notebooks, the `src` folder contains configuration
for a [Jupyter Book][jb]. Building the notebooks as one book allows for separation
of content from the JavaScript and CSS, unlike standalone HTML files built with `nbconvert`. It also provides
a way to test that all notebook are free of errors. Run the following commands in an environment with
all dependencies along with the jupyter-book and jupytext packages.

For building the HTML
```
$ uv sync --extra dev
$ source .venv/bin/activate
(oceandata-notebooks) $ jb build src
```
That populates the `src/_build` folder. The folder is (mostly) ignored by git. Note that
the `jupytext` pre-commit check might update the "clean" notebooks under `src/_build/html/_sources`
and report "Failed". That's okay, just commit the "clean" notebooks and try again. They
are committed to the repository as targets for the "Downloand and Run" links on the [tutorials][tutorials]
page. Note that opening those notebooks in Jupyter will dirty them up again, so
do not include the changes introduced by opening the clean notebooks in any commit.


<!--
FIXME: seems to be (have been? can't get missing outputs now ...) a bug in the chain from jb build src that does not add the reader to the jcache.
```
jcache notebook -p src/_build/.jupyter_cache list
```
Add notebooks to the jupyter cache with something like this:
```
cd src
jcache notebook -p _build/.jupyter_cache add -r jupytext notebooks/hackweek/<new_notebook>.py
```
After builds that use the case, merge the cache output into the notebook (do this for all notebooks).
```
for f in notebooks/hackweek/*.py; do
  jcache notebook -p _build/.jupyter_cache merge ${f} _build/jupyter_execute/${f%.*}.ipynb
done
``` -->


The `src/_ext` folder includes a local Sphinx extension that adds the ".ipynb" download
button to the article header buttons. It has no effect, however, when the `_templates` configration
is uncommented, because the provided template removes all the buttons. TODO: keep desired buttons.

## How to Cite

## Acknowledgements
This repository has greatly benefited from works of multiple open-science projects, notably [Learn OLCI][learn-olci] and the [NASA EarthData Cloud Cookbook][cookbook].

[tutorials]: https://oceancolor.gsfc.nasa.gov/resources/docs/tutorials
[jupytext]: https://jupytext.readthedocs.io/
[jupyterlab]: https://jupyter.org
[jb]: https://jupyterbook.org
[learn-olci]: https://github.com/wekeo/learn-olci/blob/main/README.md
[cookbook]: https://nasa-openscapes.github.io/earthdata-cloud-cookbook
