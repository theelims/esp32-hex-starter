#!/usr/bin/env bash
# Reject any xTaskCreate*/xTaskCreateStatic* call whose stack-size argument is
# a bare integer literal. Stacks MUST come from a named `<task>_STACK_BYTES`
# constexpr so budgets are reviewable and greppable.
set -euo pipefail

# Match the 3rd argument of xTaskCreate(pvTask, "name", <stack>, ...) — a bare integer.
PATTERN='xTaskCreate(Static|PinnedToCore)?\s*\([^,]+,[^,]+,\s*[0-9]+\b'

violations=0
while IFS= read -r f; do
    if grep -nE "$PATTERN" "$f" 2>/dev/null; then
        echo "  ↑ in $f — use a named *_STACK_BYTES constexpr, not a literal."
        violations=$((violations + 1))
    fi
done < <(git diff --cached --name-only --diff-filter=AM | grep -E '\.(cpp|c)$' || true)

if [ "$violations" -gt 0 ]; then
    cat <<'EOF'

❌ RTOS task stacks must be named constants so budgets are auditable.

    constexpr uint32_t kSamplerStackBytes = 4096;  // Why: 3 floats × N + logging frame
    xTaskCreate(sampler_task, "sampler", kSamplerStackBytes, nullptr, 5, nullptr);

Not:
    xTaskCreate(sampler_task, "sampler", 4096, nullptr, 5, nullptr);
EOF
    exit 1
fi
exit 0
