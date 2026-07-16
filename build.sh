#!/usr/bin/env bash
# Reproducible build: compile the curriculum, copy it into the explorer, build the
# static site. No cloud, no secrets, no runtime inference.
set -euo pipefail
REPO_ROOT="$(cd "$(dirname "$0")" && pwd)"

echo "== 1. compile curriculum (deterministic, no model) =="
python3 -m compiler.cli build --corpus corpus --out build --version v1

echo "== 2. copy artifact into explorer public/ =="
rm -rf apps/explorer/public/curriculum
mkdir -p apps/explorer/public/curriculum
cp -R build/v1/. apps/explorer/public/curriculum/

echo "== 3. build static explorer =="
cd apps/explorer
npm install
npx next build

echo "== done. static site in apps/explorer/out =="
