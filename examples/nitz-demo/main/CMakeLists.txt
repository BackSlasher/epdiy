set(app_sources stuff.c "main.c")

idf_component_register(SRCS ${app_sources} REQUIRES epd_driver)
