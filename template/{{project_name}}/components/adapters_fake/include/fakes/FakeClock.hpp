#pragma once
#include <cstdint>

#include "ports/IClock.hpp"

namespace fakes {

class FakeClock : public ports::IClock {
public:
    uint64_t now_ms() const override { return now_; }
    void sleep_ms(uint32_t ms) override { now_ += ms; }

    void advance(uint64_t ms) { now_ += ms; }
    void set(uint64_t ms) { now_ = ms; }

private:
    mutable uint64_t now_{0};
};

}  // namespace fakes
