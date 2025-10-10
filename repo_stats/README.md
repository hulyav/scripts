Repo Stats
===========

Quickstart
---------

Create a virtual environment, install dev dependencies, and run tests:

```bash
python -m venv .venv
source .venv/bin/activate
pip install -r requirements-dev.txt
pip install -e .
make test
```

Common targets:

- `make venv` - create `.venv`
- `make install` - install dev requirements
- `make test` - run pytest
- `make lint` - run flake8
- `make format` - run black and isort
