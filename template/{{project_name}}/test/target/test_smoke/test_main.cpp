#include <unity.h>

#include "esp_system.h"

void test_chip_is_alive(void) {
    TEST_ASSERT_EQUAL(CHIP_ESP32S3, esp_get_chip_model());
}

extern "C" void app_main(void) {
    UNITY_BEGIN();
    RUN_TEST(test_chip_is_alive);
    UNITY_END();
}
