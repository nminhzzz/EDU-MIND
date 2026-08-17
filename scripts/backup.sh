#!/bin/sh
set -eu

compose_file="${COMPOSE_FILE:-docker-compose.prod.yml}"
backup_root="${BACKUP_DIR:-./backups}"
timestamp="$(date -u +%Y%m%dT%H%M%SZ)"
target="$backup_root/$timestamp"

mkdir -p "$target"

docker compose -f "$compose_file" exec -T db sh -c \
  'exec mysqldump --single-transaction --routines --triggers -u"$MYSQL_USER" -p"$MYSQL_PASSWORD" "$MYSQL_DATABASE"' \
  | gzip > "$target/mysql.sql.gz"

docker compose -f "$compose_file" exec -T mongodb sh -c \
  'exec mongodump --quiet --archive --gzip -u "$MONGO_INITDB_ROOT_USERNAME" -p "$MONGO_INITDB_ROOT_PASSWORD" --authenticationDatabase admin' \
  > "$target/mongodb.archive.gz"

docker compose -f "$compose_file" exec -T redis sh -c \
  'redis-cli -a "$REDIS_PASSWORD" --no-auth-warning SAVE >/dev/null && cat /data/dump.rdb' \
  > "$target/redis.rdb"

docker compose -f "$compose_file" exec -T backend \
  tar -C /app -czf - uploads > "$target/uploads.tar.gz"

sha256sum "$target"/* > "$target/SHA256SUMS"

printf '%s\n' "Backup written to $target"
