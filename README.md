# Oceandata Notebooks

A repository for notebooks published as [oceandata tutorials and data recipes][tutorials].

## For Contributors

> [!IMPORTANT]
> - Edit notebooks in JupyterLab so Jupytext can do its magic.
> - Create new notebooks under the `notebooks` folder, starting from a copy of `COPYME.ipynb`.
> - If a notebook is missing from the `notebooks` folder, but its paired ".py" file is present under
>   the `src/notebooks` folder, open a terminal from the project root and run `jupytext --sync src/notebooks/**/*.py`.

Keeping notebooks in a code repository presents challenges for collaboration and curation,
because notebooks can contain very large blobs of binary outputs and include
constantly changing metadata. This repository contains ".py" files that the [Jupytext extension][jupytext]
synchronizes with notebooks (".ipynb" files) in your clone. The ".py" files live
in the `src/notebooks` folder and are commited to the repository. The paired ".ipynb" files live
in the `notebooks` folder and are ignored by git. Other than the steps above,
just work on the ".ipynb" files, save your changes, and commit normally (well, almost ... git
only tracks the paired ".py" files and ignores the ".ipynb" files, so commit the ".py" files).

## For Maintainers

TODO:
  - pre-commit
    - ruff lint and fmt

For building the HTML
```
$ uv sync --extra dev
$ source .venv/activate
(oceandata-notebooks) $ jb build src
```

### Dependencies

For packages imported into notebooks:
```
$ uv add scipy
```


<!-- Check that conda can solve it.
```
$ conda create --name=oc --file=requirements.txt
```

FIXME: and this is where we fail b/c we need to specify that some packages come from
pypi not conda-forge
- conda create -n oc pip; conda run -n oc pip install -r requirements
- keep environment.yml and pip freeze?
- pipx script with locked requirements? <- works! but need a way to embed requirements. -->

okay, so let's try to get this all as a book,
with requirements.txt "built" into the insall script that
is referenced in the index.html (is an asset).

need to get jb build to run custom script.

uv pip compile ... could be a pre-commit?

### Repo2docker Image

now image definition for binderhub, oss (using repo2docker subdir)

### Building HTML

In addition to the ".py" files paired to notebooks, the `src` folder contains configuration
for a [Jupyter Book][jb]. Building the notebooks as one book allows for separation
of content from the JavaScript and CSS, unlike standalone HTML files built with `nbconvert`. It also provides
a way to test that all notebook are free of errors. Run the following commands in an environment with
all dependencies along with the jupyter-book and jupytext packages.

```
jb build src
```
That populates the `src/_build` folder. The folder is (mostly) ignored by git.

The second step needs globstar (a.k.a. `**` patterns) enabled in bash, so we do that first and then call jupytext.
```
shopt -s globstar
jupytext --to=notebook src/_build/**/*.py  # TODO: with metadata filter?
```
That writes an unpaired ".ipynb" format to the ".py" format sources under `src/_build`. These files are not
ignored by git. They are (will be, eventually) targets for the "Downloand and Run" links on the [tutorials][tutorials]
page. Note that opening those notebooks in Jupyter will dirty them up again, so
do not include the changes introduced by opening the clean notebooks in any commit.

FIXME: seems to be a bug in the chain from jb build src that does not add the reader to the jcache.
```
cd src
jcache notebook -p _build/.jupyter_cache list
```
Add notebooks to the jupyter cache with something like this:
```
jcache notebook -p _build/.jupyter_cache add -r jupytext notebooks/hackweek/<new_notebook>.py
```
After builds that use the case, merge the cache output into the notebook (do this for all notebooks).
```
for f in notebooks/hackweek/*.py; do
  jcache notebook -p _build/.jupyter_cache merge ${f} _build/jupyter_execute/${f%.*}.ipynb
done
```


The `src/_ext` folder includes a local Sphinx extension that adds the ".ipynb" download
button to the article header buttons. It has no effect, however, when the `_templates` configration
is uncommented, because the provided template removes all the buttons. TODO: keep desired buttons.

**WIP**:

1. Curating dependencies without duplicating between pyproject.toml and environment.yml
1. Formatting notebooks with black (although black does not format markdown)
1. Building notebooks in an isolated environment
1. Automate `shopt -s globstar`
1. Fails for oci_install_ocssw because of `%conda` cell.
1. https://github.com/jupyter/nbconvert/issues/1125
1. random cell ids, preserved id metadata from notebooks? (https://github.com/mwouts/jupytext/issues/1263)
1. stop doing manual copy of animation to ../../img

## How to Cite

**WIP**:

1. fill in once on Zenodo

## Acknowledgements
This repository has greatly benefited from works of multiple open-science projects, notably [Learn OLCI][learn-olci] and the [NASA EarthData Cloud Cookbook][cookbook].

[tutorials]: https://oceancolor.gsfc.nasa.gov/resources/docs/tutorials
[jupytext]: https://jupytext.readthedocs.io/
[jupyterlab]: https://jupyter.org
[jb]: https://jupyterbook.org
[learn-olci]: https://github.com/wekeo/learn-olci/blob/main/README.md
[cookbook]: https://nasa-openscapes.github.io/earthdata-cloud-cookbook
