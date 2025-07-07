---
kernelspec:
  name: bash
  language: bash
  display_name: Bash
---

# Contributor's Guide

We are happy to have your help maintaining the repo of data recipes for  of the [Ocean Biology Distributed Active Archive Center (OB.DAAC)][OB].
The following subsections provide additional information on the structure of this repo and maintenaner tasks.
Maintainers are responsible for building HTML files for publishing the content on the [Help Hub], which also tests that the notebooks run successfully in an isolated Python environment.
Here is how select contents of this repo map to the sections below:

```shell
.
├── CONTRIBUTING.md          # YOU ARE HERE
├── uv.lock                  # Isolated Environment
├── book                     # Rendering to HTML
├── pyproject.toml           # Dependencies
├── .pre-commit-config.yaml  # Automation and Checks
└── docker                   # Image for a JupyterHub
```

[OB]: https://www.earthdata.nasa.gov/centers/ob-daac
[Help Hub]: https://oceancolor.gsfc.nasa.gov/resources/docs/tutorials


Use the `uv` command line tool to create a Python environment for maintainer actions.
If needed, install `uv` as shown next or by one of [many other installation methods][uv].
Once `uv` is installed, it will keep the Python environment up to date, so you only need to install `uv` once.

> [!Important]
> This guide is itself a Jupytext Notebook: use right-click > "Open With" > "Notebook" and use the `bash` kernel to run code cells.

[uv]: https://docs.astral.sh/uv/getting-started/installation

```{code-cell}
curl -LsSf https://astral.sh/uv/install.sh | sh
```

## Isolated Environment

The `uv.lock` file defines the envrionment that should be sufficient to run the notebooks, and `uv` will install the packages listed here in a [Python virtual environment][venv] used for rendering to HTML.
If being conscientious about storage (e.g. if you are `jovyan` on a cloud-based JupyterHub), tell `uv` to use temporary directories using the following environment variables.
On a laptop or on-prem server, there are good reasons to not set these variables.

[venv]: https://docs.python.org/3/library/venv.html

> [!Important]
> The subsections below assume you have run the following cell to configure and activate the development environment. The last line ensures you can run a bash kernel from jupyter.

```{code-cell}
:scrolled: true

if [ $(whoami) = "jovyan" ]; then
  export UV_PROJECT_ENVIRONMENT=/tmp/uv/venv
  export UV_CACHE_DIR=/tmp/uv/cache
fi
uv sync
uv run python -m bash_kernel.install --sys-prefix
```

## Rendering to HTML

In addition to the ".md" files paired to notebooks, the `book` folder contains configuration for a [Jupyter Book].
Building the notebooks as one book provides smaller files for tutorial content, a single source of JavaScript and CSS, and tests that all notebooks run without errors.

> [!Important]
> Only notebooks listed in `book/_toc.yml` are built, so adding a new notebook requires updating `book/_toc.yml`.

The next cell builds the HTML in `book/_build/html`.
Presently (for `jupyter-book<2`), it's best to build from .ipynb rather than .md, so we generate clean notebooks and exclude (see `book/_config.yml`) the markdown files.

[Jupyter Book]: https://jupyterbook.org/

```{code-cell}
:scrolled: true

uv run jupytext --quiet --to ipynb $(git ls-files book/notebooks)
```

```{code-cell}
uv run jupyter --paths
```

```{code-cell}
:scrolled: true

uv run jupyter-book build book
```

That populates the `book/_build` folder.
The folder is ignored by git, but its contents can be provided to the website team.
The `_templates` make the website very plain, on purpose, for the benefit of the website team.
For a website with the same content but including navigation tools, comment out the `templates_path` part of `book/_config.yml` and rebuild the website.

Run the next cell to preview the website.
Interrupt the kernel (press ◾️ in the toolbar) to stop the server.

```{code-cell}
:scrolled: true

python -m http.server -d book/_build/html
```

> [!Note]
> On a JupyterHub? Try viewing at [/user-redirect/proxy/8000/](/user-redirect/proxy/8000/).

+++

## Dependencies

For every `import` statement, or if a notebook requires a package to be installed for a backend (e.g. h5netcdf),
make sure the package is listed in the `notebooks` array under the `dependency-groups` table in `pyproject.toml`.
You can add entries manually or using `uv add`.

```shell
uv add --group notebooks scipy
```

The other keys in the `dependency-groups` table provide additional dependencies,
which are needed for a working Jupyter kernel, for a complete JupyterLab in a Docker image, or for maintenance tasks.

+++

## Automation and Checks

We use several automations to get standard code formatting, run lint checks, and ensure consistency between ".md" and ".ipynb" files.
These are implemented using the [pre-commit] tool from the development environment.
You can setup git hooks to run these automations, as needed, at every commit.

[pre-commit]: https://pre-commit.com/

```{code-cell}
# pre-commit install ## TODO don't install yet, not working
```

You can also run checks over all files chaged on a feature branch or the currently checked out git ref. For the latter:

```{code-cell}
pre-commit run --from-ref main --to-ref HEAD
```

## Image for a JupyterHub

The `docker` folder has configuration files that [repo2docker] uses to build an image suitable for use with a JupyterHub platform.
The following command builds and runs the image locally, while the [repo2docker-action] pushes built images to GitHub packages.
You must have `docker` available to use `repo2docker`.

[repo2docker]: https://repo2docker.readthedocs.io/
[repo2docker-action]: https://github.com/marketplace/actions/repo2docker-action

```{code-cell}
:scrolled: true

# just need the latest repo2docker ...
# but, still need to resolve python version consistently
```

If you have `docker` available, you can build the image defined in the `docker` folder.

```{code-cell}
:scrolled: true

repo2docker \
    --Repo2Docker.platform=linux/amd64 \
    --appendix "$(< docker/appendix-cryocloud)" \
    --user-id 1000 \
    --user-name jovyan \
    --no-run \
    docker
```

> [!Important]
> - No `requirements.*` file in this repository should be manually edited.
> - Note where critical versions are pinned
>   - python: docker/environment.yml
>   - jupyter-repo2docker: .pre-commit-config.yaml

The configuration files are a bit complicated, but updated automatically by `pre-commit` hooks following changes to `pyproject.toml` and `docker/environment.yml`.
The `docker/environment.yml` file is there for non-Python packages needed from conda-forge.
We use PyPI for Python packages.

1. `requirements.txt` has the (locked) packages needed in `book/setup.py`
1. `docker/requirements.in` has the (frozen) packages from repo2docker and `docker/environment.yml`
1. `docker/requirements.txt` has the (locked) packages needed in the Docker image

> [!Note]
> The top-level `requirements.txt` file also makes our repo work on [Binder].

[Binder]: https://mybinder.org/

```{code-cell}

```
