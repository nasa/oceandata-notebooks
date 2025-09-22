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
1. ensuring the reproducible environment configuration is correct, and
2. publishing the notebooks to [GitHub Pages] as the [Help Hub] (a.k.a releasing!).

The following sections map to the contents of the repository as follows:

```shell
.
├── CONTRIBUTING.md          # (this document)
├── uv.lock                  # -> Isolated Environment
├── docs                     # -> GitHub Pages Website
├── pyproject.toml           # -> Dependencies
├── container                # -> Container Image for JupyterHub
└── .pre-commit-config.yaml  # -> Automation and Checks
```

[OB]: https://www.earthdata.nasa.gov/centers/ob-daac
[Help Hub]: https://nasa.github.io/oceandata-notebooks
[GitHub Pages]: https://docs.github.com/en/pages

## Isolated Environment

The `pyproject.toml` file lists all packages for an envrionment meant to be sufficient for running all notebooks.
The `uv.lock` file gives a versioned list of all the packages installed when creating the environment;
it includes dependencies along with the packages listed in `pyproject.toml`.
The `uv` tool will install packages in a clean [Python virtual environment][venv], which is used during the website build to ensure completeness.
If `uv` is not already installed, install it by exectuing the cell below or by some other documented [installation method][uv].

> [!Important]
> This guide is an executable MyST Markdown file: use right-click > "Open With" > "Notebook" to open, and select the `bash` kernel to run code cells on JupyterLab.

[uv]: https://docs.astral.sh/uv/getting-started/installation
[venv]: https://docs.python.org/3/library/venv.html

```{code-cell}
if ! command -v uv; then
  curl -LsSf https://astral.sh/uv/install.sh | sh
fi
```

Create the environment using the `sync` subcommand.

```{code-cell}
:scrolled: true

uv sync
```

The `run` subcommand works in the environment, and our first use is installing the bash kernel:

```{code-cell}
:scrolled: true

uv run python -m bash_kernel.install --sys-prefix
```

## GitHub Pages Website

### Preview

The `docs` folder contains configuration and content for the [Jupyter Book] we host on GitHub Pages.
The tutorials are written as executable MyST Markdown notebooks, and publishing the website requires executing tutorials ... unless they are in the cache.
We use [DVC] to share that cache among maintainers as well as to the deployment workflow on GitHub.

> [!Important]
> Only notebooks listed in `docs/_toc.yml` are built, so adding a new notebook requires updating `docs/_toc.yml`.

The next cell builds a static website in `docs/_build/html` using `jupyter-book<2`.

[Jupyter Book]: https://jupyterbook.org/
[DVC]: https://dvc.org/

```{code-cell}
uv run dvc pull
```

Now use Jupyter Book (alias `jb`) to generate or update the `docs/_build` folder.

```{code-cell}
:scrolled: true

uv run jb build docs
```

Run the next cell to preview the website.
Interrupt the kernel (press ◾️ in the toolbar) to stop the server.

```{code-cell}
:scrolled: true

python -m http.server -d docs/_build/html
```

> [!Note]
> On a JupyterHub? Try viewing at [/user-redirect/proxy/8000/](/user-redirect/proxy/8000/).

### Publish (a.k.a. Release)

If any notebooks have been executed, rather than built using cached outputs, there are three steps for making the new outputs available to the GitHub Action that deploys the website.
First, commit the updated cache with `dvc commit`.

```{code-cell}
uv run dvc commit
```

Second, use `dvc` to push your cache to the remote location accessible to the website build.

```{code-cell}
uv run dvc push
```

Third, if there are changes committed by DVC, then there will be changes you need to commit with Git as well.
Use your preferred method of working with Git to stage the `docs/_cache.dvc` changes, commit, and push them.

**Fourth** (this won't be necessary with AWS CodeBuilder, and maybe there's some other solution).
- generate temp aws credentials
- todo: aws credentials to github actions

### Jupyter-Cache

Alternatively, and with the option for parallel notebook execution, update the cache without building the book.

```{code-cell}
:scrolled: true

uv run jcache project -p docs/_cache execute --executor temp-parallel --timeout -1
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
>   - python: container/environment.yml
>   - jupyter-repo2docker: .pre-commit-config.yaml

The ontology of the `requirements.*` files is a bit complicated, but updates happen automatically by `pre-commit` when necessary, i.e. when there are changes to `pyproject.toml`, `container/environment.yml`, or the `repo2docker` version.
The `container/environment.yml` file is there for non-Python packages needed from conda-forge, as well as some special Python packages.
We use PyPI for Python packages when able.

1. `requirements.txt` lists the packages needed in `docs/setup.py` (export-kernel-dependencies)
1. `container/requirements.txt` lists the packages needed in the container image (export-container-dependencies)
1. `container/requirements.in` lists the packages resulting from `repo2docker` and `container/environment.yml` (repo2docker-requirements)

> [!Note]
> Having a top-level `requirements.txt` file also makes our tutorials work on [Binder] ... most of them anyways.

[Binder]: https://mybinder.org/

## Container Image for a JupyterHub

The `container` folder has configuration files that [repo2docker] uses to build a container image suitable for use with a JupyterHub platform.
The following command builds and runs the image locally, while the [repo2docker-action] builds images on GitHub and distributes them via the GitHub Container Registry.

If you have Docker available, you can build the image defined in the `container` folder.

[repo2docker]: https://repo2docker.readthedocs.io/
[repo2docker-action]: https://github.com/marketplace/actions/repo2docker-action

```{code-cell}
:scrolled: true

repo2docker \
    --Repo2Docker.platform=linux/amd64 \
    --appendix "$(< container/appendix)" \
    --user-id 1000 \
    --user-name jovyan \
    --no-run \
    container
```

## (WIP) Automation and Checks

We use several automations to get improve code formatting, and run checks or update.
These are implemented using the [pre-commit] tool from the development environment.
You may create hooks to run these automations, as needed, before making any commits.

[pre-commit]: https://pre-commit.com/

```{code-cell}
uv run pre-commit install
```

You can also run checks over all files chaged on a feature branch or the currently checked out git ref. For the latter:

```{code-cell}
uv run pre-commit run --from-ref main --to-ref HEAD
```
