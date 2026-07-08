# chime_tts developer tasks. Run inside the test venv:
#   python3 -m venv .venv && . .venv/bin/activate && pip install -r requirements_test.txt
#
# To test against the latest Home Assistant (which needs Python 3.13/3.14), use
# `make venv-latest` and activate .venv314. Latest HA is the primary target.

PKG := custom_components/chime_tts
HA_HOST ?=
HA_PORT ?= 22
HA_USER ?= root
HA_PATH ?= /config/custom_components/chime_tts

.PHONY: help install venv-latest lint format format-fix typecheck test test-strict cov matrix deploy-restart clean

help:
	@grep -E '^[a-zA-Z_-]+:.*?# .*$$' $(MAKEFILE_LIST) | \
		awk 'BEGIN{FS=":.*?# "}{printf "  %-16s %s\n", $$1, $$2}'

install: # install the test/lint/type stack into the active venv
	pip install -r requirements_test.txt

venv-latest: # build .venv314 (Python 3.14) with the latest Home Assistant for testing
	# Latest HA (2026.6.x) declares requires-python >=3.14.2, so 3.14 is required
	# here; 3.13 resolves to an older HA and would not test the current release.
	uv venv --python 3.14 .venv314
	. .venv314/bin/activate && uv pip install -r requirements_test.txt
	@echo "Activate with: . .venv314/bin/activate"

lint: # ruff lint
	ruff check $(PKG) tests

format: # check formatting only
	ruff format --check $(PKG) tests

format-fix: # apply formatting
	ruff format $(PKG) tests

typecheck: # mypy
	mypy $(PKG)

test: # run tests with a coverage report
	pytest tests/ --cov=$(PKG) --cov-report=term-missing

test-strict: # tests + 80% coverage gate (pre-PR)
	pytest tests/ --cov=$(PKG) --cov-report=term-missing --cov-fail-under=80

cov: # html coverage report
	pytest tests/ --cov=$(PKG) --cov-report=html && echo "open htmlcov/index.html"

matrix: # run the full HA version matrix (tox)
	tox

deploy-restart: # rsync the integration to a live HA host and restart it
	@test -n "$(HA_HOST)" || { echo "set HA_HOST=<ip>"; exit 1; }
	rsync -az --delete -e "ssh -p $(HA_PORT)" \
		$(PKG)/ $(HA_USER)@$(HA_HOST):$(HA_PATH)/
	ssh -p $(HA_PORT) $(HA_USER)@$(HA_HOST) 'ha core restart'

clean:
	rm -rf .pytest_cache .mypy_cache .ruff_cache htmlcov .coverage .tox
