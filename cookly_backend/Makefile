ifeq ($(OS),Windows_NT)
    OS := windows
else
    OS := $(shell uname -s | tr A-Z a-z)
endif

# Цели
.PHONY: all up build deps db dev clean

# Основная цель
all: deps db dev

check_docker:
ifeq ($(OS),windows)
	@docker ps > NUL 2>&1 || (echo "Docker is not running. Please start Docker and try again." && exit 1)
else
	@docker ps > /dev/null 2>&1 || (echo "Docker is not running. Please start Docker and try again." && exit 1)
endif

# Docker цели
up:
	docker-compose up

up-prod:
	docker-compose --profile grafana up

up-setup:
	docker-compose --profile setup up

up-m: check_docker
	docker-compose --profile migration up -d

build: check_docker
	docker-compose build

down:
	docker-compose down

up-non-log: check_docker
	docker-compose -f ./docker-compose-non-log.yml up

down-non-log: check_docker
	docker-compose -f ./docker-compose-non-log.yml down

up-dev: check_docker
	docker-compose -f ./docker-compose-local-dev.yml up --build

down-dev: check_docker
	docker-compose -f ./docker-compose-local-dev.yml down

deps:
	poetry install

dbo:
	cd auth_service && \
	alembic revision --autogenerate && \
#	alembic upgrade head


downgrade:
	cd auth_service && \
	alembic downgrade -1

uv:
	cd auth_service/src && \
	uvicorn presentation.web_auth_service.main:app --reload

server-prod:
	cd auth_service/src && \
	uvicorn presentation.web_auth_service.main:app --reload

nfy:
	cd notification/ && \
	python app.py

clean:
	poetry env remove python
	find . -type d -name "__pycache__" -exec rm -rf {} +
