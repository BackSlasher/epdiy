set(app_sources wifi.c http.c stuff2.c stuff.c "main.c")

idf_component_register(SRCS ${app_sources} REQUIRES epd_driver esp_http_server nvs_flash)
