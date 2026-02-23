.PHONY: install uninstall

PACKAGE := pcpm
PYTHON ?= python3

install:
	@echo "Installing $(PACKAGE)..."
	@$(PYTHON) -m pip install --upgrade --break-system-packages .

uninstall:
	@echo "Uninstalling $(PACKAGE)..."
	@$(PYTHON) -m pip uninstall --yes --break-system-packages $(PACKAGE)