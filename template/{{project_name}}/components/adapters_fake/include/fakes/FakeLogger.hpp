#pragma once
#include <string>
#include <string_view>
#include <vector>

#include "ports/ILogger.hpp"

namespace fakes {

struct LogEntry {
    ports::LogLevel level;
    std::string tag;
    std::string msg;
};

class FakeLogger : public ports::ILogger {
public:
    void log(ports::LogLevel level, std::string_view tag, std::string_view msg) override {
        entries_.push_back({level, std::string(tag), std::string(msg)});
    }
    const std::vector<LogEntry>& entries() const { return entries_; }
    void clear() { entries_.clear(); }

private:
    std::vector<LogEntry> entries_;
};

}  // namespace fakes
