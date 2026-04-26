#!/usr/bin/env bash
# Reject any commit that introduces ESP-IDF / Arduino includes into components/core/.
# This is the single most important architectural invariant.
set -euo pipefail

# Anchor on path segments so innocuous names (my_esp32_driver.h,
# esp32_hexagonal_starter.h) don't trip the hook. Match only real IDF / Arduino headers.
FORBIDDEN='^[[:space:]]*#include[[:space:]]*[<"](esp_[a-z0-9_]+\.h|driver/|freertos/|Arduino\.h|soc/|hal/|nvs\.h|nvs_flash\.h|esp32\.h|sdkconfig\.h)'

if git diff --cached --name-only | grep -E '^components/(core|adapters_fake)/.*\.(hpp|cpp|h|c)$' \
   | xargs -r grep -lE "$FORBIDDEN" 2>/dev/null; then
    echo "❌ core/ and adapters_fake/ must stay hardware-agnostic. Forbidden includes detected above."
    echo "   Move hardware-touching code to components/adapters_esp32/."
    exit 1
fi
exit 0
