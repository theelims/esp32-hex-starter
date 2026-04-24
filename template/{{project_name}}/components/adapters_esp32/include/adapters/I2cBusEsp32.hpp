#pragma once
#include "ports/II2cBus.hpp"

namespace adapters {

// Stub — fill in on first real need. Pattern: construct with a bus id
// and clock-speed from board::, configure driver/i2c_master, translate
// esp_err_t → ports::I2cError.
class I2cBusEsp32 : public ports::II2cBus {
public:
    core::Result<void, ports::I2cError> write(uint8_t addr,
                                              const uint8_t* data,
                                              size_t len) override;
    core::Result<void, ports::I2cError> read(uint8_t addr,
                                             uint8_t* buf,
                                             size_t len) override;
    core::Result<void, ports::I2cError> write_read(uint8_t addr,
                                                   const uint8_t* wr, size_t wl,
                                                   uint8_t* rd, size_t rl) override;
};

}  // namespace adapters
