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
    cmd = 'open %s --hide --background' % settings.TRAIN_AUDIO_FILE
    os.system(cmd)


def remind_login_qr():
    """
    登录提醒
    """
    cmd = 'open %s --hide --background' % settings.LOGIN_AUDIO_FILE
    os.system(cmd)