#!/bin/bash
# Extract enabled packages with version info from config.json
PACKAGES=$(jq -c '[.packages[] | select(.enabled == true) | {name: .name, version: .version, build: .build, build_env: .build_env}]' config.json)
echo "matrix={\"package\":$PACKAGES}" >> "$1"
echo "Found packages to build:"
echo "$PACKAGES" | jq -r '.[] | "\(.name) v\(.version)-\(.build) (\(.build_env))"'
