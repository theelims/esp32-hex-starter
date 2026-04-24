#pragma once
#include "ports/IClock.hpp"

namespace adapters {

class ClockEsp32 : public ports::IClock {
public:
    uint64_t now_ms() const override;
    void sleep_ms(uint32_t ms) override;
};

}  // namespace adapters
