---
jupytext:
  text_representation:
    extension: .md
    format_name: myst
    format_version: 0.13
    jupytext_version: 1.18.1
kernelspec:
  display_name: Bash
  language: bash
  name: bash
---

# Maintainer's Guide

+++

We are glad to have your help maintaining the [Help Hub] for the [Ocean Biology Distributed Active Archive Center (OB.DAAC)][OB].
You should already be familiar with the [README](README.md).
This guide provides additional information on the structure of this repository and maintainer tasks.
Maintainers are responsible for:
1. ensuring the reproducible environment configuration is correct, and
2. publishing the notebooks to [GitHub Pages] as the [Help Hub] (a.k.a releasing!).

> [!IMPORTANT]
> 
> This guide is an executable MyST Markdown file: use right-click > "Open With" > "Notebook" to open, and select the `bash` kernel to run code cells on JupyterLab.

The following sections relate to the content of this repository as follows:

```shell
.
├── CONTRIBUTING.md          # (this document)
├── uv.lock                  # -> Isolated Environment
├── docs                     # -> GitHub Pages Website
├── pyproject.toml           # -> Dependencies
├── container                # -> Container Image for JupyterHubs
└── .pre-commit-config.yaml  # -> Automation and Checks
```

[OB]: https://www.earthdata.nasa.gov/centers/ob-daac
[Help Hub]: https://nasa.github.io/oceandata-notebooks
[GitHub Pages]: https://docs.github.com/en/pages

## Isolated Environment

The `conda-lock.yml` file gives a versioned list of all packages needed to run the tutorials;
it includes the packages specified in `pyproject.toml` along with all their dependencies.
The [conda-lock] tool will install these packages in an isolated conda [environment], which is used during the website build to ensure completeness.

[conda-lock]: https://conda.github.io/conda-lock/
[environment]: https://docs.conda.io/projects/conda/en/latest/user-guide/tasks/manage-environments.html

+++

Create the environment using `conda-lock install`.

```{code-cell}
:scrolled: true

conda-lock install --name env container/conda-lock.yml --extras jupyter --extras tools
```

Create a shorthand "envx" ("x" for execute) for the command meaning "run the following in the isolated environment while displaying output".

```{code-cell}
alias envx='conda run --no-capture-output --name env'
```

## GitHub Pages Website

### Build and Preview

The `docs` folder contains configuration and content for the [Jupyter Book] we host on GitHub Pages.
The tutorials are written in executable MyST Markdown, and publishing the website requires pulling execution results from a notebook cache.
We use [DVC] to share that cache among maintainers as well as to the deployment workflow on GitHub.

> [!IMPORTANT]
> Only notebooks listed in `docs/_toc.yml` are built, so adding a new notebook requires updating `docs/_toc.yml`.

The `dvc pull` command retrieves the notebook cache.
We execute it via `uv run` only because we've included the DVC tool in the project environment to simplify this workflow.

[Jupyter Book]: https://jupyterbook.org/
[DVC]: https://dvc.org/

```{code-cell}
envx dvc pull
```

Update the notebook cache as needed by executing notebooks.
We use the isolated virtual environment to make sure the environment configuration is correct.
We use `jcache` directly to achieve parallel execution.
For a full but slow test of the environment configuration, delete `docs/_cache` before executing.

```{code-cell}
:scrolled: true

envx jcache project -p docs/_cache execute --executor temp-parallel --timeout -1
```

The next cell builds a static website in `docs/_build/html` using `jupyter-book<2` (alias `jb`).

```{code-cell}
:scrolled: true

envx jb build docs
```

Run the next cell to preview the website.
Interrupt the kernel (press ◾️ in the toolbar) to stop the server.

> [!NOTE]
> On a JupyterHub? Try viewing at [/user-redirect/proxy/8000/](/user-redirect/proxy/8000/).

```{code-cell}
:scrolled: true

python -m http.server -d docs/_build/html
```

### Notebook Cache

If any notebooks have been executed, the updated notebook cache needs to be made available to the GitHub Action that deploys the website.
Follow the next steps to share the updates using DVC, starting with checking whether the cache has actually changed.

```{code-cell}
envx dvc status
```

If the status is not "Data and pipelines are up to date." then commit the updated cache with `dvc commit`. (The purpose of `--force` is only to skip the confirmation prompt that you can't interact with from within a notebook).

```{code-cell}
envx dvc commit --force
```

Now use `dvc` to push your cache to the remote location accessible to the website build.

```{code-cell}
:scrolled: true

envx dvc push
```

Finally, if changes are committed by DVC, then there will be changes you also need to commit with Git.
Use your preferred method of working with Git to stage the `docs/_cache.dvc` changes, commit, and push them.

### Temporary

(this won't be necessary with AWS CodeBuilder, and maybe there's some other solution)

Generate temporary credentials.

```python
import os
import boto3

client = boto3.client('sts')

with open(os.environ['AWS_WEB_IDENTITY_TOKEN_FILE']) as f:
    TOKEN = f.read()

response = client.assume_role_with_web_identity(
    RoleArn=os.environ['AWS_ROLE_ARN'],
    RoleSessionName=os.environ['JUPYTERHUB_CLIENT_ID'],
    WebIdentityToken=TOKEN,
    DurationSeconds=3600
)
secrets = response["Credentials"]
```

The `secrets` dictionary contains the "AccessKeyId", "SecretAccessKey", and "SessionToken" that a repo admin needs to provide to GitHub.

+++

### Publish (a.k.a. Release)

Website updates occur automatically whenever a pull request to main is merged.
The `.github/workflows/website.yaml` file provides the instructions to GitHub Actions.

## Dependencies

For every `import` statement, or if a notebook requires a package to be installed for a backend (e.g. h5netcdf),
make sure the package is listed in the `notebooks` array under the `dependency-groups` table in `pyproject.toml`.

The other keys in the `dependency-groups` table provide the additional dependencies needed for a working Jupyter kernel, for a complete JupyterLab in a container image, or for maintenance tasks.

> [!IMPORTANT]
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

> [!NOTE]
> Having a top-level `requirements.txt` file also makes our tutorials work on [Binder] ... most of them anyways.

[Binder]: https://mybinder.org/

## Container Image for JupyterHubs

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
envx pre-commit install
```

You can also run checks over all files chaged on a feature branch or the currently checked out git ref. For the latter:

```{code-cell}
envx pre-commit run --from-ref main --to-ref HEAD
```
