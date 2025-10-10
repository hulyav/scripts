Contributing to repo_stats
=========================

Thank you for contributing! This document explains how to set up a development environment, run tests, and use pre-commit hooks.

Local setup
-----------

1. Create a virtual environment and activate it (Linux/macOS):

```bash
cd repo_stats
python3 -m venv .venv
source .venv/bin/activate
```

2. Install dev dependencies and the package in editable mode:

```bash
pip install -r requirements-dev.txt
pip install -e .
```

3. Install pre-commit hooks:

```bash
pre-commit install -c .pre-commit-config.yaml
```

Running tests and linters
------------------------

- Run tests: `make test`
- Run linters: `make lint`
- Format code: `make format`

CI

There is a GitHub Actions workflow at `.github/workflows/ci.yml` that runs tests and linters on pushes and pull requests.

Code style
----------

We use Black and isort for formatting and flake8 for linting. Please run `pre-commit run --all-files` before opening a PR.

Reporting issues
----------------

Please open issues for bugs or feature requests on the upstream repository.

Thanks for contributing!
