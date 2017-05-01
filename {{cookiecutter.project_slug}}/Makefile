.DEFAULT_GOAL := help

.PHONY: requirements
requirements: ## Generate all the requirement files
	make -C requirements all

.PHONY: upgrade-requirements
upgrade-requirements: ## Upgrade the requirements
	make -C requirements clean
	make -C requirements all PIP_OPTIONS="--upgrade"

.PHONY: help
help: ## Display this help
	@grep -E '^[.a-zA-Z_-]+:.*?## .*$$' $(MAKEFILE_LIST) | sort -k 1,1 | awk 'BEGIN {FS = ":.*?## "}; {printf "\033[36m%-30s\033[0m %s\n", $$1, $$2}'
