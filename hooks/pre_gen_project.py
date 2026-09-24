"""Validate cookiecutter answers before the project is generated.

Cookiecutter aborts generation if this script exits with a non-zero status.
"""

import sys

data_dir = "{{ cookiecutter.data_dir }}"
examples = "{{ cookiecutter.examples }}"

if examples in ("data-science", "data-science-and-dashboard") and data_dir == "none":
    print(
        "ERROR: The data-science scaffold reads and writes data via DATA_DIR, "
        "so it requires a data directory. "
        "Choose 'local', 'github', or 'box' for data_dir, "
        "or pick a different examples option.",
        file=sys.stderr,
    )
    sys.exit(1)
