.PHONY: install uninstall

PACKAGE := pcpm
PYTHON ?= python3

PIPX := $(shell command -v pipx 2>/dev/null)
PIP := $(shell command -v $(PYTHON) >/dev/null && echo "$(PYTHON) -m pip" || echo "")

install:
	@if [ -n "$(PIPX)" ]; then \
		echo "Installing $(PACKAGE) with pipx..."; \
		$(PIPX) install --force . || echo "Error: Failed to install $(PACKAGE) with pipx."; \
	elif [ -n "$(PIP)" ]; then \
		echo "Installing $(PACKAGE) with pip..."; \
		$(PIP) install --upgrade --break-system-packages . --user || echo "Error: Failed to install $(PACKAGE) with pip."; \
	else \
		echo "Error: Neither pipx nor pip are available. Please install one of them."; \
		exit 1; \
	fi

uninstall:
	@if [ -n "$(PIPX)" ]; then \
		echo "Uninstalling $(PACKAGE) with pipx..."; \
		$(PIPX) uninstall $(PACKAGE) || echo "Error: Failed to uninstall $(PACKAGE) with pipx."; \
	elif [ -n "$(PIP)" ]; then \
		echo "Uninstalling $(PACKAGE) with pip..."; \
		$(PIP) uninstall --yes --break-system-packages $(PACKAGE) --user || echo "Error: Failed to uninstall $(PACKAGE) with pip."; \
	else \
		echo "Error: Neither pipx nor pip are available. Please install one of them."; \
		exit 1; \
	fi