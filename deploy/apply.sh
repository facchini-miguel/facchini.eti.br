#!/bin/bash
# Run on your machine: copies compose.yml and setup.sh to the VPS (~/site) and runs setup.sh
# there, which creates or updates the site in Dokploy, deploys it and checks it.
set -euo pipefail
HERE=$(cd "$(dirname "$0")" && pwd)
ssh vps 'mkdir -p ~/site'
scp -q "$HERE/compose.yml" "$HERE/setup.sh" vps:site/
ssh vps 'bash ~/site/setup.sh'
