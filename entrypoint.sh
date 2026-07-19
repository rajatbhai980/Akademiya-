#!/bin/sh

# Wait for Postgres to be available, run migrations, then exec the CMD

host="${DB_HOST:-db}"
port=${DB_PORT:-5432}

echo "Waiting for Postgres at $host:$port..."

while ! python - <<PY
import socket,sys
host="${host}"
port=${port}
try:
    s=socket.socket()
    s.settimeout(1)
    s.connect((host, port))
    s.close()
    sys.exit(0)
except Exception:
    sys.exit(1)
PY
do
  echo "Postgres is unavailable - sleeping"
  sleep 1
done

echo "Postgres is up - running migrations"
python manage.py migrate --noinput

exec "$@"
