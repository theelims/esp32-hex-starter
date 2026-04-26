idf_component_register(
    SRCS "main.cpp"
         "logging.cpp"
    INCLUDE_DIRS "."
    REQUIRES core adapters_esp32
)
