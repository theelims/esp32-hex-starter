#include "adapters/I2cBusEsp32.hpp"

namespace adapters {

core::Result<void, ports::I2cError>
I2cBusEsp32::write(uint8_t /*addr*/, const uint8_t* /*data*/, size_t /*len*/) {
    // TODO: wire up driver/i2c_master_* and translate esp_err_t -> ports::I2cError.
    return core::Result<void, ports::I2cError>::Err(ports::I2cError::Unknown);
}

core::Result<void, ports::I2cError>
I2cBusEsp32::read(uint8_t /*addr*/, uint8_t* /*buf*/, size_t /*len*/) {
    return core::Result<void, ports::I2cError>::Err(ports::I2cError::Unknown);
}

core::Result<void, ports::I2cError>
I2cBusEsp32::write_read(uint8_t /*addr*/,
                        const uint8_t* /*wr*/, size_t /*wl*/,
                        uint8_t* /*rd*/, size_t /*rl*/) {
    return core::Result<void, ports::I2cError>::Err(ports::I2cError::Unknown);
}

}  // namespace adapters
