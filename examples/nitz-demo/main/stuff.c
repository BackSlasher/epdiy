#include <stdio.h>
#include <string.h>
#include "epd_driver.h"
#include "esp_heap_caps.h"
#include "esp_log.h"

#include "giraffe.h"

#define true 1

const int frame_size = EPD_WIDTH * EPD_HEIGHT / 2;
uint8_t *framebuffer;

void print_giraffe() {
  int pos = 0;
  int counter = 0;
  printf("This is a giraffe\n");
  while (pos++ < (340*768)/2) {
    uint8_t current = giraffe_data[pos];
    char high = current / 16 + 'A';
    char low = current % 16 + 'A';
    fputc(high, stdout);
    fputc(low, stdout);
    counter+=2;
  }
  fputc('\n', stdout);
  printf("done %d chars!\n", counter);
}

char mygetc() {
  return fgetc(stdin);
}

void draw_commit() {
  epd_poweron();
  epd_draw_grayscale_image(epd_full_screen(), framebuffer);
  epd_poweroff();
}

const char ESCAPE = '\n';

void cmd_draw() {
  memset(framebuffer, 0xFF, frame_size); // Color white
  int current_location = 0;
  while (true) {
    if (current_location >= frame_size) {
      ESP_LOGW(__FUNCTION__, "Drawing size exceeded, discarding drawing\n");
      return;
    }
    char c = mygetc();
    if(c == ESCAPE) {
      char c2 = mygetc();
      if (c2 == ESCAPE) {
        return draw_commit();
      } else if (c2 == 0) {
        framebuffer[current_location++] = ESCAPE;
      } else {
        ESP_LOGW(__FUNCTION__, "Invalid escaped char, code %d, discarding drawing\n", c2);
        return;
      }
    } else {
      framebuffer[current_location++] = c;
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
    if (c == ESCAPE) return;
    else if (c == ',') return parse_command(command);
    else command[cmd_len++] = c;
  }
}

void loop() {
  framebuffer = (uint8_t *)heap_caps_malloc(frame_size, MALLOC_CAP_SPIRAM);
  print_giraffe();
  // read_command();
}
