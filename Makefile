.PHONY : help install update test lint clean build publish all

#
# Variables
#

PROJ = athena_federation
CONTAINER = athena-federation
VERSION = $(shell poetry version | cut -d' ' -f2)
IMG = local/$(CONTAINER):$(VERSION)
CLIENT_PORT = 9000
SERVER_PORT = 8080
PORTMAP = -p $(CLIENT_PORT):$(SERVER_PORT)
ARCH = amd64  # force to standard platform
PLAT = --platform=linux/$(ARCH)
BUILD = image build $(PLAT)
RUN = container run $(PLAT)

#
# Development
#

all: test

lock:
	poetry lock

# Install project dependencies
install: lock
	poetry install

# Update project dependencies
update:
	poetry update

# Run project tests
test:
	poetry run pytest --cov-report xml --cov=athena_federation

coverage:
	poetry run pytest --cov-report html --cov=athena_federation
	open htmlcov/index.html

watch:
	poetry run ptw . --now

# Lint code using flake8
lint:
	poetry run black .
	poetry run flake8
	poetry run mypy .

# Clean up generated files
clean:
	poetry run rm -rf dist build *cov* .*cache

# Build project distribution
build: lint
	poetry check
	poetry build

# Publish project to PyPI
publish: clean test build
	poetry publish

#
# Docker Commands
#

docker: docker-stop docker-build docker-detached lambda-ping lambda-list-schemas

# Verify Docker is running

docker-status:
	docker ps

# Build Docker image
docker-build:
	docker $(BUILD) -t $(IMG) .
	docker images | grep $(CONTAINER)

docker-debug:
	docker $(BUILD) . --no-cache --build-arg DEBUG=true

# One blog post claims this is necessary to get poetry to work in a docker container
docker-poetry-config:
	poetry config virtualenvs.in-project true --local

# Run Docker container

docker-run: docker-build
	docker $(RUN) --rm $(PORTMAP) $(IMG)

# Run Docker container in detached mode (untested)

docker-detached:
	docker $(RUN) -d  $(PORTMAP) $(IMG)
	sleep 5

# Stop Docker container

docker-stop:
	docker ps -q | xargs --no-run-if-empty docker stop


# Ping lambda

lambda-ping:
	curl -XPOST "http://localhost:9000/2015-03-31/functions/function/invocations" -d '{"@type": "PingRequest", "identity": {"id": "UNKNOWN", "principal": "UNKNOWN", "account": "123456789012", "arn": "arn:aws:iam::123456789012:root", "tags": {}, "groups": []}, "catalogName": "athena_python_sdk", "queryId": "1681559a-548b-4771-874c-2aa2ea7c39ab"}'

lambda-list-schemas:
	curl -XPOST "http://localhost:9000/2015-03-31/functions/function/invocations" -d '{"@type": "ListSchemasRequest", "identity": {"id": "UNKNOWN", "principal": "UNKNOWN", "account": "123456789012", "arn": "arn:aws:iam::123456789012:root", "tags": {}, "groups": []}, "catalogName": "athena_python_sdk", "queryId": "1681559a-548b-4771-874c-2aa2ea7c39ab"}'
