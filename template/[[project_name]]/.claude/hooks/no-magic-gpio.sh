#!/usr/bin/env bash
# Reject raw GPIO integer literals in source code. Every pin reference
# must go through board:: constants from the generated Pins.hpp .
set -euo pipefail

# Match patterns like:
#   gpio_set_level(21, ...)   ← bare int
#   .pin = 8                  ← struct init with bare int
#   GPIO_NUM_21               ← IDF macro (use board::X_PIN instead)
# Allow:
#   board::FOO_PIN
#   GPIO_NUM_NC  (explicit "not connected")
PATTERN='(gpio_num_t\)[[:space:]]*[0-9]+|GPIO_NUM_([0-9]+)|\.pin[[:space:]]*=[[:space:]]*[0-9]+|gpio_(set_level|set_direction|config|pulldown|pullup|isr_handler_add)[[:space:]]*\([[:space:]]*[0-9]+'

violations=0
while IFS= read -r f; do
    case "$f" in
        components/board/include/board/Pins.hpp) continue ;;
    esac
    # Filter out exempted lines (commented with `// gpio-ok: <reason>`) before
    # matching. Prints file:line:content for the non-exempt hits.
    if grep -nE "$PATTERN" "$f" 2>/dev/null | grep -v 'gpio-ok:' | grep .; then
        echo "  ↑ in $f"
        violations=$((violations + 1))
    fi
done < <(git diff --cached --name-only --diff-filter=AM \
         | grep -E '\.(cpp|hpp|c|h)$')

if [ "$violations" -gt 0 ]; then
    cat <<EOF
❌ Raw GPIO numbers found. Use board:: constants from Pins.hpp.

    #include "board/Pins.hpp"
    gpio_set_level(static_cast<gpio_num_t>(board::STATUS_LED_PIN), 1);

If you really must use a literal (very rare — prefer extending board.yaml),
add  // gpio-ok: <reason>  on the same line.
EOF
    exit 1
fi
exit 0
