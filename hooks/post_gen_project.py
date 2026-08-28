import os
import shutil
from datetime import datetime

use_cluster = "{{ cookiecutter.cluster }}" == "yes"
use_docker = "{{ cookiecutter.docker }}" == "yes"
use_data_dir = "{{ cookiecutter.data_dir }}" != "none"
use_local_data_dir = "{{ cookiecutter.data_dir }}" in ["local", "github"]
examples = "{{ cookiecutter.examples }}"
keep_bsd3 = f"{{ cookiecutter.bsd }}" == "yes"
use_annotations = f"{{ cookiecutter.ann }}" == "yes"
use_dashboard = "{{ cookiecutter.dashboard }}" == "yes"

if not use_cluster:
    shutil.rmtree("config")

if not use_docker:
    os.remove("Dockerfile")
    os.remove("docker-compose.yaml")

if not use_data_dir:
    os.remove("src/{{ cookiecutter.code_directory }}/settings.py")

if not use_local_data_dir:
    os.remove("data/README.md")
    os.rmdir("data")

if examples != "no":
    # Copy chosen example set into project root
    shutil.copytree(
        f"_examples/{examples.replace('-', '_')}", ".", dirs_exist_ok=True
    )

if use_dashboard:
    shutil.copytree("_examples/dashboard", "dashboard")

# Always remove the staging directory
shutil.rmtree("_examples")

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

if not use_dashboard:
    workflow = ".github/workflows/dashboard.workflow.yml"
    if os.path.exists(workflow):
        os.remove(workflow)
    export_py = "src/{{ cookiecutter.code_directory }}/dashboard_export.py"
    if os.path.exists(export_py):
        os.remove(export_py)
else:
    # Replace __PROJECT_NAME__ token in unrendered files
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
