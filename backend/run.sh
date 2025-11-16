#!/bin/bash

# Скрипт для запуска приложения
# Убедитесь, что PostgreSQL и Redis запущены перед запуском

echo "Starting FastAPI application..."
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000


