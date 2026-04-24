#pragma once
#include <string_view>

namespace ports {

enum class LogLevel { Trace, Debug, Info, Warn, Error, Fatal };

struct ILogger {
    virtual ~ILogger() = default;

    /// Log a line. `tag` identifies the source module (component folder name).
    virtual void log(LogLevel level, std::string_view tag, std::string_view msg) = 0;
};

}  // namespace ports
