"""Pytest configuration for the scaffold's structural tests.

The tests never read data, but importing the scripts imports
``{{ cookiecutter.code_directory }}.settings``, which requires ``DATA_DIR``.
In CI there is no ``.env``, so give it a harmless default before anything is
imported. ``setdefault`` means a real ``.env`` or environment still wins.
"""

import os
from pathlib import Path

os.environ.setdefault("DATA_DIR", str(Path(__file__).resolve().parents[1] / "data"))
