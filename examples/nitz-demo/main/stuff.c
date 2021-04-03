#include <stdio.h>
#include <string.h>
#include "epd_driver.h"
#include "esp_heap_caps.h"
#include "esp_log.h"

#define true 1

const int frame_size = EPD_WIDTH * EPD_HEIGHT / 2;
uint8_t *framebuffer;

char mygetc() {
  return fgetc(stdin);
}

void draw_commit() {
  epd_poweron();
  epd_draw_grayscale_image(epd_full_screen(), framebuffer);
  epd_poweroff();
}

void cmd_draw() {
  memset(framebuffer, 0xFF, frame_size); // Color white
  int current_location = 0;
  while (true) {
    if (current_location >= frame_size) {
      ESP_LOGW(__FUNCTION__, "Drawing size exceeded, discarding drawing\n");
      return;
    }
    char c = mygetc();
    if(c == '\n') return draw_commit();
    if (c >= 'A' && c <= 'P') {
      int val = c - 'A';
      framebuffer[current_location++] = val;
    } else {
      ESP_LOGW(__FUNCTION__, "Invalid char, ASCII code %d, discarding drawing\n", c);
      return;
    }
  }
}

void parse_command(char* cmd) {
  if (!strcmp(cmd, "draw")) {
    cmd_draw();
  } else {
    ESP_LOGW(__FUNCTION__, "Unknown command \"%s\", ignoring\n", cmd);
  }
}

// Max command length: 20
void read_command() {
  char command[20] = {};
  int cmd_len = 0;
  while (true) {
    if(cmd_len >= 20){
      ESP_LOGW(__FUNCTION__, "Command too long, discarding\n");
      return;
    }
    char c = mygetc();
    if (c == '\n') return;
    else if (c == ',') return parse_command(command);
    else command[cmd_len++] = c;
  }
}

void loop() {
  framebuffer = (uint8_t *)heap_caps_malloc(frame_size, MALLOC_CAP_SPIRAM);
  while (true) {
    read_command();
  }
}
