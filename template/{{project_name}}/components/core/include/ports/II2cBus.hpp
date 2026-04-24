#pragma once
#include <cstddef>
#include <cstdint>

#include "core/Result.hpp"

namespace ports {

enum class I2cError { Nack, Timeout, Arbitration, Bus, Unknown };

struct II2cBus {
    virtual ~II2cBus() = default;

    virtual core::Result<void, I2cError> write(uint8_t addr,
                                               const uint8_t* data,
                                               size_t len) = 0;
    virtual core::Result<void, I2cError> read(uint8_t addr,
                                              uint8_t* buf,
                                              size_t len) = 0;
    virtual core::Result<void, I2cError> write_read(uint8_t addr,
                                                    const uint8_t* wr, size_t wr_len,
                                                    uint8_t* rd, size_t rd_len) = 0;
};

}  // namespace ports
