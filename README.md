# Oceandata Notebooks

A repository for notebooks delivered as [oceandata tutorials and data recipes][1].

## Getting Started

TL;DR

1. Create new notebooks in the `notebooks/` folder.
2. Initialize notebooks found in the `src/` folder, but missing from your `notebooks/` folder, using "Open With" -> "Notebook".

Keeping notebooks, which can get very large, become full of binary outputs, and have
constantly changing metadata, in a code repository presents challenges for collaboration
and curation. This repository contains ".py" files that the [Jupytext extension][2]
synchronizes with notebooks (".ipynb" files) in your working tree. The ".py" files live
in the `src/` folder and are commited to the repository. The paired ".ipynb" files live
in the `notebooks/` folder and are ignored by the repository. Other than the steps above,
just work on the ".ipynb" files, save your changes, and commit normally!

[1]: https://oceancolor.gsfc.nasa.gov/resources/docs/tutorials/
[2]: https://jupytext.readthedocs.io/
