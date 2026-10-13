#!/usr/bin/env bash
# Point git at the versioned hooks in tools/hooks. Run once per clone.
set -euo pipefail
cd "$(git rev-parse --show-toplevel)"
git config core.hooksPath tools/hooks
chmod +x tools/hooks/* tools/*.sh
echo "hooks installed: $(git config core.hooksPath)"
