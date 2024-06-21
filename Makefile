
.PHONY: test venv pkg-install lambda-build aws-deploy 

python_libs= \
	boto3 \
	'boto3-stubs-lite[dynamodb]' \
	'boto3-stubs-lite[lambda]' \
	'boto3-stubs-lite[sns]' \
	'boto3-stubs-lite[iam]' \
	jsonpath_ng lxml \
	tabulate \
	pyyaml

.venv:
	python -m venv .venv

venv: .venv

pkg-install: venv
	.venv/bin/pip install $(python_libs)

test: venv pkg-install
	.venv/bin/python -m unittest discover tests/

lambda-build: venv
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

aws-deploy: lambda-build
	.venv/bin/python main.py aws-deploy