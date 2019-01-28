# encoding: utf8

"""
remind.py
@author Meng.yangyang
@description 提醒
@created Mon Jan 28 2019 09:49:14 GMT+0800 (CST)
"""

import os
from . import settings


def remind_left_ticket():
    """
    有票提醒
    """
    cmd = 'open %s' % settings.TRAIN_AUTIO_FILE
    os.system(cmd)
