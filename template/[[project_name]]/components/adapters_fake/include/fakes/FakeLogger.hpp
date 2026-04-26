#pragma once
#include <chrono>
#include <cstring>
#include <fstream>
#include <iostream>
#include <source_location>
#include <string>
#include <string_view>
#include <vector>

#include "ports/ILogger.hpp"

namespace fakes {

struct LogEntry {
    ports::LogLevel      level;
    std::string          tag;
    std::string          msg;
    std::source_location loc;
    uint32_t             ms;
};

class FakeLogger : public ports::ILogger {
public:
    void log(ports::LogLevel level, std::string_view tag, std::string_view msg,
             std::source_location loc = std::source_location::current()) override {
        uint32_t ms = elapsed_ms();
        entries_.push_back({level, std::string(tag), std::string(msg), loc, ms});

        const char* file = loc.file_name();
        const char* slash = strrchr(file, '/');
        file = slash ? slash + 1 : file;

        std::string line = std::string(1, level_char(level))
            + " (" + pad4(ms) + ") "
            + std::string(tag) + ": "
            + std::string(msg)
            + "  [" + file + ":" + std::to_string(loc.line()) + "]\n";

        std::cerr << line;
        log_file() << line;
        log_file().flush();
    }

    const std::vector<LogEntry>& entries() const { return entries_; }
    void clear() { entries_.clear(); }

private:
    using Clock = std::chrono::steady_clock;
    Clock::time_point start_{Clock::now()};
    std::vector<LogEntry> entries_;

    uint32_t elapsed_ms() const {
        return static_cast<uint32_t>(
            std::chrono::duration_cast<std::chrono::milliseconds>(
                Clock::now() - start_).count());
    }

    static char level_char(ports::LogLevel l) {
        switch (l) {
            case ports::LogLevel::Trace: return 'V';
            case ports::LogLevel::Debug: return 'D';
            case ports::LogLevel::Info:  return 'I';
            case ports::LogLevel::Warn:  return 'W';
            case ports::LogLevel::Error: return 'E';
        }
        return 'E';
    }

    static std::string pad4(uint32_t ms) {
        std::string s = std::to_string(ms);
        while (s.size() < 4) s = " " + s;
        return s;
    }

    // One log file per process run, opened lazily on first use.
    // Filename: native_test_<epoch_ms>.log in the working directory.
    static std::ofstream& log_file() {
        static std::ofstream file = [] {
            auto epoch_ms = std::chrono::duration_cast<std::chrono::milliseconds>(
                std::chrono::system_clock::now().time_since_epoch()).count();
            return std::ofstream{"native_test_" + std::to_string(epoch_ms) + ".log"};
        }();
        return file;
    }
};

}  // namespace fakes
