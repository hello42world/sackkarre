
python_libs= \
	boto3 'boto3-stubs-lite[dynamodb]' 'boto3-stubs-lite[lambda]' jsonpath_ng lxml pyyaml

test:
	.venv/bin/python  -m unittest discover tests/

venv:
	python -m venv .venv

pkg-install:
	.venv/bin/pip install $(python_libs)

lambda-build:
	[[ -d .build ]] && rm -r .build ; \
	mkdir .build && \
	.venv/bin/pip install \
		--target ./.build \
		--platform manylinux2014_x86_64 \
		--implementation cp \
		--python-version 3.12 \
		--only-binary=:all: --upgrade \
		$(python_libs) && \
	cp *.py .build && \
	cd .build && zip -r sackkarre.zip .