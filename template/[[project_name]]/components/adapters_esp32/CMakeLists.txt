idf_component_register(
    SRCS "src/ClockEsp32.cpp"
         "src/I2cBusEsp32.cpp"
         "src/LoggerEspLog.cpp"
    INCLUDE_DIRS "include"
    REQUIRES core driver esp_timer log
)
