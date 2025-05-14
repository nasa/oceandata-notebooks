# Oceandata Notebooks

Welcome to the repository of data recipes for users of the Ocean Biology Distributed Active Archive Center ([OB.DAAC]).

## For Users

Navigate to our [Help Hub] to access the published notebooks.

## For Contributors

> [!IMPORTANT]
> - Edit notebooks in JupyterLab so Jupytext can do its magic.
> - Create new notebooks under the `notebooks` folder, starting from a copy of `COPYME.ipynb`.

Keeping notebooks in a code repository is tough for collaboration and curation because notebooks contain large, binary outputs and metadata that frequently changes.
This repository uses [Jupytext] to keep notebooks (`.ipynb`) paired with markdown (`.md`) files.
Although the entire `notebooks` folder is ignored by git, the paired markdown files are not.
Contributors should compose and edit notebooks in the `notebooks` folder, and commit changes to paired markdown files in the `book/notebooks` folder.

> [!Note]
> When you first clone this repository, the `notebooks` folder will not exist.

Run the following in Terminal to generate ".ipynb" files, creating the `notebooks` folder if needed.

```shell
jupytext --sync $(git ls-files book/notebooks)
```

## For Maintainers

> [!IMPORTANT]
> If you merge pull requests to `main`, you might be a maintainer.

### Development Environment: the `uv.lock` file

Use the `uv` command line tool to maintain a Python environment for maintainer activities.
If needed, install `uv` with `curl -LsSf https://astral.sh/uv/install.sh | sh` or by one of [many other installation methods][uv].

If being conscientious about storage (e.g. on a cloud-based JupyterHub), tell `uv` to use temporary directories.
On a laptop or on-prem server, there are good reasons not to set these variables.

```shell
export UV_PROJECT_ENVIRONMENT=/tmp/uv/venv
export UV_CACHE_DIR=/tmp/uv/cache
```

The `uv sync` command creates an isolated development environment based on the `uv.lock` file.

```shell
uv sync
```

Execute all notebooks in the isolated development environment by launching the Jupyter Book.

```shell
cd book
uv run jupyter book start --execute
```

The launched server runs until you type `Ctrl-C` in the same Terminal.
The following sub-sections provide additional information on the structure of this repo and maintenance tips.

### Automation and Checks: the `.pre-commit-config.yaml` file

We use several automations to get standard code formatting, run lint checks, and ensure consistency between ".md" and ".ipynb" files.
These are implemented using the [pre-commit] tool from the development environment.
You can setup git hooks to run these automations, as needed, at every commit.

```shell
pre-commit install
```

You can also run checks over all files chaged on a feature branch or the currently checked out git ref. For the latter:

```shell
pre-commit run --from-ref main --to-ref HEAD
```

If you have `docker` available, you can build the image defined in the `docker` folder.

```shell
pre-commit run --hook-stage manual repo2docker-build
```

### Dependencies: the `pyproject.toml` file

For every `import` statement, or if a notebook requires a package to be installed for a backend (e.g. h5netcdf),
make sure the package is listed in the `notebooks` array under the `dependency-groups` table in `pyproject.toml`.
You can add entries manually or using `uv add`.

```shell
uv add --group notebooks scipy
```

The other keys in the `dependency-groups` table provide additional dependencies,
which are needed for a working Jupyter kernel, for a complete JupyterLab in a Docker image, or for maintenance tasks.

### Container Image: the `docker` folder

The `docker` folder has configuration files that [repo2docker] uses to build an image suitable for use with a JupyterHub platform.
The following command builds and runs the image locally, while the [repo2docker-action] pushes built images to GitHub packages.
You must have `docker` available to use `repo2docker`.

```shell
export DOCKER_HOST=unix://${HOME}/.docker/run/docker.sock
repo2docker \
    --user-id 1000 \
    --user-name jovyan \
    --appendix "$(< docker/appendix)" \
    -p 8889:8888 \
    docker jupyter lab --no-browser --ip 0.0.0.0
```

The configuration files are a bit complicated, but updated automatically by `pre-commit` hooks following changes to `pyproject.toml` and `docker/environment.yml`.
No `requirements` file in this repository should be manually edited.
The `docker/environment.yml` file is there for non-Python packages needed from conda-forge.
We use PyPI for Python packages.

1. `requirements.txt` has the (locked) packages needed in `book/setup.py`
1. `docker/requirements.in` has the (frozen) packages from repo2docker and `docker/environment.yml`
1. `docker/requirements.txt` has the (locked) packages needed in the Docker image

> [!Note]
> The top-level `requirements.txt` file is also in the location needed for [Binder].

### Rendering to HTML: the `book` folder

In addition to the ".md" files paired to notebooks, the `book` folder contains configuration for a [Jupyter Book].
Only notebooks listed in `book/myst.yml` under `site.toc` are included.
Building the notebooks as one book provides smaller files for tutorial content, a single source of JavaScript and CSS, and tests that all notebooks run without errors.

```shell
cd book
uv run jupyter book build --execute --html
```

That populates the `book/_build` folder. The folder is ignored by git, but its contents can be provided to the website team.
The `myst.yml` configu makes the result plain on purpose, so that the notebook content is most of what's included in the HTML files.

## Acknowledgements

This repository has greatly benefited from works of multiple open-science projects, notably [Learn OLCI] and the [NASA EarthData Cloud Cookbook].

[OB.DAAC]: https://www.earthdata.nasa.gov/centers/ob-daac
[Help Hub]: https://oceancolor.gsfc.nasa.gov/resources/docs/tutorials
[Jupytext]: https://jupytext.readthedocs.io/
[uv]: https://docs.astral.sh/uv/getting-started/installation
[Jupyter Book]: https://jupyterbook.org/
[pre-commit]: https://pre-commit.com/
[Binder]: https://mybinder.org/
[repo2docker]: https://repo2docker.readthedocs.io/
[repo2docker-action]: https://github.com/marketplace/actions/repo2docker-action
[Learn OLCI]: https://github.com/wekeo/learn-olci
[NASA EarthData Cloud Cookbook]: https://nasa-openscapes.github.io/earthdata-cloud-cookbook
