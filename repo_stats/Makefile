.PHONY: venv install test lint format clean

VENV=.venv
PY=${VENV}/bin/python
PIP=${VENV}/bin/pip

venv:
	python -m venv ${VENV}

install: venv
	${PIP} install -r requirements-dev.txt
	${PIP} install -e .

test:
	${VENV}/bin/pytest -q

lint:
	${VENV}/bin/flake8 src tests

format:
	${VENV}/bin/black src tests
	${VENV}/bin/isort src tests

clean:
	rm -rf ${VENV} build dist *.egg-info
