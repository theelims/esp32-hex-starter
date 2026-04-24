#include "adapters/ClockEsp32.hpp"

#include "esp_timer.h"
#include "freertos/FreeRTOS.h"
#include "freertos/task.h"

namespace adapters {

uint64_t ClockEsp32::now_ms() const {
    return static_cast<uint64_t>(esp_timer_get_time() / 1000);
}

void ClockEsp32::sleep_ms(uint32_t ms) {
    vTaskDelay(pdMS_TO_TICKS(ms));
}

}  // namespace adapters
