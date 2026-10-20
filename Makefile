.DEFAULT_GOAL := help
PYTHON ?= python
.PHONY: help setup lint manifest build test verify prototype release hooks
help setup lint manifest build test verify prototype release hooks:
	$(PYTHON) tools/project.py $@
