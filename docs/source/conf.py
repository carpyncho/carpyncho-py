# Configuration file for the Sphinx documentation builder.
#
# This file only contains a selection of the most common options. For a full
# list see the documentation:
# https://www.sphinx-doc.org/en/master/usage/configuration.html

# -- Path setup --------------------------------------------------------------

# If extensions (or modules to document with autodoc) are in another directory,
# add these directories to sys.path here. If the directory is relative to the
# documentation root, use os.path.abspath to make it absolute, like shown here.
#
import os
import sys
import pathlib


# this path is pointing to project/docs/source
CURRENT_PATH = pathlib.Path(os.path.abspath(os.path.dirname(__file__)))
CARPYNCHO_PATH = CURRENT_PATH.parent.parent

sys.path.insert(0, str(CARPYNCHO_PATH))

import carpyncho


# -- Project information -----------------------------------------------------

project = 'Carpyncho-py'
copyright = '2020, 2021, 2022, J.B. Cabral'
author = 'J.B. Cabral'

# The short X.Y version.
version = carpyncho.__version__
# The full version, including alpha/beta/rc tags
release = version


# -- General configuration ---------------------------------------------------

# Add any Sphinx extension module names here, as strings. They can be
# extensions coming with Sphinx (named 'sphinx.ext.*') or your custom
# ones.
extensions = ['sphinx.ext.autodoc',
    'sphinx.ext.doctest',
    'sphinx.ext.todo',
    'sphinx.ext.coverage',
    'sphinx.ext.mathjax',
    'sphinx.ext.ifconfig',
    'sphinx.ext.viewcode',
    'sphinx.ext.githubpages',
    'sphinx.ext.autodoc',
    'sphinx.ext.napoleon',
    'sphinx.ext.autosummary',

    'nbsphinx',
    'IPython.sphinxext.ipython_console_highlighting'
]

# nbsphinx
nbsphinx_execute = 'never'

nbsphinx_execute_arguments = [
    "--InlineBackend.figure_formats={'svg', 'pdf'}",
    "--InlineBackend.rc={'figure.dpi': 96}",
]


# Add any paths that contain templates here, relative to this directory.
templates_path = ['_templates']

# The language for content autogenerated by Sphinx. Refer to documentation
# for a list of supported languages.
#
# This is also used if you do content translation via gettext catalogs.
# Usually you set "language" from the command line for these cases.
language = 'en'

# List of patterns, relative to source directory, that match files and
# directories to ignore when looking for source files.
# This pattern also affects html_static_path and html_extra_path.
exclude_patterns = [
    'build',
    '**.ipynb_checkpoints',
    'source/.ipynb_checkpoints/*',
    'source/tutorial/.ipynb_checkpoints/*']

# The suffix(es) of source filenames.
# You can specify multiple suffix as a list of string:
#
# source_suffix = ['.rst', '.md']
source_suffix = ['.rst']

# The master toctree document.
master_doc = 'index'

# -- Options for HTML output -------------------------------------------------

# The theme to use for HTML and HTML Help pages.  See the documentation for
# a list of builtin themes.
#
html_theme = 'sphinx_rtd_theme'

# Add any paths that contain custom static files (such as style sheets) here,
# relative to this directory. They are copied after the builtin static files,
# so a file named "default.css" will overwrite the builtin "default.css".
html_static_path = ['_static']



# =============================================================================
# PREPROCESS RST
# =============================================================================

import m2r

with open(CARPYNCHO_PATH / "README.md") as fp:
    md = fp.read()


index = f"""

{m2r.convert(md)}

Contents:
---------

.. toctree::
    :maxdepth: 3

    tutorials/tutorials.rst
    api/modules.rst


Indices and tables
==================

* :ref:`genindex`
* :ref:`modindex`
* :ref:`search`

"""

with open(CURRENT_PATH / "index.rst", "w") as fp:
    fp.write(index)