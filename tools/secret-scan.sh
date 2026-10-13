#!/usr/bin/env bash
# Fail if any given file contains a private-key header, or lives under keys/.
# Used by the pre-commit hook (on staged content) and by CI (on the whole tree).
#
#   tools/secret-scan.sh --staged     scan what is about to be committed
#   tools/secret-scan.sh --tree       scan every tracked file
set -euo pipefail

# Split with [ ] so this script never matches itself.
PATTERN='-----BEGIN ([A-Z0-9]+ )*PRIVATE[ ]KEY-----|PuTTY-User-Key-[F]ile'

fail=0
case "${1:---staged}" in
  --staged)
    while IFS= read -r -d '' f; do
      if [[ "$f" == keys/* ]]; then
        echo "BLOCKED: $f is inside keys/, which must never be committed" >&2; fail=1; continue
      fi
      if git show ":$f" 2>/dev/null | grep -aEq -- "$PATTERN"; then
        echo "BLOCKED: $f contains a private-key header" >&2; fail=1
      fi
    done < <(git diff --cached --name-only --diff-filter=ACMR -z)
    ;;
  --tree)
    while IFS= read -r -d '' f; do
      if [[ "$f" == keys/* ]]; then
        echo "FOUND: $f is tracked inside keys/" >&2; fail=1; continue
      fi
      if grep -aEq -- "$PATTERN" "$f" 2>/dev/null; then
        echo "FOUND: $f contains a private-key header" >&2; fail=1
      fi
    done < <(git ls-files -z)
    ;;
  *) echo "usage: $0 [--staged|--tree]" >&2; exit 2 ;;
esac

if [[ $fail -ne 0 ]]; then
  echo "Private key material must stay in the gitignored keys/ directory. Regenerate it with tools/gen-keys.sh." >&2
  exit 1
fi
