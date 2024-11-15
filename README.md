# Oceandata Notebooks

The code repository for the collection of notebooks distributed as data recipes for
users of the Ocean Biology Distributed Active Archive Center ([OB.DAAC]).

## For Users

Get started on our [Help Hub].

## For Contributors

> [!IMPORTANT]
> - Edit notebooks in JupyterLab so Jupytext can do its magic.
> - Create new notebooks under the `notebooks` folder, starting from a copy of `COPYME.ipynb`.

Keeping notebooks in a code repository is tough for collaboration and curation
because notebooks contain large, binary outputs and metadata that messes up `git merge`.
This repository uses [Jupytext] to keep notebooks (the ".ipynb" files) paired
with plain text files (the ".py" files). Contributors should work on the ".ipynb" files
in the `notebooks` folder. These files are ignored by git, but the paired ".py" files are
not. So, save your changes in a notebook, commit the paired ".py" file, and push.

> [!Note]
> When you first clone this repository, the `notebooks` folder will be empty. Open a
> terminal at the project root and sync from the `src` using `jupytext`.

```shell
shopt -s globstar  # enables `**` in Bash (enabled by default in Zsh)
jupytext --sync src/**/*.py
```
You can run this any time to ensure there is an ".ipynb" file in your `notebooks` folder
for every ".py" file in the `src` folder.

## For Maintainers

> [!IMPORTANT]
> If you merge pull requests to `main`, you might be a maintainer.

### Development Environment: the `uv.lock` file

We use the `uv` command line tool to maintain a Python environment for maintainer activities.
It can be installed with `pip install uv`, `pip install --user uv`, or `pipx install uv`.
The `uv sync` command creates an isolated development environment, at `.venv` by default, based
on the `uv.lock` file.
```shell
uv sync
PATH=.venv/bin:$PATH
```
If being conscientious about storage (e.g. on a cloud-based JupyterHub), set the `UV_PROJECT_ENIRONMENT`
variable to a temporary directory and avoid caching.
```shell
export UV_PROJECT_ENVIRONMENT=/tmp/venv
uv sync --no-cache
PATH=${UV_PROJECT_ENVIRONMENT}/bin:$PATH
```

### Automation and Checks: the `.pre-commit-config.yaml` file

We use several automations to get standard code formatting, run lint checks, and ensure
consistency between ".py" and ".ipynb" files. These are implemented using the [pre-commit]
tool from the development environment. You can setup git hooks to run these automations,
as needed, at every commit.
```shell
pre-commit install
```
You can also run checks over all files chaged on a feature branch or the currently
checked out git ref. For the latter:
```shell
pre-commit run --from-ref main --to-ref HEAD
```
If you have `docker` available, you can build the image defined in the `docker` folder.
```shell
pre-commit run --hook-stage manual repo2docker-build
```

### Dependencies: the `pyproject.toml` file

For every `import` statement, or if a notebook requires a package to be installed
for a backend (e.g. h5netcdf), make sure the package is listed in the `project.dependencies`
array in `pyproject.toml`. You can add entries manually or using `uv`, as in:
```shell
uv add scipy
```
The `project.optional-dependencies` tables list additional dependencies that are needed
either for a Jupyter kernel, for a Docker image with JupyterLab, or by maintainers.

### Container Image: the `docker` folder

The `docker` folder has configuration files that [repo2docker] uses to build an image suitable
for use with a JupyterHub platform. The following command builds and runs the image locally,
while the [repo2docker-action] pushes built images to GitHub packages. You
must have `docker` available to use `repo2docker`.
```shell
export DOCKER_HOST=unix://${HOME}/.docker/run/docker.sock
repo2docker \
    --image-name oceandata-notebooks \
    --user-id 1000 \
    --user-name jovyan \
    --appendix "$(< docker/appendix)" \
    -p 8889:8888 \
    docker jupyter lab --no-browser --ip 0.0.0.0
```
The configuration files are a bit complicated, but updated automatically by `pre-commit`
hooks following changes to `pyproject.toml` and `docker/environment.yml`. No `requirements`
file in this repository should be manually edited. The `docker/environment.yml` file is there
for non-Python packages needed from conda-forge. We use PyPI for Python packages.
1. `requirements.txt` are the (locked) dependencies needed in `book/setup.py`
1. `docker/requirements.in` are the (locked) packages from repo2docker and `docker/environment.yml`
1. `docker/requirements.txt` are a merge of our (locked) dependencies with `docker/requirements.in`

> [!Note]
> The top-level `requirements.txt` file is located there to also provide dependencies for [Binder].

### Rendering to HTML: the `book` folder

In addition to the ".py" files paired to notebooks, the `book` folder contains configuration
for a [Jupyter Book]. Only notebooks listed in `book/_toc.yml` are included. Building
the notebooks as one book provides smaller files for tutorial content, a single source of
JavaScript and CSS, and a test that all notebook run without errors.

To build the book:
```shell
jb build book
```
That populates the `book/_build` folder. The folder is ignored by git, but its contents
can be provided to the web team. The `_templates` make the website look very plain on
purpose, so that only the notebook content is included in the HTML files.

When you create a brand new notebook under the `notebooks` folder, it won't be rendered
to HTML locally or visible as a notebook on GitHub until you create, commit, and push the
copy under `book`. To create the `book` version:
```shell
jupytext --sync book/src/path/to/new/tutorial.py
git add book/notebooks/path/to/new/tutorial.ipynb
```
Opening the notebook this creates under `book/notebooks` in JupyterLab will add unwanted
metadata. Do not commit any changes introduced by opening the new notebook.

## Acknowledgements

This repository has greatly benefited from works of multiple open-science projects,
notably [Learn OLCI] and the [NASA EarthData Cloud Cookbook].

[OB.DAAC]: https://www.earthdata.nasa.gov/centers/ob-daac
[Help Hub]: https://oceancolor.gsfc.nasa.gov/resources/docs/tutorials
[Jupytext]: https://jupytext.readthedocs.io
[Jupyter Book]: https://jupyterbook.org
[pre-commit]: https://pre-commit.com
[Binder]: https://mybinder.org/
[repo2docker]: https://repo2docker.readthedocs.io
[repo2docker-action]: https://github.com/marketplace/actions/repo2docker-action
[Learn OLCI]: https://github.com/wekeo/learn-olci
[NASA EarthData Cloud Cookbook]: https://nasa-openscapes.github.io/earthdata-cloud-cookbook
