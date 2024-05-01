.ONESHELL:

all: help

################################################################################
# PROJECT CONFIG
PROJECT_NAME := magic_circle
CONTAINER_NAME := backend
IMAGE_REGISTRY := registry.cojodi.com
IMAGE_NAME := $(PROJECT_NAME)/$(CONTAINER_NAME)
RELEASE_DATE := $(shell date -u +'%Y-%m-%dT%H:%M:%SZ')
RELEASE_DATE_TAG := $(shell date -u +'%Y-%m-%dT%H-%M-%SZ')

################################################################################
# DOCKER
docker: docker-build docker-push ## build and push the docker image, extra args with DOCKER_ARGS=... (e.g. --no-cache)

docker-push:
	docker image push $(IMAGE_REGISTRY)/$(IMAGE_NAME):latest
		&& docker image push $(IMAGE_REGISTRY)/$(IMAGE_NAME):$(RELEASE_DATE_TAG)

docker-build: ## build the docker image, extra args with DOCKER_ARGS=... (e.g. --no-cache)
	DOCKER_BUILDKIT=1 docker buildx build \
		$${DOCKER_ARGS} \
		--ssh default \
		--network host \
		--build-arg BUILD_DATE=$(RELEASE_DATE) \
		--build-arg VCS_REF=$(RELEASE_VERSION) \
		-t $(IMAGE_NAME):$(RELEASE_DATE_TAG) \
		-t $(IMAGE_NAME):latest \
		-t $(IMAGE_REGISTRY)/$(IMAGE_NAME):$(RELEASE_DATE_TAG) \
		-t $(IMAGE_REGISTRY)/$(IMAGE_NAME):latest \
		.

################################################################################
# RUN
run: ## run app=<backend>
	python3 -m magic_circle.run_$(app)

run-local: docker-build ## run a local docker-compose setup with all app parts
	docker compose -f dev-assets/docker-compose.local.yaml up -d

run-local-down: ## stop the local docker-compose setup
	docker compose -f dev-assets/docker-compose.local.yaml down -t 0

################################################################################
# ALEMBIC
DB_URL_MIGRATION := "mysql+asyncmy://root:root@127.0.0.1:3306/migration"

alembic-upgrade-head: ## upgrade database to latest revision
	export DB_URL=${DB_URL_MIGRATION}
	python3 -m alembic upgrade head

alembic-upgrade: ## upgrade database by one revision
	export DB_URL=${DB_URL_MIGRATION}
	python3 -m alembic upgrade +1

alembic-downgrade: ## downgrade database by one revision
	export DB_URL=${DB_URL_MIGRATION}
	python3 -m alembic downgrade -1

alembic-revision: ## create a database revision (alembic-revision msg='YOUR MESSAGE')
	@if [ -z "$$msg" ]; then
	@	echo "Usage: make alembic-revision msg='YOUR MESSAGE'"
	@	exit
	@fi
	export DB_URL=${DB_URL_MIGRATION}
	python3 -m alembic revision --autogenerate -m "$$msg"

################################################################################
# DEVELOPMENT
dev-db: ## start the dev db, calling this another time will clean and restart the db
	if [ -z "$$(docker ps | grep magic-circle-backend-dev-db)" ]; then \
		echo "Starthing db..."; \
		docker compose -f dev-assets/docker-compose.db.yaml up -d; \
	else \
		echo "Restarting db..."; \
		docker compose -f dev-assets/docker-compose.db.yaml -v down -t 0; \
		docker volume rm magic-circle-backend-dev-db; \
		docker compose -f dev-assets/docker-compose.db.yaml up -d; \
	fi

dev-redis: ## start redis
	docker compose -f dev-assets/docker-compose.redis.yaml up -d

################################################################################
# OPENAPI CLIENT
api-client: api-client-build api-client-publish ## build & publish openapi api-client

api-client-build: ## build openapi api-client
	sh ./dev-assets/generate-openapi-client $(version)

api-client-publish: ## publish openapi api-client
	cd magic-circle-backend-client/client && npm publish

################################################################################
# TESTS
test: test-unit test-e2e ## run all tests

test-unit: ## run unit tests
	python3 -m pytest -s tests/unit

test-e2e: ## run e2e tests
	python3 -m pytest -s tests/e2e

test-cov: ## run the tests with coverage
	python3 -m pytest -s tests \
        --cov-report term-missing:skip-covered \
        --cov-config pytest.ini \
        --cov=. tests/ \
        -vv

help: ## print help
	@grep '##' $(MAKEFILE_LIST) \
		| grep -Ev 'grep|###' \
		| sed -e 's/^\([^:]*\):[^#]*##\([^#]*\)$$/\1:\2/' \
		| awk -F ":" '{ printf "%-21s%s\n", $$1 ":", $$2 }' \
		| grep -v 'sed'
