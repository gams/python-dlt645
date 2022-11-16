.PHONY: docs
docs:
	poetry run make -C docs/ html
