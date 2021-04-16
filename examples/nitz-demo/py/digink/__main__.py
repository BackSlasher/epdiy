#!/usr/bin/env python3

# get command
# If draw, get file, parse it

import click
import PIL.Image
import devices_esp
import devices

all_devices = devices.DeviceCollection([
    devices_esp.ESPDevice(
        physical_dimensions = devices.Rectangle(
            start=devices.Point(
                x=20,
                y=14,
            ),
            dimensions=devices.Dimensions(
                width=20,
                height=14,
            ),
            rotation_deg=180,
        ),
        address="192.168.1.136",
    )
])

@click.group()
def cli():
    pass

@cli.command()
def clear():
    all_devices.clear()

# Draw a file on the entire screen
@cli.command()
@click.option('-f','--file', help="File to draw", required=True)
def draw(file):
    with PIL.Image.open(file) as f:
        img = f.copy()
    all_devices.draw(img)

if __name__ == '__main__':
    cli(obj={})
