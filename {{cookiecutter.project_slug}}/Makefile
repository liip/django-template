.DEFAULT_GOAL := help

.PHONY: translations
translations: ## Regenerate .po files with ./manage.py makemessages
	./manage.py makemessages -a -i "deployment/*" -i "requirements/*" -i "virtualization/*"

.PHONY: help
help: ## Display this help
	@grep -E '^[.a-zA-Z_-]+:.*?## .*$$' $(MAKEFILE_LIST) | sort -k 1,1 | awk 'BEGIN {FS = ":.*?## "}; {printf "\033[36m%-30s\033[0m %s\n", $$1, $$2}'

