REQUIREMENTS_DIR = requirements
objects = $(REQUIREMENTS_DIR)/base.txt $(REQUIREMENTS_DIR)/dev.txt

all: requirements

requirements/%.txt: $(REQUIREMENTS_DIR)/%.in $(REQUIREMENTS_DIR)/base.in
	pip-compile $<

.PHONY: requirements
requirements: $(objects)

.PHONY: upgrade-requirements
upgrade-requirements:
	for file in $(REQUIREMENTS_DIR)/*.in; do \
		pip-compile --upgrade $$file; \
	done

clean:
	rm $(objects)
