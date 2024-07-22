# Oceandata Notebooks

A repository for notebooks published as [oceandata tutorials and data recipes][tutorials].

## For Contributors

> [!IMPORTANT]
> - Edit notebooks in JupyterLab so Jupytext can do its magic.
> - Create new notebooks within the `notebooks/` folder, starting from a a copy of "COPYME.ipynb".
> - If a notebook is missing from the `notebooks/` folder, but its paired ".py" file is present in
>   the `src/` folder, open a terminal from the project root and run `jupytext --sync src/**/*.py`.
> - Nothing in the `docs/` folder should be manually edited.

Keeping notebooks in a code repository presents challenges for collaboration and curation,
because notebooks can contain very large blobs of binary outputs and they also include
constantly changing metadata. This repository contains ".py" files that the [Jupytext extension][jupytext]
synchronizes with notebooks (".ipynb" files). The ".py" files live
in the `src/` folder and are commited to the repository. The paired ".ipynb" files live
in the `notebooks/` folder and are ignored by the repository. Other than the steps above,
just work on the ".ipynb" files, save your changes, and commit normally (well, almost ... git
only tracks the paired ".py" files and ignores the ".ipynb" files, so commit the ".py" files).

## For Maintainers

To prepare for a release, ensure that the clean notebooks are updated in the `docs/notebooks/` folder.
```
jupyter nbconvert --ClearOutputPreprocessor.enabled=True --ClearMetadataPreprocessor.enabled=True --to=notebook --output-dir=docs/notebooks notebooks/**/*.ipynb
```
Those are the (eventual) targets for the "Downloand and Run" links on the [tutorials][tutorials] page. Note that opening those notebooks in Jupyter will dirty them up again, so
do not include the changes introduced by opening the clean notebooks in any commit.

**WIP**:

1. Curating dependencies without duplicating between pyproject.toml and environment.yml
1. Formatting notebooks with black (although black does not format comments)
1. Testing notebooks in isolated environments (e.g. using `jupyter execute ...`)
1. Automatically generate HTML using:
   ```
   jupyter nbconvert --to=html --TemplateExporter.filters="{'markdown2html': 'nbconvert.filters.markdown.markdown2html_pandoc'}"  --execute notebooks/**/*.ipynb
   ```
   - TODO: automate `shopt -s globstar`
   - TODO: fails for oci_install_ocssw because of `%conda` cell.
   - TODO: https://github.com/jupyter/nbconvert/issues/1125

## How to Cite

**WIP**:

1. fill in once on Zenodo

## Acknowledgements
This repository has greatly benefited from works of multiple open-science projects, notably [Learn OLCI][learn-olci] and the [NASA EarthData Cloud Cookbook][cookbook].

[tutorials]: https://oceancolor.gsfc.nasa.gov/resources/docs/tutorials/
[jupyterlab]: https://jupyter.org/
[learn-olci]: https://github.com/wekeo/learn-olci/blob/main/README.md
[cookbook]: https://nasa-openscapes.github.io/earthdata-cloud-cookbook/