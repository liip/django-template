.DEFAULT_GOAL := help

PIP_OPTIONS ?=

objects := base.txt dev.txt test.txt

all: $(objects)

base.txt: base.in ## Generate the base environment requirements
	pip-compile ${PIP_OPTIONS} base.in --output-file base.txt

dev.txt: dev.in base.in ## Generate the dev environment requirements
	pip-compile ${PIP_OPTIONS·} dev.in --output-file dev.txt

test.txt: test.in base.in ## Generate the test environment requirements
	pip-compile ${PIP_OPTIONS} test.in --output-file test.txt

.PHONY: clean
clean: 
	rm $(objects)

.PHONY: help
help: ## Display this help
	@grep -E '^[.a-zA-Z_-]+:.*?## .*$$' $(MAKEFILE_LIST) | sort -k 1,1 | awk 'BEGIN {FS = ":.*?## "}; {printf "\033[36m%-30s\033[0m %s\n", $$1, $$2}'
