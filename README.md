# Oceandata Notebooks

A repository for notebooks delivered as [oceandata tutorials and data recipes][tutorials].

## For Users

See [docs](docs/index.md).

## For Contributors

> [!IMPORTANT]
> - Edit notebooks in JupyterLab so Jupytext can do its magic.
> - Create new notebooks in the `notebooks/` folder.
> - Open notebooks found only in the `src/` folder with **Open With** -> **Notebook** from the "right-click"
>    menu. Save and close the notebook. The notebook will now exist in the `notebooks/` folder.

Keeping notebooks in a code repository presents challenges for collaboration and curation,
because notebooks can contain very large blobs of binary outputs and they also include
constantly changing metadata. This repository contains ".py" files that the [Jupytext extension][jupytext]
synchronizes with notebooks (".ipynb" files) in your working tree. The ".py" files live
in the `src/` folder and are commited to the repository. The paired ".ipynb" files live
in the `notebooks/` folder and are ignored by the repository. Other than the steps above,
just work on the ".ipynb" files, save your changes, and commit normally (well, almost ... git
only tracks the paired ".py" files and ignores the ".ipynb" files, so commit the ".py" files).

## For Maintainers

**WIP**:

1. Curating dependencies without duplicating between pyproject.toml and environment.yml
2. Formatting notebooks with black
3. Testing notebooks in isolated environments (using `jupyter execute ...`)
4. Auto populate `docs/` using:
   ```
   jupyter nbconvert --ClearOutputPreprocessor.enabled=True --ClearMetadataPreprocessor.enabled=True --to=notebook --output-dir=docs
   ```
5. Auto populate somewhere using:
   ```
   cd docs/oci
   jupyter nbconvert --to=html --execute *.ipynb
   ```

## How to Cite

**WIP**:

1. fill in once on Zenodo

## Acknowledgements
This repository has greatly benefited from works of multiple open-science projects, notably [Learn OLCI][learn-olci] and the [NASA EarthData Cloud Cookbook][cookbook].

[tutorials]: https://oceancolor.gsfc.nasa.gov/resources/docs/tutorials/
[jupyterlab]: https://jupyter.org/
[learn-olci]: https://github.com/wekeo/learn-olci/blob/main/README.md
[cookbook]: https://nasa-openscapes.github.io/earthdata-cloud-cookbook/