---
kernelspec:
  display_name: Bash
  language: bash
  name: bash
---

# Oceandata Notebooks

Welcome to the repository of data recipes for users of the [Ocean Biology Distributed Active Archive Center (OB.DAAC)][OB].

[OB]: https://www.earthdata.nasa.gov/centers/ob-daac

## For Users

Head over to our [Help Hub] to access the published notebooks.

[Help Hub]: https://oceancolor.gsfc.nasa.gov/resources/docs/tutorials

## For Contributors

> [!Important]
> - Edit notebooks in JupyterLab so Jupytext can do its magic.
> - Create new notebooks by copying `COPYME.ipynb` into the `notebooks` folder.
> - When you first clone this repository, the `notebooks` folder will not exist.

Keeping notebooks in a code repository is tough for collaboration and curation because notebooks contain large, binary outputs and metadata that frequently changes.
This repository uses [Jupytext] to keep notebooks (.ipynb) paired with markdown files (.md).
Although the entire `notebooks` folder is ignored by git, the paired markdown files are not.
Contributors should compose and edit notebooks in the `notebooks` folder, and commit changes to paired markdown files in the `book/notebooks` folder.

[Jupytext]: https://jupytext.readthedocs.io/

> [!Note]
> This `README.md` is itself recognized by Jupytext to have executable cells.
> Open it in JupyterLab as a notebook using right-click > "Open With" > "Notebook".

To create the `notebooks` folder, or any time you want to manually sync all the notebooks, run the following cell.
The `jupytext --sync` command will generate or update .ipynb files for every .md file tracke by git.

```{code-cell}
:scrolled: true

jupytext --sync $(git ls-files book/notebooks)
```

## For Maintainers

The following sub-sections provide additional information on the structure of this repo and maintenance tips.

> [!Warning]
> If you merge pull requests to `main`, you might be a maintainer.

### Development Environment: the `uv.lock` file

Use the `uv` command line tool to maintain a Python environment for maintainer activities.
If needed, install `uv` with `curl -LsSf https://astral.sh/uv/install.sh | sh` or by one of [many other installation methods][uv].

If being conscientious about storage (e.g. if you are `jovyan` on a cloud-based JupyterHub), tell `uv` to use temporary directories.
On a laptop or on-prem server, there are good reasons not to set these variables.

[uv]: https://docs.astral.sh/uv/getting-started/installation

```{code-cell}
if [ $(whoami) = "jovyan" ]; then
  export UV_PROJECT_ENVIRONMENT=/tmp/uv/venv
  export UV_CACHE_DIR=/tmp/uv/cache
fi
```

The `uv sync` command creates an isolated development environment based on the `uv.lock` file.

```{code-cell}
:scrolled: true

uv sync
```

> [!Warning]
> The subsections below assume you have activated the development environment with the following cell.

```{code-cell}
source .venv/bin/activate
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

+++

### Rendering to HTML: the `book` folder

In addition to the ".md" files paired to notebooks, the `book` folder contains configuration for a [Jupyter Book].
Only notebooks listed in `book/_toc.yml`.
Building the notebooks as one book provides smaller files for tutorial content, a single source of JavaScript and CSS, and tests that all notebooks run without errors.

Presently, it's best to build from ipynb rather than mystmd, so we generate clean ipynb and exclude (see `book/_config.yml`) the md files.

[Binder]: https://mybinder.org/
[Jupyter Book]: https://jupyterbook.org/

```{code-cell}
---
scrolled: true
editable: true
slideshow:
  slide_type: ''
tags: []
---
jupytext --to ipynb $(git ls-files book/notebooks)
uv run --directory book jupyter book build .
```

That populates the `book/_build` folder.
The folder is ignored by git, but its contents can be provided to the website team.
The `_templates` make the website very plain, on purpose, for the benefit of the website team.

To preview a website with the same content and navigation tools, comment out the `templates_path` part of `book/_config.yml` and start a simple web server.

```{code-cell}
python -m http.server -d book/_build/html &> /dev/null &
```

The above command was run in the background due to the final `&`, and the next command kills it.

```{code-cell}
kill %1
```

### Automation and Checks: the `.pre-commit-config.yaml` file

We use several automations to get standard code formatting, run lint checks, and ensure consistency between ".md" and ".ipynb" files.
These are implemented using the [pre-commit] tool from the development environment.
You can setup git hooks to run these automations, as needed, at every commit.

[pre-commit]: https://pre-commit.com/

```{code-cell}
# pre-commit install
```

You can also run checks over all files chaged on a feature branch or the currently checked out git ref. For the latter:

```{code-cell}
pre-commit run --from-ref main --to-ref HEAD
```

If you have `docker` available, you can build the image defined in the `docker` folder.

```{code-cell}
pre-commit run --hook-stage manual repo2docker-build
```

### Image: the `docker` folder

The `docker` folder has configuration files that [repo2docker] uses to build an image suitable for use with a JupyterHub platform.
The following command builds and runs the image locally, while the [repo2docker-action] pushes built images to GitHub packages.
You must have `docker` available to use `repo2docker`.

[repo2docker]: https://repo2docker.readthedocs.io/
[repo2docker-action]: https://github.com/marketplace/actions/repo2docker-action

```{code-cell}
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
> The top-level `requirements.txt` file also makes our repo work on [Binder].

+++

## Acknowledgements

This repository has greatly benefited from works of multiple open-science projects, notably [Learn OLCI] and the [NASA EarthData Cloud Cookbook].

[Learn OLCI]: https://github.com/wekeo/learn-olci
[NASA EarthData Cloud Cookbook]: https://nasa-openscapes.github.io/earthdata-cloud-cookbook
