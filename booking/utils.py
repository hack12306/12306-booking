# encoding: utf8
"""
utils.py
@author Meng.yangyang
@description 工具函数
@created Mon Jan 07 2019 13:22:25 GMT+0800 (CST)
"""

import os
import json
import platform
import requests


# def qr_terminal_draw(filepath):
#     from PIL import Image
#     assert isinstance(filepath, (str))

#     if not os.path.exists(filepath):
#         raise Exception('file not exists. %s' % filepath)

#     if platform.system() == "Windows":
#         white_block = '▇'
#         black_block = '  '
#         new_line = '\n'
#     else:
#         white_block = '\033[1;37;47m  '
#         black_block = '\033[1;37;40m  '
#         new_line = '\033[0m\n'

#     output = ''
#     im = Image.open(filepath)
#     im = im.resize((21, 21))

#     pixels = im.load()

#     output += white_block * (im.width + 2) + new_line
#     for h in range(im.height):
#         output += white_block
#         for w in range(im.width):
#             pixel = pixels[w,h]     # NOQA
#             if pixel[0] == 0:
#                 output += black_block
#             elif pixel[0] == 255:
#                 output += white_block
#             else:
#                 assert 'Unsupported pixel. %s' % pixel

#         else:
#             output += white_block + new_line
#     output += white_block * (im.width + 2) + new_line

#     return output


def get_public_ip():
    resp = requests.get('http://httpbin.org/ip')
    if resp.status_code != 200:
        raise Exception('Network error')
    return json.loads(resp.content)['origin'].encode('utf8')


def check_seat_types(seat_types):
    from hack12306.constants import SEAT_TYPE_CODE_MAP

    assert isinstance(seat_types, (list, tuple))
    if not frozenset(seat_types) <= frozenset(dict(SEAT_TYPE_CODE_MAP).keys()):
        return False
    return True
