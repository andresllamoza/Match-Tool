.PHONY: test data-needed walk-amazon walk-walmart walk-citi funnel cli

cli:
	python3 engine_cli.py demo

test:
	python3 -m pytest -q

data-needed:
	python3 -c "from engine.data_needed import report; print(report())"

walk-amazon:
	python3 cli.py walk "Amazon.com Services LLC"

walk-walmart:
	python3 cli.py walk Walmart

walk-citi:
	python3 cli.py walk Citi --channel forms

funnel:
	python3 cli.py funnel
