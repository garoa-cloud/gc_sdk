.PHONY: docs

fmt:
	poetry run black . && poetry run isort --profile=black --float-to-top .

test:
	poetry run pytest --verbose .

test-watch:
	poetry run ptw .

docs:
	pyreverse -ASmy -o html -d ./docs/ rpc

docs-server:
	mkdocs serve
