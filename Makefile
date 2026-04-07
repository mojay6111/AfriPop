.PHONY: up down restart logs ps clean seed test

up:
	docker compose up -d

down:
	docker compose down

restart:
	docker compose down && docker compose up -d

logs:
	docker compose logs -f

ps:
	docker compose ps

clean:
	docker compose down -v --remove-orphans

seed:
	python3 database/seeds/demo_seed.py

test:
	bash scripts/run_tests.sh
