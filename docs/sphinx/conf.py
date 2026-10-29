# Configuration file for the Sphinx documentation builder.

import sys
from pathlib import Path

# Add the project root to Python path
project_root = Path(__file__).parent.parent.parent
sys.path.insert(0, str(project_root))

# Import the package to get version info
import doc_converter

# -- Project information -----------------------------------------------------
project = "Documents to Images Converter"
copyright = "2024, Kiran Raj Baral"
author = "Kiran Raj Baral"
release = doc_converter.__version__
version = doc_converter.__version__

# -- General configuration ---------------------------------------------------
extensions = [
    "sphinx.ext.autodoc",
    "sphinx.ext.autosummary",
    "sphinx.ext.viewcode",
    "sphinx.ext.intersphinx",
    "sphinx.ext.napoleon",
    "sphinx.ext.githubpages",
    "myst_parser",
    "sphinx_autodoc_typehints",
]

# Add any paths that contain templates here, relative to this directory.
templates_path = ["_templates"]

# List of patterns, relative to source directory, that match files and
# directories to ignore when looking for source files.
exclude_patterns = ["_build", "Thumbs.db", ".DS_Store"]

# The suffix(es) of source filenames.
source_suffix = {
    ".rst": None,
    ".md": None,
}

# The master toctree document.
master_doc = "index"

# -- Options for HTML output -------------------------------------------------
html_theme = "sphinx_rtd_theme"
html_theme_options = {
    "canonical_url": "",
    "analytics_id": "",
    "logo_only": False,
    "display_version": True,
    "prev_next_buttons_location": "bottom",
    "style_external_links": False,
    "collapse_navigation": True,
    "sticky_navigation": True,
    "navigation_depth": 4,
    "includehidden": True,
    "titles_only": False,
}

# Add any paths that contain custom static files (such as style sheets)
html_static_path = ["_static"]

# Custom sidebar templates, must be a dictionary that maps document names
# to template names.
html_sidebars = {
    "**": [
        "relations.html",  # needs 'show_related': True theme option to display
        "searchbox.html",
    ]
}

# -- Extension configuration -------------------------------------------------

# -- Options for autodoc ----------------------------------------------------
autodoc_default_options = {
    "members": True,
    "member-order": "bysource",
    "special-members": "__init__",
    "undoc-members": True,
    "exclude-members": "__weakref__",
}

# Don't show typehints in the signature
autodoc_typehints = "description"

# -- Options for intersphinx ------------------------------------------------
intersphinx_mapping = {
    "python": ("https://docs.python.org/3", None),
    "PIL": ("https://pillow.readthedocs.io/en/stable/", None),
}

# -- Options for Napoleon (Google/NumPy docstring support) ------------------
napoleon_google_docstring = True
napoleon_numpy_docstring = True
napoleon_include_init_with_doc = False
napoleon_include_private_with_doc = False
napoleon_include_special_with_doc = True
napoleon_use_admonition_for_examples = False
napoleon_use_admonition_for_notes = False
napoleon_use_admonition_for_references = False
napoleon_use_ivar = False
napoleon_use_param = True
napoleon_use_rtype = True
napoleon_preprocess_types = False
napoleon_type_aliases = None
napoleon_attr_annotations = True

# -- Options for autosummary ------------------------------------------------
autosummary_generate = True

# -- Options for MyST parser ------------------------------------------------
# MyST parser configuration
myst_enable_extensions = [
    "deflist",
    "tasklist",
    "colon_fence",
    "smartquotes",
    "replacements",
    "substitution",
]
