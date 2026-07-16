#!/usr/bin/env bash
# Vercel build entrypoint.
# 1. Compile the curriculum from the seed corpus (deterministic, no model) using
#    the repo's pure-Python compiler. This regenerates apps/explorer/public/curriculum
#    which is gitignored and therefore absent in the Vercel checkout.
# 2. Build the static Next.js export.
set -euo pipefail

ROOT="$(cd "$(dirname "$0")/../../.." && pwd)"
cd "$ROOT"

echo "== compile curriculum =="
python3 -m compiler.cli build --corpus corpus --out build --version v1

echo "== copy artifact into explorer public/ =="
rm -rf apps/explorer/public/curriculum
mkdir -p apps/explorer/public/curriculum
cp -R build/v1/. apps/explorer/public/curriculum/

echo "== next build (static export) =="
cd apps/explorer
npx next build
