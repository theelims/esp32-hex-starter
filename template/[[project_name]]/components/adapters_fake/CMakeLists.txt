# Header-only. Compiled into native GoogleTest builds only
# (the native env pulls it via build_src_filter in platformio.ini).
# Target builds ignore this component by simply not listing it in any
# on-target REQUIRES chain. Registering it as empty keeps ESP-IDF happy
# if it auto-discovers the folder.
idf_component_register(SRCS "" INCLUDE_DIRS "include")
