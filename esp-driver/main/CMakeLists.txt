set(srcs "sd_card_example_main.c")

idf_component_register(SRCS ${srcs}
                       INCLUDE_DIRS "." "../components/linger" "../components/spin_control"
                       REQUIRES fatfs sd_card esp_driver_i2s esp_driver_gpio linger spin_control 
                       WHOLE_ARCHIVE)
