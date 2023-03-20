lint:
	@echo "Running black:"
	@poetry run black --check .
	@echo "Running mypy:"
	@poetry run mypy .
	@echo "Running flake8:"
	@poetry run flake8 .
	@echo "Running isort:"
	@poetry run isort --check .
	
format:
	@echo "Running black:"
	@poetry run black .
	@echo "Running mypy:"
	@poetry run mypy .
	@echo "Running flake8:"
	@poetry run flake8 .
	@echo "Running isort:"
	@poetry run isort .
