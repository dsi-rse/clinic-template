# Clinic Cookiecutter

The goal of this repository is to be a central location for templating University of Chicago Data Clinic projects. When updating this repository the following principals should be followed:
- Low overhead on developers: This cookiecutter is meant to create templates that can be used to quickly spin up new project repositories. Adding additional steps post creation or an endless series of prompts will reduce its usefullness. 
- Up to date with best practices: The tools used here should adhere as closely as possible to modern and popular methods
- Justify decisions: Decisions should be justified so future collaborators can make informed decisions as conditions change

## Usage

1. Install cookiecutter. `pip install cookiecutter`
2. Select this template to create a repository in the current directory. `cookiecutter https://github.com/uchicago-dsi/clinic-template`
3. Follow the prompts in your terminal.
4. Turn the directory into a git repository
    ```sh
    git init
    git add .
    git commit -m "Initial Commit"
    ```
5. We will follow the steps [here](https://docs.github.com/en/migrations/importing-source-code/using-the-command-line-to-import-source-code/adding-locally-hosted-code-to-github#adding-a-local-repository-to-github-using-git) to create repo on github and then push this repository. 
   1. Step \#1 is to crete an empty repo
   2. Step \#2 is to set the remote branch and then push. Note that the code below requires replacing the GH_ORG and the REPO_NAME.

    ```sh
    git remote add origin git@github.com:{{GH_ORG}}/{{REPO_NAME}}.git
    git branch -M main
    git push -u origin main
    ```

### Next steps

1. Did you add branch protections?
2. Set up additional users and permissions.

### Notes once complete 

The file ``DataPolicy.md" contains the _default_ data and code sharing policies for the project.

## Linter

To check for style, we use `ruff`. This run using `pre-commit`. [pre-commit](https://pre-commit.com/) is a tool for managing git hook scripts that we can use to run code checkers before git actions (like run `ruff` before every commit). If it fails, the commit will be blocked and the user will be shown what needs to be changed. We configure our linters with [pyproject.toml](https://packaging.python.org/en/latest/guides/writing-pyproject-toml/)


## GitHub

To run checkers on pull requests to `main` and `dev`, we use the `.github/workflows/main.workflow.yml` file.

## Contributing

The root directory of this repository contains files related to the cookiecutter itself. All generated repositories will have `{{ cookiecutter.project_slug }}` as its root directory. To make additions that are dependent on user prompts, add the variable to the `cookiecutter.json` file and reference the variable withing the `{{ cookiecutter.project_slug }}` directory using Jinja templating. 

For more information on cookiecutter, visit its [git repository](https://github.com/cookiecutter/cookiecutter)

### Dashboard scaffold (`dashboard/`)

The `{{ cookiecutter.project_slug }}/_examples/dashboard/` directory is listed
in `cookiecutter.json` under `_copy_without_render` (as `_examples/dashboard`);
the post-generation hook copies it to `dashboard/` in generated projects.  This
means cookiecutter copies every file in that directory **verbatim** — Jinja
expressions are never evaluated inside it.

**Critical:** never add Jinja syntax (`{{ ... }}`, `{% ... %}`, `${{ ... }}`)
to any file under `_examples/dashboard/`.  Any such expression would be copied literally
into generated projects, breaking the JavaScript/TypeScript source.  If you
need to inject a value into a dashboard file at generation time (e.g. the
project name in `index.html`), use a plain token like `__PROJECT_NAME__` and
replace it in `hooks/post_gen_project.py` — see the existing replacement block
there for the pattern.
