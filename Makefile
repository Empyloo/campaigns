PHONY: test
test:
	python -m pytest -vv $(file)

PHONY: install
install:
	pip install --upgrade pip
	pip install -r requirements.txt
	pip install -r requirements-test.txt

PHONY: run
run:
	python -m main