#!/bin/sh
set -e

PACKAGE_HASH="$(sha256sum package.json | cut -d ' ' -f 1)"

if [ ! -d node_modules/.bin ] || [ ! -f node_modules/.package-json.sha ] || [ "$PACKAGE_HASH" != "$(cat node_modules/.package-json.sha)" ]; then
  echo "Installing frontend dependencies..."
  npm install --no-audit --no-fund
  echo "$PACKAGE_HASH" > node_modules/.package-json.sha
else
  echo "Frontend dependencies are up to date."
fi

exec npm run dev -- --host 0.0.0.0
