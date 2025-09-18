---
jupytext:
  text_representation:
    extension: .md
    format_name: myst
    format_version: 0.13
    jupytext_version: 1.17.2
kernelspec:
  name: bash
  language: bash
  display_name: Bash
---

# Maintainer's Guide

We are glad to have your help maintaining the [Help Hub] for the [Ocean Biology Distributed Active Archive Center (OB.DAAC)][OB].
You should already be familiar with the [README](README.md).
This guide provides additional information on the structure of this repository and maintenaner tasks.
Maintainers are responsible for:
1. ensuring the reproducible environment specifications are correct, and
2. publishing its content on the [Help Hub].

The following sections map to the contents of the repository as follows:

```shell
.
├── CONTRIBUTING.md          # (this document)
├── docs                     # -> GitHub Pages Website
├── uv.lock                  # -> Isolated Environment
├── pyproject.toml           # -> Dependencies
├── container                # -> Container Image for JupyterHub
└── .pre-commit-config.yaml  # -> Automation and Checks
```

Use the `uv` command line tool to create isolated Python environments for maintainer actions.
If `uv` is not already installed, install it by exectuing the cell below or some other documented [installation method][uv].

> [!Important]
> This guide is an executable MyST Markdown file: use right-click > "Open With" > "Notebook" to open, and select the `bash` kernel to run code cells on JupyterLab.

[OB]: https://www.earthdata.nasa.gov/centers/ob-daac/
[Help Hub]: https://nasa.github.io/oceandata-notebooks/
[uv]: https://docs.astral.sh/uv/getting-started/installation

```{code-cell}
if ! command -v uv; then
  curl -LsSf https://astral.sh/uv/install.sh | sh
fi
```

## GitHub Pages Website

The `docs` folder contains configuration and content for the [Jupyter Book] we host on [GitHub Pages].
For all tutorials, the content is formatted as executable MyST Markdown notebooks, and building the notebooks requires executing any tutorials that are not found in the cache.
We use [DVC] to share that cache among maintainers as well as to the deployment infrastructure on GitHub.

> [!Important]
> Only notebooks listed in `docs/_toc.yml` are built, so adding a new notebook requires updating `docs/_toc.yml`.

The next cell builds a static website in `docs/_build/html` using `jupyter-book<2`.

[Jupyter Book]: https://jupyterbook.org/
[DVC]: https://dvc.org/

```{code-cell}
uvx dvc pull
```

```{code-cell}

```

```{code-cell}
:scrolled: true

uv run jupytext --update --to ipynb $(git ls-files book/notebooks)
```

Now use `jupyter-book` to generate or update the `book/_build` folder.
This folder is ignored by git, but its contents are provided to the website team.

```{code-cell}
:scrolled: true

conda run --live-stream -n notebook jupyter-book build --all book
```

```{code-cell}
# uv run jcache notebook -p book/_build/.jupyter_cache invalidate
```

```{code-cell}
uv run jcache notebook -p book/_build/.jupyter_cache list
```

Run the next cell to preview the website.
Interrupt the kernel (press ◾️ in the toolbar) to stop the server.

```{code-cell}

```

```{code-cell}
:scrolled: true

python -m http.server -d book/_build/html
```

> [!Note]
> On a JupyterHub? Try viewing at [/user-redirect/proxy/8000/](/user-redirect/proxy/8000/).

The `_templates` make the website very plain, on purpose, for the benefit of the website.
For a navigable website with the same content, comment out the `templates_path` part of `book/_config.yml` and rebuild the website.

+++

## Isolated Environment

The `uv.lock` file defines the envrionment that should be sufficient to run the notebooks, and `uv` will install the packages listed here in a [Python virtual environment][venv] used for rendering to HTML.
If being conscientious about storage (e.g. if you are `jovyan` on a cloud-based JupyterHub), tell `uv` to use temporary directories using the following environment variables.
On a laptop or on-prem server, there are good reasons to not set these variables.

[venv]: https://docs.python.org/3/library/venv.html

> [!Important]
> The subsections below assume you have run the following cell to configure and activate the development environment. The last line ensures you can run a bash kernel from jupyter.

```{code-cell}
:scrolled: true

uv sync
```

```{code-cell}
:scrolled: true

uv run python -m bash_kernel.install --sys-prefix
```

## Jupyter-Cache

+++

Late effort method for use on cryo cloud ...

+++

First
```
jcache cache list
```
Followed by "y" in Terminal.

```{code-cell}
#jcache notebook add --reader jupytext book/notebooks/**/*.md
uv run jcache notebook add --reader jupytext book/notebooks/hackweek/oci_gpig.md
```

```{code-cell}
uv run jcache notebook list
```

```{code-cell}
:scrolled: true

uv run jcache project execute --executor temp-parallel --timeout -1
```

## Dependencies

For every `import` statement, or if a notebook requires a package to be installed for a backend (e.g. h5netcdf),
make sure the package is listed in the `notebooks` array under the `dependency-groups` table in `pyproject.toml`.
You can add entries manually or using `uv add`, for example:

```{code-cell}
uv add --group notebooks xarray
```

The other keys in the `dependency-groups` table provide the additional dependencies needed for a working Jupyter kernel, for a complete JupyterLab in a container image, or for maintenance tasks.

> [!Important]
> - No `requirements.*` file in this repository should be manually edited.
> - Note where critical versions are pinned
>   - python: docker/environment.yml
>   - jupyter-repo2docker: .pre-commit-config.yaml

The ontology of the `requirements.*` files is a bit complicated, but updates happen automatically by `pre-commit` when necessary, i.e. when there are changes to `pyproject.toml`, `docker/environment.yml`, or the `repo2docker` version.
The `docker/environment.yml` file is there for non-Python packages needed from conda-forge, as well as some special Python packages.
We use PyPI for Python packages when able.

1. `requirements.txt` lists the packages needed in `book/setup.py` (compile-kernel-dependencies)
1. `docker/requirements.txt` lists the packages needed in the container image (compile-docker-dependencies)
1. `docker/requirements.in` lists the packages resulting from `repo2docker` and `docker/environment.yml` (repo2docker-requirements)

> [!Note]
> Having a top-level `requirements.txt` file also makes our tutorials work on [Binder] ... most of them anyways.

[Binder]: https://mybinder.org/

## (WIP) Automation and Checks

We use several automations to get standard code formatting, run lint checks, and ensure consistency between ".md" and ".ipynb" files.
These are implemented using the [pre-commit] tool from the development environment.
You can setup git hooks to run these automations, as needed, at every commit.

[pre-commit]: https://pre-commit.com/

```{code-cell}
pre-commit install
```

You can also run checks over all files chaged on a feature branch or the currently checked out git ref. For the latter:

```{code-cell}
pre-commit run --from-ref main --to-ref HEAD
```

## Container Image for a JupyterHub

The `docker` folder has configuration files that [repo2docker] uses to build a container image suitable for use with a JupyterHub platform.
The following command builds and runs the image locally, while the [repo2docker-action] builds images on GitHub and distributes them via the GitHub Container Registry.

If you have `docker` available, you can build the image defined in the `docker` folder.

[repo2docker]: https://repo2docker.readthedocs.io/
[repo2docker-action]: https://github.com/marketplace/actions/repo2docker-action

```{code-cell}
:scrolled: true

repo2docker \
    --Repo2Docker.platform=linux/amd64 \
    --appendix "$(< docker/appendix)" \
    --user-id 1000 \
    --user-name jovyan \
    --no-run \
    docker
```
