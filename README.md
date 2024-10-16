# Oceandata Notebooks

The code repository for the collection of notebooks distributed as
the [oceandata tutorials and data recipes][tutorials].

## For Contributors

> [!Note]
> After you clone this repository, the `notebooks` folder will be empty. Open a
> terminal at the project root and sync from the `src` with `jupytext`.

```shell
$ shopt -s globstar  # enables `**` in Bash (on by default in Zsh)
$ jupytext --sync src/**/*.py
```

Keeping notebooks in a code repository is tough for collaboration and curation
because notebooks contain blobs of binary outputs and have constantly changing metadata.
This repository uses [Jupytext][jupytext] to maintain notebook contents (as ".py" files)
in sync with each notebook (the ".ipynb" files). Work on the ".ipynb" files living
in the `notebooks` folder. While these are ignored by git, their paired ".py" files are
not. So, save your notebook changes, commit the ".py" file, and push.

> [!IMPORTANT]
> - Edit notebooks in JupyterLab so Jupytext can do its magic.
> - Create new notebooks under the `notebooks` folder, starting from a copy of `COPYME.ipynb`.

## For Maintainers

The sections below provide information that repository maintainers (if you merge a pull
request to `main`, consider yourself a maintainer) will want to know. You will need the
`uv` command line tool to prepare a development environment for certain actions.
```shell
$ uv sync --extra dev
$ source .venv/bin/activate
(oceandata-notebooks) $
```
The `uv` command line tool is not included as a `dev` dependency, as is common for projects
that build Python packages. Since this is not a Python package, we avoid `pip install ".[dev]"`.

### Checks: the `.pre-commit-config.yaml` file

We use several automations to get considtent code formatting, run lint checks, and ensure
consistency between ".py" and ".ipynb" files. These are implemented using the [pre-commit]
tool. You can install git hooks too run these automations at every commit.
```shell
(oceandata-notebooks) $ pre-commit install
```
You can also run checks over all files chaged on a feature branch or the currently
checked out git ref. For the latter:
```shell
(oceandata-notebooks) $ pre-commit run --from-ref main --to-ref HEAD
```

### Dependencies: the `pyproject.toml` file

For every `import` statement, or if a notebook requires a package to be installed
for a backend (e.g. h5netcdf), make sure the package is listed in the `project.dependencies`
array in `pyproject.toml`. You can add entries manually or using `uv`, as in:
```shell
$ uv add scipy
```

### Container Image: the `hub` folder

The `hub` folder has configuration files that `repo2docker` uses to build an image suitable
for use with a JupyterHub platform. The following command builds and runs the image locally,
while the `jupyterhub/repo2docker-action` pushes built images to GitHub packages. You
must have `docker` available to use `repo2docker`.

```shell
(oceandata-notebooks) $ repo2docker --appendix="$(< hub/appendix)" -p 8889:8888 hub jupyter lab --no-browser --ip 0.0.0.0
```

The configuration files are a bit complicated, but updated automatically by `pre-commit`
hooks following changes to `pyproject.toml` and `hub/environment.yml`. No `requirements`
file in this repository should be manually edited. The `hub/environment.yml` is there
for non-Python packages we prefer to get from conda-forge.
1. `requirements.txt` are the (locked) dependencies needed in `book/setup.py`
1. `hub/requirements.in` are the (locked) packages from repo2docker and `hub/environment.yml`
1. `hub/requirements.txt` are a merge of our (locked) dependencies `hub/requirements.in`

### Rendering to HTML: the `book` folder

In addition to the ".py" files paired to notebooks, the `book` folder contains configuration
for a [Jupyter Book][jb]. Only notebooks listed in `book/_toc.yml` are included. Building
the notebooks as one book allows for separation of content from the JavaScript and CSS,
unlike standalone HTML files built with `nbconvert`. It also provides a way to test that
all notebook are free of errors. Run the following commands in an environment with all
dependencies along with the jupyter-book and jupytext packages.

Build the book:
```shell
(oceandata-notebooks) $ jb build book
```
That populates the `book/_build` folder. The folder is ignored by git, but its contents
can be provided to the web team. The `_templates` make the website look very plain on
purpose, so that only the notebook content is included in the HTML files.

When you create a brand new notebook under the `notebooks` folder, it won't be rendered
to HTML locally or visible as a notebook on GitHub until you create, commit, and push the
copy under `book`. To create the `book` version:
```shell
$ jupytext --sync book/src/path/to/new/tutorial.py
$ git add book/notebooks/path/to/new/tutorial.ipynb
```
Opening the notebook this creates under `book/notebooks` in JupyterLab will add unwanted
metadata. Do not commit any changes introduced by opening the notebooks.

## How to Cite

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
