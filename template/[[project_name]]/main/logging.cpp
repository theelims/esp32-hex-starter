#include "logging.hpp"

#include "esp_log.h"

void configure_logging() {
    esp_log_level_set("*",    ESP_LOG_INFO);   // global default
    // per-tag overrides — add one line per component as needed:
    // esp_log_level_set("imu",  ESP_LOG_DEBUG);
    // esp_log_level_set("wifi", ESP_LOG_WARN);
}
