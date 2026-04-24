#pragma once
#include <cstdint>
#include <map>
#include <vector>

#include "ports/II2cBus.hpp"

namespace fakes {

// Simple register-bank fake. Scripted by set_register() per address.
class FakeI2cBus : public ports::II2cBus {
public:
    core::Result<void, ports::I2cError>
    write(uint8_t addr, const uint8_t* data, size_t len) override {
        writes_.push_back({addr, std::vector<uint8_t>(data, data + len)});
        if (len >= 1) last_reg_[addr] = data[0];
        if (len >= 2) regs_[addr][data[0]] = data[1];
        return core::Result<void, ports::I2cError>::Ok();
    }

    core::Result<void, ports::I2cError>
    read(uint8_t addr, uint8_t* buf, size_t len) override {
        for (size_t i = 0; i < len; ++i) {
            buf[i] = regs_[addr][last_reg_[addr] + i];
        }
        return core::Result<void, ports::I2cError>::Ok();
    }

    core::Result<void, ports::I2cError>
    write_read(uint8_t addr, const uint8_t* wr, size_t wl,
               uint8_t* rd, size_t rl) override {
        if (wl) last_reg_[addr] = wr[0];
        return read(addr, rd, rl);
    }

    void set_register(uint8_t addr, uint8_t reg, uint8_t value) {
        regs_[addr][reg] = value;
    }

    struct WriteRecord { uint8_t addr; std::vector<uint8_t> data; };
    const std::vector<WriteRecord>& writes() const { return writes_; }

private:
    std::map<uint8_t, std::map<uint8_t, uint8_t>> regs_;
    std::map<uint8_t, uint8_t> last_reg_;
    std::vector<WriteRecord> writes_;
};

}  // namespace fakes
