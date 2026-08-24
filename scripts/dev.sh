#!/usr/bin/env bash
set -euo pipefail

# Koreum OS dev helper — starts data services, runs migrations, launches backend + frontend
cd "$(dirname "$0")/.."

echo "==> Starting Postgres + Redis"
docker compose -f infrastructure/docker-compose.yml up -d postgres redis

echo "==> Waiting for Postgres..."
until docker exec koreum-postgres pg_isready -U koreum > /dev/null 2>&1; do
  sleep 1
done

echo "==> Running migrations"
(cd backend && alembic upgrade head)

echo "==> Starting backend (foreground)"
cd backend
uvicorn app.main:app --reload --port 8000
