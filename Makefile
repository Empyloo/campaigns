PHONY: test
test:
	python -m pytest -vv

PHONY: install
install:
	pip install -r requirements.txt

PHONY: install-dev
install-dev:
	pip install -r requirements-dev.txt

PHONY: run
run:
	python -m main