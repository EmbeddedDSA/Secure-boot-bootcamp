#!/usr/bin/env bash
# Build and run every lab, and diff its output against expected-output.txt.
# A lab containing a file named PENDING is reported but not run: it has not
# been completed yet. CI fails if any completed lab's output differs.
set -uo pipefail
cd "$(dirname "$0")/.."

pass=0; failed=0; pending=0
for dir in labs/lab-*/; do
  lab=$(basename "$dir")
  if [[ -f "$dir/PENDING" ]]; then
    echo "PENDING  $lab"; pending=$((pending+1)); continue
  fi
  if [[ -x "$dir/run.sh" ]]; then cmd=(./run.sh)
  elif [[ -f "$dir/Makefile" ]]; then cmd=(make -s run)
  else echo "FAIL     $lab: no run.sh or Makefile"; failed=$((failed+1)); continue
  fi
  actual=$(cd "$dir" && "${cmd[@]}" 2>&1)
  if diff -u "$dir/expected-output.txt" <(printf '%s\n' "$actual") > /tmp/lab-diff.$$; then
    echo "PASS     $lab"; pass=$((pass+1))
  else
    echo "FAIL     $lab"; cat /tmp/lab-diff.$$; failed=$((failed+1))
  fi
  rm -f /tmp/lab-diff.$$
done
echo "passed=$pass failed=$failed pending=$pending"
[[ $failed -eq 0 ]]
