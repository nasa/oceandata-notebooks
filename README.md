# Oceandata Notebooks

The code repository for the collection of notebooks distributed as
the [oceandata tutorials and data recipes][tutorials].

## For Contributors

> [!Note]
> After you clone this repository, the `notebooks` folder will be empty. Open a
> terminal at the project root and sync from the `src` with `jupytext`.

```shell
$ shopt -s globstar  # enable `**` in Bash (can skip for Zsh)
$ jupytext --sync src/**/*.py
```

Keeping notebooks in a code repository is tough for collaboration and curation
because notebooks contain blobs of binary outputs and constantly changing metadata.
This repository uses the [Jupytext extension][jupytext] to maintain ".py" files that are
synchronized with each notebook (the ".ipynb" files). Edit the ".ipynb" files living
in the `notebooks` folder. These are ignored by git, while the paired ".py" files are
tracked by git. Save the ".ipynb", commit the ".py", and push.

> [!IMPORTANT]
> - Edit notebooks in JupyterLab so Jupytext can do its magic.
> - Create new notebooks under the `notebooks` folder, starting from a copy of `COPYME.ipynb`.

When you create a brand new notebook under the `notebooks` folder, it won't be visible
as a notebook on GitHub until you create, commit, and push the "clean" version under `book`.
To create the `book` version for GitHub, use `jupytext`.
```shell
$ jupytext --sync book/src/path/to/tutorial.py
$ git add book/notebooks/path/to/tutorial.ipynb
```
Opening the notebook this creates under `book/notebooks` in JupyterLab will add unwanted
metadata. Do not commit any changes introduced by opening the notebooks.

## For Maintainers

The sections below provide information that repository maintainers (if you merge a pull
request to `main`, consider yourself a maintainer) will want to know.

> [!IMPORTANT]
> Before a pull request is merged, run the [pre-commit] checks on the changes, fix failing
> checks, and repeat until all checks pass.

TODO: describe using pre-commit on changes between a branch to main

### Dependencies

For every `import` statement, or if a notebook requires a package to be installed
for a backend (e.g. h5netcdf), make sure the package is listed in the `project.dependencies`
array in `pyproject.toml`. You can add entries manually or using `uv`, as in:
```shell
$ uv add scipy
```

### Repo2Docker Image

The `hub` folder has configuration files that `repo2docker` uses to build an image suitable
for use with a JupyterHub platform. The following command builds and runs the image locally,
while the `jupyterhub/repo2docker-action` pushes built images to GitHub packages.

```shell
$ uv sync --extra dev
$ source .venv/bin/activate
(oceandata-notebooks) $ repo2docker --appendix="$(< hub/appendix)" -p 8889:8888 hub jupyter lab --no-browser --ip 0.0.0.0
```

These configuration files are a bit complicated, but automated by `pre-commit` to update
on manual updates to `pyproject.toml` and `hub/environment.yml`. No `requirements`
file in this repository should be manually edited. The `hub/environment.yml` is there
for non-Python packages we prefer to get from conda-forge.
1. `requirements.txt` are the locked dependencies needed in `src/setup.py`
1. `hub/requirements.in` are the (locked) packages from repo2docker and `hub/environment.yml`
1. `hub/requirements.txt` are a merge of our (locked) dependencies `hub/requirements.in`

### Building Notebooks as HTML

In addition to the ".py" files paired to notebooks, the `src` folder contains configuration
for a [Jupyter Book][jb]. Building the notebooks as one book allows for separation of content
from the JavaScript and CSS, unlike standalone HTML files built with `nbconvert`. It also
provides a way to test that all notebook are free of errors. Run the following commands
in an environment with all dependencies along with the jupyter-book and jupytext packages.

Build the full book (the HTML files):
```shell
$ uv sync --extra dev
$ source .venv/bin/activate
(oceandata-notebooks) $ jb build src
```
That populates the `src/_build` folder. The folder is ignored by git, but its contents
can be provided to the web team. The `_templates` make the website look very plain on
purpose, so that only the notebook content is included in the HTML files.

## TODO: How to Cite

## Acknowledgements
This repository has greatly benefited from works of multiple open-science projects,
notably [Learn OLCI][learn-olci] and the [NASA EarthData Cloud Cookbook][cookbook].

[tutorials]: https://oceancolor.gsfc.nasa.gov/resources/docs/tutorials
[jupytext]: https://jupytext.readthedocs.io/
[jupyterlab]: https://jupyter.org
[jb]: https://jupyterbook.org
[learn-olci]: https://github.com/wekeo/learn-olci/blob/main/README.md
[cookbook]: https://nasa-openscapes.github.io/earthdata-cloud-cookbook
[pre-commit]: https://pre-commit.com/
