#!/bin/sh
# Run inside the isolated course PostgreSQL service. Uses unique temporary databases.
set -eu
export PGUSER="${POSTGRES_USER:-marlowe}"
work=$(mktemp -d)
src="marlowe_src_$$"
dst="marlowe_dst_$$"
createdb "$src"
dst_created=0
trap 'dropdb --if-exists "$src"; if [ "$dst_created" = 1 ]; then dropdb --if-exists "$dst"; fi; rm -f "$work/catalog.dump"; rmdir "$work"' EXIT
createdb "$dst"
dst_created=1
psql -X -v ON_ERROR_STOP=1 -d "$src" -c "CREATE EXTENSION vector; CREATE TABLE catalog(id text PRIMARY KEY,v vector(2)); INSERT INTO catalog VALUES ('mug','[1,0]'),('chair','[0,1]');"
pg_dump -Fc -d "$src" -f "$work/catalog.dump"
pg_restore --exit-on-error --no-owner -d "$dst" "$work/catalog.dump"
result=$(psql -XAt -d "$dst" -c "SELECT id FROM catalog ORDER BY v <=> '[1,0]' LIMIT 1")
test "$result" = mug
echo "Restored native archive: nearest item $result"
