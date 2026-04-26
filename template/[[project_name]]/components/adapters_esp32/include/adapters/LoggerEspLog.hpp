#pragma once
#include <source_location>
#include <string_view>

#include "ports/ILogger.hpp"

namespace adapters {

// tag must be a null-terminated string literal; used by esp_log_write() for runtime
// level filtering via esp_log_level_set().
class LoggerEspLog : public ports::ILogger {
public:
    void log(ports::LogLevel level, std::string_view tag, std::string_view msg,
             std::source_location loc = std::source_location::current()) override;
};

}  // namespace adapters
