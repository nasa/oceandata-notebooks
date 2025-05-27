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
> - This README is also recognized by Jupytext: use right-click > "Open With" > "Notebook".

Keeping notebooks (.ipynb) in a code repository is tough for collaboration because notebooks contain large, binary outputs and metadata that frequently changes.
By means of the [Jupytext] extension, markdown (.md) files can behave like notebooks without those bulky outputs.
To get the benefits of notebooks with saved outputs *while only* storing markdown files in a code repository, we let the Jupytext extension keep a paired markdown file synchronized with each notebook.
Contributors should compose and edit notebooks in the `notebooks` folder and commit the paired markdown files in the `book/notebooks` folder.

[Jupytext]: https://jupytext.readthedocs.io/

### Edit Notebooks

> [!Note]
> When you first clone this repository, the `notebooks` folder will not exist!

To create the `notebooks` folder, or any time a notebook does not appear under `notebooks`, run the following cell.
It will synchronize your .ipynb files with all the .md files tracked by git.

```{code-cell}
:scrolled: true

jupytext --sync $(git ls-files book/notebooks)
```

### Create a New Notebook

> [!Note]
> Create new notebooks by copying `COPYME.ipynb` into the `notebooks` folder.

When you save your new notebook, watch for a new markdown file to appear in the `book/notebooks` folder and add that file to your commit.

## For Maintainers

The following subsections provide additional information on the structure of this repo and maintenaner tasks.
Maintainers are responsible for building HTML files for hosting the content online, which also tests that the notebooks run successfully in an isolated Python environment.

> [!Warning]
> If you merge pull requests to `main`, you might be a maintainer.

Use the `uv` command line tool to create a Python environment for maintainer actions.
If needed, install `uv` as below or by one of [many other installation methods][uv].
Once `uv` is installed, it will keep the Python environment up to date, so you only need to install `uv` once.

```shell
curl -LsSf https://astral.sh/uv/install.sh | sh
```

[uv]: https://docs.astral.sh/uv/getting-started/installation

### Isolated Python Environment: the `uv.lock` file

The `uv.lock` file defines the envrionment used by maintainers, and `uv` will install packages based on its content.
If being conscientious about storage (e.g. if you are `jovyan` on a cloud-based JupyterHub), tell `uv` to use temporary directories.
On a laptop or on-prem server, there are good reasons not to set these variables.

> [!Important]
> The subsections below assume you have run the following cell to configure and activate the development environment.

```{code-cell}
if [ $(whoami) = "jovyan" ]; then
  export UV_PROJECT_ENVIRONMENT=/tmp/uv/venv
  export UV_CACHE_DIR=/tmp/uv/cache
fi
source ${UV_PROJECT_ENVIRONMENT:-.venv}/bin/activate
```

### Rendering to HTML: the `book` folder

In addition to the ".md" files paired to notebooks, the `book` folder contains configuration for a [Jupyter Book].
Building the notebooks as one book provides smaller files for tutorial content, a single source of JavaScript and CSS, and tests that all notebooks run without errors.

> [!Important]
> Only notebooks listed in `book/_toc.yml` are built, so adding a new notebook requires updating `book/_toc.yml`.

The next cell builds the HTML in `book/_build/html`.
Presently (for `jupyter-book<2`), it's best to build from .ipynb rather than .md, so we generate clean notebooks and exclude (see `book/_config.yml`) the markdown files.

[Jupyter Book]: https://jupyterbook.org/

```{code-cell}
:scrolled: true

jupytext --quiet --to ipynb $(git ls-files book/notebooks)
uv run --directory book jupyter book build .
```

That populates the `book/_build` folder.
The folder is ignored by git, but its contents can be provided to the website team.
The `_templates` make the website very plain, on purpose, for the benefit of the website team.
For a website with the same content but including navigation tools, comment out the `templates_path` part of `book/_config.yml` and rebuild the website.

Run the cell below to preview the website.
Interrupt the kernel (press ◾️ in the toolbar) to stop the server.

```{code-cell}
:scrolled: true

python -m http.server -d book/_build/html
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

### Automation and Checks: the `.pre-commit-config.yaml` file

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

## Acknowledgements

This repository has greatly benefited from works of multiple open-science projects, notably [Learn OLCI] and the [NASA EarthData Cloud Cookbook].

[Binder]: https://mybinder.org/
[Learn OLCI]: https://github.com/wekeo/learn-olci
[NASA EarthData Cloud Cookbook]: https://nasa-openscapes.github.io/earthdata-cloud-cookbook
