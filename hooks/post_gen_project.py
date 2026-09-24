import os
import re
import shutil
from datetime import datetime

use_cluster = "{{ cookiecutter.cluster }}" == "yes"
use_docker = "{{ cookiecutter.docker }}" == "yes"
use_data_dir = "{{ cookiecutter.data_dir }}" != "none"
use_github_data_dir = "{{ cookiecutter.data_dir }}" == "github"
examples = "{{ cookiecutter.examples }}"
keep_bsd3 = f"{{ cookiecutter.bsd }}" == "yes"
use_annotations = f"{{ cookiecutter.ann }}" == "yes"
use_data_science = examples in ("data-science", "data-science-and-dashboard")
use_dashboard = examples in ("dashboard", "data-science-and-dashboard")

if not use_cluster:
    shutil.rmtree("config")

if not use_docker:
    os.remove("Dockerfile")
    os.remove("docker-compose.yaml")

if not use_data_dir:
    os.remove("src/{{ cookiecutter.code_directory }}/settings.py")

if not use_github_data_dir:
    os.remove("data/README.md")
    os.rmdir("data")

# Each example set mirrors the project root; copy the chosen ones over it.
# Ignore local build artifacts that may exist when generating from a working
# checkout of the template (they are git-ignored, not committed).
example_sets = []
if examples == "generic":
    example_sets.append("generic")
if use_data_science:
    example_sets.append("data_science")
if use_dashboard:
    example_sets.append("dashboard")
for name in example_sets:
    shutil.copytree(
        f"_examples/{name}",
        ".",
        dirs_exist_ok=True,
        ignore=shutil.ignore_patterns(
            "node_modules",
            "dist",
            "test-results",
            "playwright-report",
            ".wrangler",
            "*.parquet",
            "*.parquet.tmp",
            ".env",
        ),
    )

# Always remove the staging directory
shutil.rmtree("_examples")

# Root docs are Jinja-conditional on examples/dashboard; drop them when empty
for doc in ("PROJECT_SETUP.md", "TUTORIAL.md"):
    if not use_data_science and not use_dashboard:
        os.remove(doc)
        continue
    # Each Jinja block tag leaves an empty line behind; squash the runs
    with open(doc) as f:
        text = re.sub(r"\n{3,}", "\n\n", f.read()).strip("\n") + "\n"
    with open(doc, "w") as f:
        f.write(text)

if not keep_bsd3:
    os.remove("LICENSE")
else:
    # change the year to current
    new_text_lines = []
    with open("LICENSE", "r") as f:
        old_text_lines = f.readlines()
    for line in old_text_lines:
        if "YEAR" in line:
            line = line.replace("YEAR", str(datetime.today().year), 1)
        new_text_lines.append(line)
    with open("LICENSE", "w") as f:
        f.writelines(new_text_lines)

if not use_annotations:
    # remove annotation line
    new_text_lines = []
    with open("pyproject.toml", "r") as f:
        old_text_lines = f.readlines()
    for line in old_text_lines:
        if "ANN" in line:
            line = ""
        new_text_lines.append(line)
    with open("pyproject.toml", "w") as f:
        f.writelines(new_text_lines)

if use_dashboard:
    # dashboard/ is copied without rendering (JSX braces); inject the name here
    project_name = "{{ cookiecutter.project_name }}"
    token_files = [
        "dashboard/index.html",
        "dashboard/README.md",
    ]
    for path in token_files:
        if os.path.exists(path):
            with open(path, "r") as f:
                content = f.read()
            content = content.replace("__PROJECT_NAME__", project_name)
            with open(path, "w") as f:
                f.write(content)
