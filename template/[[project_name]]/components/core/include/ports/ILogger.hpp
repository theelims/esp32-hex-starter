#pragma once
#include <source_location>
#include <string_view>

namespace ports {

enum class LogLevel { Trace, Debug, Info, Warn, Error };

struct ILogger {
    virtual ~ILogger() = default;
    virtual void log(LogLevel level, std::string_view tag, std::string_view msg,
                     std::source_location loc = std::source_location::current()) = 0;
};

}  // namespace ports
