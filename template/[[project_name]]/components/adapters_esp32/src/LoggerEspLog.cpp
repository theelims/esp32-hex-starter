#include "adapters/LoggerEspLog.hpp"

#include <cinttypes>
#include <cstring>

#include "esp_log.h"

namespace adapters {

namespace {

esp_log_level_t to_esp_level(ports::LogLevel l) {
    switch (l) {
        case ports::LogLevel::Trace: return ESP_LOG_VERBOSE;
        case ports::LogLevel::Debug: return ESP_LOG_DEBUG;
        case ports::LogLevel::Info:  return ESP_LOG_INFO;
        case ports::LogLevel::Warn:  return ESP_LOG_WARN;
        case ports::LogLevel::Error: return ESP_LOG_ERROR;
    }
    return ESP_LOG_ERROR;
}

char level_char(ports::LogLevel l) {
    switch (l) {
        case ports::LogLevel::Trace: return 'V';
        case ports::LogLevel::Debug: return 'D';
        case ports::LogLevel::Info:  return 'I';
        case ports::LogLevel::Warn:  return 'W';
        case ports::LogLevel::Error: return 'E';
    }
    return 'E';
}

}  // namespace

void LoggerEspLog::log(ports::LogLevel level, std::string_view tag,
                       std::string_view msg, std::source_location loc) {
    const char* file = loc.file_name();
    const char* slash = strrchr(file, '/');
    file = slash ? slash + 1 : file;

    esp_log_write(to_esp_level(level), tag.data(),
        "%c (%4" PRIu32 ") %s: %.*s  [%s:%d]\n",
        level_char(level),
        esp_log_timestamp(),
        tag.data(),
        (int)msg.size(), msg.data(),
        file, (int)loc.line());
}

}  // namespace adapters
