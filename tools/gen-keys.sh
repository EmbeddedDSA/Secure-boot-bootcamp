#!/usr/bin/env bash
# Regenerate every throwaway test key into the gitignored keys/ directory.
#
# You write the body of this script yourself in lab-00, once you can explain
# every openssl flag in it. Until then it refuses to run.
set -euo pipefail
cd "$(dirname "$0")/.."
mkdir -p keys
echo "gen-keys.sh: not written yet - this is part of lab-00-signing" >&2
exit 1
