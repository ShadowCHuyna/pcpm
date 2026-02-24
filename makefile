.PHONY: help install uninstall reinstall dev-install clean

PACKAGE := pcpm
PYTHON  ?= python3

VENV_ACTIVE := $(VIRTUAL_ENV)
PIPX        := $(shell command -v pipx 2>/dev/null)
PYTHON_BIN  := $(shell command -v $(PYTHON) 2>/dev/null)

help:
	@echo "Targets:"
	@echo "  install       Install package"
	@echo "  uninstall     Uninstall package"
	@echo "  reinstall     Reinstall package"
	@echo "  dev-install   Editable install"
	@echo "  clean         Remove build artifacts"

install:
	@if [ -n "$(VENV_ACTIVE)" ]; then \
		echo "Detected virtualenv: $(VENV_ACTIVE)"; \
		echo "Installing $(PACKAGE) into active venv..."; \
		$(PYTHON) -m pip install --upgrade .; \
	elif [ -n "$(PIPX)" ]; then \
		echo "Installing $(PACKAGE) globally via pipx..."; \
		$(PIPX) install --force .; \
	elif [ -n "$(PYTHON_BIN)" ]; then \
		echo "Attempting global installation via pip..."; \
		if $(PYTHON) -m pip install --upgrade --user . 2>&1 | grep -q externally-managed-environment; then \
			echo ""; \
			echo "System Python is externally managed (PEP 668)."; \
			printf "Install with --break-system-packages? [y/N]: "; \
			read ans; \
			if [ "$$ans" = "y" ] || [ "$$ans" = "Y" ]; then \
				$(PYTHON) -m pip install --upgrade --break-system-packages .; \
			else \
				echo "Aborted."; \
				exit 1; \
			fi; \
		fi; \
	else \
		echo "Error: python not found."; \
		exit 1; \
	fi

dev-install:
	@$(PYTHON) -m pip install -e .

uninstall:
	@if [ -n "$(VENV_ACTIVE)" ]; then \
		echo "Uninstalling $(PACKAGE) from active venv..."; \
		$(PYTHON) -m pip uninstall -y $(PACKAGE); \
	elif [ -n "$(PIPX)" ]; then \
		echo "Uninstalling $(PACKAGE) from pipx..."; \
		$(PIPX) uninstall $(PACKAGE); \
	elif [ -n "$(PYTHON_BIN)" ]; then \
		if $(PYTHON) -m pip uninstall -y $(PACKAGE) 2>&1 | grep -q externally-managed-environment; then \
			echo ""; \
			echo "System Python is externally managed (PEP 668)."; \
			printf "Uninstall with --break-system-packages? [y/N]: "; \
			read ans; \
			if [ "$$ans" = "y" ] || [ "$$ans" = "Y" ]; then \
				$(PYTHON) -m pip uninstall -y --break-system-packages $(PACKAGE); \
			else \
				echo "Aborted."; \
				exit 1; \
			fi; \
		else \
			$(PYTHON) -m pip uninstall -y $(PACKAGE); \
		fi; \
	else \
		echo "Error: python not found."; \
		exit 1; \
	fi

reinstall: uninstall install

clean:
	rm -rf build dist *.egg-info