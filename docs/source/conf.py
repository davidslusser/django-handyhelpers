"""Sphinx configuration independent of the current working directory."""

import os
import sys
from datetime import datetime
from importlib import import_module
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT))
os.environ.setdefault("DJANGO_SETTINGS_MODULE", "handyhelpers_tests.handyhelpers_tests.settings")
django = import_module("django")
django.setup()
handyhelpers = import_module("handyhelpers")

project = handyhelpers.__title__
author = handyhelpers.__author__
copyright = f"{datetime.now().year}, {author}"
version = release = handyhelpers.__version__
extensions = ["sphinx.ext.autodoc", "sphinx.ext.doctest"]
source_suffix = ".rst"
master_doc = "index"
html_theme = "sphinx_rtd_theme"
html_static_path = []
exclude_patterns = []
