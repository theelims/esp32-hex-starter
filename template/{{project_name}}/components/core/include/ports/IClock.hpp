#pragma once
#include <cstdint>

namespace ports {

struct IClock {
    virtual ~IClock() = default;
    /// Monotonic milliseconds since some unspecified epoch.
    virtual uint64_t now_ms() const = 0;
    virtual void sleep_ms(uint32_t ms) = 0;
};

}  // namespace ports
