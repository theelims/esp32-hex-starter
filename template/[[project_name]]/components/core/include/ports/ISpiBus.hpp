#pragma once
#include <cstddef>
#include <cstdint>

#include "core/Result.hpp"

namespace ports {

enum class SpiError { Timeout, Bus, Unknown };

struct ISpiBus {
    virtual ~ISpiBus() = default;

    /// Full-duplex transfer. `rx` may be nullptr to discard incoming bytes.
    virtual core::Result<void, SpiError> transfer(uint8_t cs_pin,
                                                  const uint8_t* tx,
                                                  uint8_t* rx,
                                                  size_t len) = 0;
};

}  // namespace ports
