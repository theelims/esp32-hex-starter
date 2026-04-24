#!/usr/bin/env bash
# Reject ISRs that call ESP_LOGx, malloc, new, or std::string operations.
# ISR handlers are declared with IRAM_ATTR. We extract each IRAM_ATTR function
# body (naive: brace-matched) and grep for forbidden calls.
set -euo pipefail

# Run awk across every staged .cpp/.c/.hpp/.h file. awk tracks brace depth after
# an IRAM_ATTR token and yells when it sees a forbidden symbol inside the body.
violations=0
while IFS= read -r f; do
    awk '
        /IRAM_ATTR/ { in_isr = 1; depth = 0 }
        in_isr && /{/ { depth += gsub(/\{/, "{") }
        in_isr && /\}/ {
            depth -= gsub(/\}/, "}")
            if (depth <= 0) in_isr = 0
        }
        in_isr && /ESP_LOG[EWIDV]\(|\bmalloc\(|\bcalloc\(|\bfree\(|\bnew\b|std::string|std::vector/ {
            printf "%s:%d: %s\n", FILENAME, NR, $0
            exit_code = 1
        }
        END { exit exit_code }
    ' exit_code=0 "$f" || violations=$((violations + 1))
done < <(git diff --cached --name-only --diff-filter=AM | grep -E '\.(cpp|c|hpp|h)$' || true)

if [ "$violations" -gt 0 ]; then
    cat <<'EOF'

❌ ISR hygiene violation. Inside an IRAM_ATTR function:
  • No ESP_LOGx — use ESP_EARLY_LOGx or queue a message.
  • No malloc / calloc / free / new / delete.
  • No std::string, std::vector, std::map (allocating STL).
  • Only touch shared state through FreeRTOS primitives (queues, semaphores).

If you really need one of these in an ISR (very rare), annotate the line with
`// isr-ok: <reason>` and document the safety argument.
EOF
    exit 1
fi
exit 0
