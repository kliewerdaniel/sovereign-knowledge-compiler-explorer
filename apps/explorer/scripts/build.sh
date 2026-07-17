#!/usr/bin/env bash
# Self-contained Vercel build entrypoint (runs with Root Directory = apps/explorer).
# 1. Compile the curriculum from the seed corpus (deterministic, no model) using
#    the bundled pure-Python compiler. This regenerates public/curriculum which
#    is gitignored and therefore absent in the Vercel checkout.
# 2. Build the Next.js app (served natively by Vercel; pages are prerendered).
set -euo pipefail
cd "$(dirname "$0")/.."   # -> apps/explorer

echo "== compile curriculum =="
python3 -m compiler.cli build --corpus corpus --out build --version v1

echo "== copy artifact into public/curriculum =="
rm -rf public/curriculum
mkdir -p public/curriculum
cp -R build/v1/. public/curriculum/

echo "== next build =="
npx next build
