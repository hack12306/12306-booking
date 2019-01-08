# encoding: utf8

import os
import json
import platform
import requests
from PIL import Image


def qr_terminal_draw(filepath):
    assert isinstance(filepath, (str))

    if not os.path.exists(filepath):
        raise Exception('file not exists. %s' % filepath)

    if platform.system() == "Windows":
        white_block = '▇'
        black_block = '  '
        new_line = '\n'
    else:
        white_block = '\033[1;37;47m  '
        black_block = '\033[1;37;40m  '
        new_line = '\033[0m\n'

    output = ''
    im = Image.open(filepath)
    im = im.resize((21, 21))

    pixels = im.load()

    output += white_block * (im.width + 2) + new_line
    for h in range(im.height):
        output += white_block
        for w in range(im.width):
            pixel = pixels[w,h]     # NOQA
            if pixel[0] == 0:
                output += black_block
            elif pixel[0] == 255:
                output += white_block
            else:
                assert 'Unsupported pixel. %s' % pixel

        else:
            output += white_block + new_line
    output += white_block * (im.width + 2) + new_line

    return output


def get_public_ip():
    resp = requests.get('https://httpbin.org/ip')
    if resp.status_code != 200:
        raise Exception('Network error')
    return json.loads(resp.content)['origin'].encode('utf8')
