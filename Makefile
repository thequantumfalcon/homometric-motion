.DEFAULT_GOAL := help
PYTHON ?= python
.PHONY: help setup lint manifest build test verify phase-permutation reviewer-kit prototype finite-motion lean-setup lean release hooks demo-browser
help setup lint manifest build test verify phase-permutation reviewer-kit prototype finite-motion lean-setup lean release hooks demo-browser:
	$(PYTHON) tools/project.py $@
