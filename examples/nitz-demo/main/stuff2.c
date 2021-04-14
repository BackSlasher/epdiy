#include <stdio.h>
#include <string.h>
#include <string.h>
#include "epd_driver.h"
#include "esp_heap_caps.h"
#include "esp_log.h"

#include "http.h"
#include "wifi.h"

/*
 * TODO remove
unsigned char * base64_encode(const unsigned char *src, size_t len,
                              size_t *out_len);
unsigned char * base64_decode(const unsigned char *src, size_t len,
                              size_t *out_len);
*/

uint8_t *framebuffer;
void epd_setup() {
  epd_init();
  framebuffer = (uint8_t *)heap_caps_malloc(EPD_WIDTH * EPD_HEIGHT / 2, MALLOC_CAP_SPIRAM);
  epd_clear();
}

void draw() {
  epd_poweron();
  epd_draw_grayscale_image(epd_full_screen(), framebuffer);
  epd_poweroff();
}

void clear() {
  memset(framebuffer, 0xFF, EPD_WIDTH * EPD_HEIGHT / 2);
  epd_poweron();
  epd_clear();
  epd_poweroff();

}

#define WRITE_HEADER(req, buffer, name, format, src) sprintf(buffer, format, src); ESP_ERROR_CHECK(httpd_resp_set_hdr(req, name, buffer));
esp_err_t http_info(httpd_req_t *req) {
  char width[20], height[20], temperature[20];
  WRITE_HEADER(req, width, "width", "%d", EPD_WIDTH);
  WRITE_HEADER(req, height, "height", "%d", EPD_HEIGHT);
  WRITE_HEADER(req, temperature, "temperature", "%.1f", epd_ambient_temperature());
  const char resp[] = "hello. Check headers!\n";
  httpd_resp_send(req, resp, HTTPD_RESP_USE_STRLEN);
  return ESP_OK;
}

esp_err_t http_clear(httpd_req_t *req) {
  const char resp[] = "done!\n";
  clear();
  httpd_resp_send(req, resp, HTTPD_RESP_USE_STRLEN);
  return ESP_OK;
}

#define READ_HEADER(req, buffer, buffer_len, name, format, dest) ESP_ERROR_CHECK(httpd_req_get_hdr_value_str(req, name, buffer, buffer_len)); sscanf(buffer, format, dest);

esp_err_t http_draw_area(httpd_req_t *req) {
  char header[20];
  memset(header, 0, 20); 
  int x, y, width, height;
  READ_HEADER(req, header, 20, "x", "%d", &x);
  READ_HEADER(req, header, 20, "y", "%d", &y);
  READ_HEADER(req, header, 20, "height", "%d", &height);
  READ_HEADER(req, header, 20, "width", "%d", &width);
  int should_clear = httpd_req_get_hdr_value_str(req, "width", header, 0) != ESP_ERR_NOT_FOUND ? 1: 0;
  // Data is binary
  int req_size = req->content_len;
  char *content = (char*)heap_caps_malloc(req_size, MALLOC_CAP_SPIRAM);
  if (content == NULL) {
    char msg[50];
    sprintf(msg, "Failed to allocate %d chars\n", req_size);
    httpd_resp_send_err(req, HTTPD_500_INTERNAL_SERVER_ERROR, msg);
    return ESP_ERR_INVALID_ARG;
  }
  int current_pos = 0;
  int amount_recieved;
  while ((amount_recieved = httpd_req_recv(req, (content+current_pos), req_size)) > 0) {
    current_pos += amount_recieved;
  }
  if (amount_recieved < 0) {
    char msg[50];
    free(content);
    sprintf(msg, "Failed to read byets. Return %d\n", amount_recieved);
    httpd_resp_send_err(req, HTTPD_500_INTERNAL_SERVER_ERROR, msg);
    return ESP_ERR_INVALID_ARG;
  }
  if (should_clear) {
    clear();
  }
  Rect_t area = {
    .x = x,
    .y = y,
    .width = width,
    .height = height,
  };
  epd_copy_to_framebuffer(area, (uint8_t *)content, framebuffer);
  draw();
  free(content);
  char resp[50];
  sprintf(resp, "%d bytes done!\n", amount_recieved);
  httpd_resp_send(req, resp, HTTPD_RESP_USE_STRLEN);
  return ESP_OK;
}


void setup_http() {
  httpd_handle_t http = start_webserver();

  if (http == NULL) {
    ESP_LOGE(__FUNCTION__, "HTTP server ded\n");
    return;
  }

  httpd_uri_t handler = {
    .uri = "/info",
    .method = HTTP_GET,
    .handler = http_info,
    .user_ctx = NULL,
  };
  httpd_register_uri_handler(http, &handler);

  httpd_uri_t handler2 = {
    .uri = "/draw_area",
    .method = HTTP_POST,
    .handler = http_draw_area,
    .user_ctx = NULL,
  };
  httpd_register_uri_handler(http, &handler2);

  httpd_uri_t handler3 = {
    .uri = "/clear",
    .method = HTTP_GET,
    .handler = http_clear,
    .user_ctx = NULL,
  };
  httpd_register_uri_handler(http, &handler3);

  // More we can do:
  // epd_clear_area, clears specific area
  // partial update?
  // Write text (write_string)
}

void setup() {
  epd_setup();
  wifi_init();
  setup_http();

  ESP_LOGI(__FUNCTION__, "yay!\n");
}

void stuff2_main() {
  setup();
}
