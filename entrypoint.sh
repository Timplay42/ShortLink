#!/usr/bin/env sh
set -e

if [ -n "$VIRTUAL_ENV" ]; then
  PYTHON_BIN="$VIRTUAL_ENV/bin/python"
elif [ -x ".venv/bin/python" ]; then
  PYTHON_BIN=".venv/bin/python"
else
  PYTHON_BIN="python3"
fi

echo "[entrypoint] waiting for database..."
"$PYTHON_BIN" -m Services.Auth.bootstrap_admin wait

echo "[entrypoint] applying database migrations..."
"$PYTHON_BIN" -m alembic upgrade head

echo "[entrypoint] ensuring admin user..."
"$PYTHON_BIN" -m Services.Auth.bootstrap_admin ensure

echo "[entrypoint] bootstrap finished"
exec "$PYTHON_BIN" app.py
