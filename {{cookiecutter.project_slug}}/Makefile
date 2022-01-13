.DEFAULT_GOAL := help

REQUIREMENTS_DIR = requirements
objects = $(REQUIREMENTS_DIR)/base.txt $(REQUIREMENTS_DIR)/dev.txt $(REQUIREMENTS_DIR)/test.txt

requirements/%.txt: $(REQUIREMENTS_DIR)/%.in $(REQUIREMENTS_DIR)/base.in
	pip-compile $<

.PHONY: requirements
requirements: $(objects) ## Compile requirements with pip-compile

.PHONY: upgrade-requirements
upgrade-requirements: ## Upgrade and compile requirements with pip-compile --upgrade
	for file in $(REQUIREMENTS_DIR)/*.in; do \
		pip-compile --upgrade $$file; \
	done

.PHONY: sync-requirements
sync-requirements:
	pip-sync $(objects)

.PHONY: translations
translations: ## Regenerate .po files with ./manage.py makemessages
	./manage.py makemessages -a -i "deployment/*" -i "requirements/*" -i "virtualization/*" -i "node_modules/*"

.PHONY: compile-translations
compile-translations: ## Compile .po files with ./manage.py compilemessages
	./manage.py compilemessages

format:  # Fix some linting issues in the project
	black {{ cookiecutter.project_slug }} fabfile.py
	isort {{ cookiecutter.project_slug }} fabfile.py

lint:  # Show linting issues in the project
	flake8 {{ cookiecutter.project_slug }} fabfile.py

.PHONY: help
help: ## Display this help
	@grep -E '^[.a-zA-Z_-]+:.*?## .*$$' $(MAKEFILE_LIST) | sort -k 1,1 | awk 'BEGIN {FS = ":.*?## "}; {printf "\033[36m%-30s\033[0m %s\n", $$1, $$2}'

clean:
	rm $(objects)
