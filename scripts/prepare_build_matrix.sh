#!/bin/bash
# Extract enabled packages with version info from config.json, derive version from tag
PACKAGES=$(jq -c '[.packages[] | select(.enabled == true) | {name: .name, version: (.tag | match("^v(?<v>[0-9].*)").v // .tag), build: .build, build_env: .build_env}]' config.json)
echo "matrix={\"package\":$PACKAGES}" >> "$1"
echo "Found packages to build:"
echo "$PACKAGES" | jq -r '.[] | "\(.name) v\(.version)-\(.build) (\(.build_env))"'
