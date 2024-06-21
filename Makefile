
test:
	.venv/bin/python  -m unittest discover tests/

venv:
	python -m venv .venv

pkg-install:
	.venv/bin/pip install \
	boto3 'boto3-stubs-lite[dynamodb]' \
	jsonpath_ng lxml pyyaml \