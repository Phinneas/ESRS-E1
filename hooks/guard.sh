#!/bin/sh
# pre_tool_use guard for the orchestrator role. Fails closed.
# gitagent treats a crashed or non-zero hook as "allow", so this wrapper
# always exits 0 and prints a block unless guard.mjs returns a decision.
here=$(cd "$(dirname "$0")" && pwd)
root=$(cd "$here/.." && pwd)
out=$(node "$root/scripts/guard/guard.mjs" orchestrator "$root" 2>/dev/null) || out=""
case "$out" in
  *'"action"'*) printf '%s\n' "$out" ;;
  *) printf '%s\n' '{"action":"block","reason":"[orchestrator guard] guard did not run, failing closed"}' ;;
esac
exit 0
