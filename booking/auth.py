# encoding: utf8
"""
auth.py
@author Meng.yangyang
@description 认证
@created Mon Jan 07 2019 16:35:01 GMT+0800 (CST)
"""


import os
import time
import uuid
import json
import base64
import logging

from hack12306.auth import TrainAuthAPI
from hack12306.user import TrainUserAPI
from hack12306.exceptions import TrainUserNotLogin

from . import settings

_logger = logging.getLogger('booking')

__all__ = ('auth_qr', 'auth_reauth', 'auth_is_login')


def _uamtk_set(uamtk):
    settings.AUTH_UAMTK = uamtk


def _uamtk_get():
    return settings.AUTH_UAMTK


def auth_is_login(cookies=None):
    """
    检查用户是否登录
    :param cookies JSON对象
    :return True已登录, False未登录
    """
    result = TrainAuthAPI().auth_check_login(cookies=cookies)
    if not result:
        _logger.debug('会话已过期，请重新登录!')
    return result


def auth_reauth(uamtk, cookie_dict):
    """
    重新认证
    :param aumtk
    :param cookie_dict
    :return JSON对象
    """
    assert uamtk is not None
    assert isinstance(cookie_dict, dict)

    train_auth_api = TrainAuthAPI()

    uamtk_result = train_auth_api.auth_uamtk(uamtk, cookies=cookie_dict)
    _logger.debug('4. auth uamtk result. %s' % json.dumps(uamtk_result, ensure_ascii=False))

    uamauth_result = train_auth_api.auth_uamauth(uamtk_result['newapptk'], cookies=cookie_dict)
    _logger.debug('5. auth uamauth result. %s' % json.dumps(uamauth_result, ensure_ascii=False))

    return uamauth_result


def auth_qr():
    """
    认证-二维码登录
    """
    try:
        qr_img_path = '/tmp/12306/booking/login-qr-%s.jpeg' % uuid.uuid1().hex

        train_auth_api = TrainAuthAPI()

        _logger.debug('1. auth init')
        cookie_dict = train_auth_api.auth_init()

        _logger.debug('2. auth get qr')
        result = train_auth_api.auth_qr_get(cookies=cookie_dict)
        assert isinstance(result, dict)
        qr_uuid = result['uuid']

        if not os.path.exists(os.path.dirname(qr_img_path)):
            os.makedirs(os.path.dirname(qr_img_path))

        with open(qr_img_path, 'wb') as f:
            f.write(base64.b64decode(result['image']))

        # open qr image with browser
        cmd = settings.CHROME_APP_OPEN_CMD.format(filepath=qr_img_path)
        os.system(cmd)

        _logger.debug('3. auth check qr')
        for _ in range(15):
            _logger.info('请扫描二维码登录！')
            qr_check_result = train_auth_api.auth_qr_check(qr_uuid, cookies=cookie_dict)
            _logger.debug('check qr result. %s' % json.dumps(qr_check_result, ensure_ascii=False))
            if qr_check_result['result_code'] == "2":
                _logger.debug('qr check success result. %s' % json.dumps(qr_check_result, ensure_ascii=False))
                _logger.info('二维码扫描成功！')
                break

            time.sleep(1)
        else:
            _logger.error('二维码扫描失败，重新生成二维码')
            raise TrainUserNotLogin('扫描述二维码失败')

        _uamtk_set(qr_check_result['uamtk'])
        uamauth_result = auth_reauth(_uamtk_get(), cookie_dict)
        _logger.info('%s 登录成功。' % uamauth_result['username'].encode('utf8'))

        cookies = {
            'tk': uamauth_result['apptk']
        }
        cookies.update(**cookie_dict)
        _logger.debug('cookies. %s' % json.dumps(cookies, ensure_ascii=False,))

        # user_info_result = TrainUserAPI().user_info(cookies=cookies)
        # _logger.debug('%s login successfully.' % user_info_result['name'])

        return cookies
    finally:
        if os.path.exists(qr_img_path):
            os.remove(qr_img_path)
