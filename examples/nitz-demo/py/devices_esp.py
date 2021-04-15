#!/usr/bin/env python3

import devices
import requests
import PIL.Image

def http_get_info(address):
    r = requests.get(f'http://{address}/info')
    headers = r.headers
    keys = ['width','height', 'temperature']
    return {k: headers[k] for k in keys}

def http_clear(address):
    requests.get(f'http://{address}/clear')

def http_draw(address, img_bytes, width, height):
    print("aaaa", width, height, len(img_bytes))
    headers = {
        'clear': '1',  # TODO make this a parameter
        'height': str(height),
        'width': str(width),
        'x': '0',
        'y': '0',
    }
    requests.post(f'http://{address}/draw_area', headers=headers, data=img_bytes)

def convert_8bit_to_4bit(bytestring):
    fourbit = []
    for i in range(0,len(bytestring),2):
        first_nibble = int(bytestring[i] / 17)
        second_nibble = int(bytestring[i+1] / 17)
        fourbit += [ first_nibble << 4 | second_nibble ]
    fourbit = bytes(fourbit)
    return fourbit

class ESPDevice(devices.Device):

    def __init__(self, physical_dimensions: devices.Rectangle, address: str):
        super().__init__(physical_dimensions, address)
        self.resolution = None

    def get_resolution(self) -> devices.Dimensions:
        if self.resolution is None:
            info = http_get_info(self.address)
            self.resolution = devices.Dimensions(
                width=int(info['width']),
                height=int(info['height']),
            )
        return self.resolution

    def draw(self, image: PIL.Image) -> None:
        resolution = self.get_resolution()
        # TODO change resolution
        image = image.convert('L')
        image = image.resize((resolution.width, resolution.height))
        img_bytes = image.tobytes()
        img_bytes = convert_8bit_to_4bit(img_bytes)
        http_draw(address=self.address, width=resolution.width, height=resolution.height, img_bytes=img_bytes)

    def clear(self) -> None:
        http_clear(self.address)
