# Oceandata Notebooks

A repository for notebooks delivered as [oceandata tutorials and data recipes][1].

## Getting Started

> [!IMPORTANT]
> - Edit notebooks in JupyterLab so Jupytext can do its magic.
> - Create new notebooks in the `notebooks/` folder.
> - Open notebooks found only in the `src/` folder with **Open With** -> **Notebook** from the "right-click"
>    menu. Save and close the notebook. The notebook will now exist in the `notebooks/` folder.

Keeping notebooks in a code repository presents challenges for collaboration and curation,
because notebooks can contain very large blobs of binary outputs and they also include
constantly changing metadata. This repository contains ".py" files that the [Jupytext extension][2]
synchronizes with notebooks (".ipynb" files) in your working tree. The ".py" files live
in the `src/` folder and are commited to the repository. The paired ".ipynb" files live
in the `notebooks/` folder and are ignored by the repository. Other than the steps above,
just work on the ".ipynb" files, save your changes, and commit normally (well, almost ... git
only tracks the paired ".py" files and ignores the ".ipynb" files, so commit the ".py" files).

[1]: https://oceancolor.gsfc.nasa.gov/resources/docs/tutorials/
[2]: https://jupytext.readthedocs.io/
