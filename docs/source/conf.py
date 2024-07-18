# -*- coding: utf-8 -*-
#
# deployfish documentation build configuration file, created by
# sphinx-quickstart on Tue Jun 13 16:54:27 2017.
#
# This file is execfile()d with the current directory set to its
# containing dir.
#
# Note that not all possible configuration values are present in this
# autogenerated file.
#
# All configuration values have a default; values that are commented out
# serve to show the default.

# If extensions (or modules to document with autodoc) are in another directory,
# add these directories to sys.path here. If the directory is relative to the
# documentation root, use os.path.abspath to make it absolute, like shown here.
#
import os
import sys
from typing import List, Dict, Any, Tuple, Optional
sys.path.insert(0, os.path.abspath('../..'))

import sphinx_rtd_theme

# -- General configuration ------------------------------------------------

# If your documentation needs a minimal Sphinx version, state it here.
#
# needs_sphinx = '1.0'

# Add any Sphinx extension module names here, as strings. They can be
# extensions coming with Sphinx (named 'sphinx.ext.*') or your custom
# ones.
extensions: List[str] = [
    'sphinx.ext.autodoc',
    'sphinx.ext.napoleon',
    'sphinx.ext.viewcode',
    'sphinx.ext.intersphinx',
    'sphinx_rtd_theme'
]

# Add any paths that contain templates here, relative to this directory.
templates_path: List[str] = ['_templates']

# The suffix(es) of source filenames.
# You can specify multiple suffix as a list of string:
#
# source_suffix = ['.rst', '.md']
source_suffix: str = '.rst'

# The master toctree document.
master_doc: str = 'index'

# General information about the project.
project: str = 'Deployfish'
copyright: str = 'Caltech IMSS ADS'  # pylint: disable=redefined-builtin
author: str = 'Chris Malek, Glenn Bach'

show_authors = False

version: str = '1.12.5'
release: str = '1.12.5'

# List of patterns, relative to source directory, that match files and
# directories to ignore when looking for source files.
# This patterns also effect to html_static_path and html_extra_path
exclude_patterns: List[str] = []

add_function_parentheses: bool = False
add_module_names: bool = True

autodoc_member_order: str = 'bysource'
autodoc_type_aliases: Dict[str, str] = {}

# the locations and names of other projects that should be linked to this one
intersphinx_mapping: Dict[str, Tuple[str, Optional[str]]] = {
    'python': ('https://docs.python.org/3', None),
    'boto3': ('https://boto3.amazonaws.com/v1/documentation/api/latest/', None),
}

# The name of the Pygments (syntax highlighting) style to use.
pygments_style: str = 'sphinx'

# If true, `todo` and `todoList` produce output, else they produce nothing.
todo_include_todos: bool = False


# -- Options for HTML output ----------------------------------------------

html_theme: str = "sphinx_rtd_theme"
html_theme_path: List[str] = [sphinx_rtd_theme.get_html_theme_path()]
html_context: Dict[str, Any] = {
    "display_github": True,
    "github_user": "caltechads",
    "github_repo": "deployfish",
    "github_version": "master",
    "conf_py_path": "/docs/source/",
}
html_theme_options: Dict[str, Any] = {
    'collapse_navigation': True,
    'display_version': True,
    'navigation_depth': 3,
}

# Add any paths that contain custom static files (such as style sheets) here,
# relative to this directory. They are copied after the builtin static files,
# so a file named "default.css" will overwrite the builtin "default.css".
# html_static_path: List[str] = ['_static']
