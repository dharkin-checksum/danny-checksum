#!/usr/bin/env bash
set -euo pipefail

SHA=$(git rev-parse HEAD)
curl -X POST http://localhost:8000/deployment \
  -H "Content-Type: application/json" \
  -d "{\"component\": \"component1\", \"sha\": \"$SHA\"}"
