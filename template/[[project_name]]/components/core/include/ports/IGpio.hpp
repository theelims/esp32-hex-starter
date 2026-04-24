#pragma once
#include <cstdint>

namespace ports {

enum class GpioDirection { Input, Output };
enum class GpioPull { None, Up, Down };

struct IGpio {
    virtual ~IGpio() = default;

    virtual void configure(int pin, GpioDirection dir, GpioPull pull) = 0;
    virtual void set(int pin, bool level) = 0;
    virtual bool get(int pin) const = 0;
};

}  // namespace ports
