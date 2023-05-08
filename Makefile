.PHONY: local
local:
	@(pip install -r requirements.txt; source .envs/.local; python3 -i src/main.py)

.PHONY: prod
prod: SHELL := /bin/bash
prod:
	@pip install -r requirements.txt
	@source .envs/.prod
	@sudo -E python3 src/main.py

.PHONY: deploy
deploy:
	@(./bin/deploy.sh $(ip))
