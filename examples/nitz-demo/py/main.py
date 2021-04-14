#!/usr/bin/env python3

# get command
# If draw, get file, parse it

import click
import requests
import PIL.Image
import PIL.ImageOps

@click.group()
# Should be a mac / IP but resolving seems hard. Keep it for later. For now it is IP
# https://stackoverflow.com/a/7629690 - is mac
@click.option('-d', '--device', required=True)
@click.pass_context
def cli(ctx, device):
    click.echo(f"Device is {device}")
    ctx.ensure_object(dict)
    ctx.obj['device'] = device

def get_info(device):
    r = requests.get(f'http://{device}/info')
    headers = r.headers
    keys = ['width','height', 'temperature']
    return {k: headers[k] for k in keys}

@cli.command()
@click.pass_context
def info(ctx):
    info = get_info(ctx.obj["device"])
    [
        click.echo(f"{k.capitalize()}: {v}") for k,v in info.items()
    ]

@cli.command()
@click.pass_context
def clear(ctx):
    r = requests.get(f'http://{ctx.obj["device"]}/clear')

def convert_8bit_to_4bit(bytestring):
    fourbit = []
    for i in range(0,len(bytestring),2):
        first_nibble = int(bytestring[i] / 17)
        second_nibble = int(bytestring[i+1] / 17)
        fourbit += [ first_nibble << 4 | second_nibble ]
    fourbit = bytes(fourbit)
    return fourbit


# Draw a file on the entire screen
@cli.command()
@click.pass_context
@click.option('-f','--file', help="File to draw", required=True)
def draw(ctx, file):
    device = ctx.obj["device"]
    # XXX skipping info
    """
    info = get_info(device)
    height = int(info["height"])
    width = int(info["width"])
    """
    height = 825
    width = 1200
    with PIL.Image.open(file) as f:
        img = f.copy()
    size = (width, height)
    img = PIL.ImageOps.fit(img, size)
    # img.thumbnail((width, height))
    img = img.convert('L')
    img.save('/tmp/bla.png')
    img_bytes = img.tobytes()
    img_bytes = convert_8bit_to_4bit(img_bytes)
    headers = {
        'clear': '1',
        'height': str(height),
        'width': str(width),
        'x': '0',
        'y': '0',
    }
    requests.post(f'http://{ctx.obj["device"]}/draw_area', headers=headers, data=img_bytes)

if __name__ == '__main__':
    cli(obj={})
