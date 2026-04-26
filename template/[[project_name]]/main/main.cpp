#include "adapters/ClockEsp32.hpp"
#include "adapters/LoggerEspLog.hpp"
#include "esp_app_desc.h"
#include "esp_log.h"
#include "logging.hpp"

static const char* TAG = "app";

// Composition root: wire real adapters to core.
extern "C" void app_main(void) {
    configure_logging();
    // esp_app_get_description()->project_name is populated by the build system
    // from the current folder name (CMake PROJECT() call).
    ESP_LOGI(TAG, "%s booted", esp_app_get_description()->project_name);

    adapters::LoggerEspLog logger;
    // Inject into core services as they land:
    // core::SomeService svc{logger};

    adapters::ClockEsp32 clock;
    (void)clock;  // replace with actual app wiring as features land
}
