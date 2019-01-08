# encoding: utf8
"""
auth.py
@author Meng.yangyang
@description 认证
@created Mon Jan 07 2019 16:35:01 GMT+0800 (CST)
@last-modified Tue Jan 08 2019 20:58:52 GMT+0800 (CST)
"""


import os
import time
import uuid
import json
import base64
import logging
from PIL import Image

from hack12306.auth import TrainAuthAPI
from hack12306.user import TrainUserAPI

_logger = logging.getLogger('booking')


def auth_is_login(cookies=None):
    """
    检查用户是否登录
    :param cookies JSON对象
    :return True已登录, False未登录
    """
    return TrainAuthAPI().auth_check_login(cookies=cookies)


def auth_qr():
    """
    认证-二维码登录
    """
    try:
        train_auth_api = TrainAuthAPI()

        _logger.debug('1. auth init')
        cookie_dict = train_auth_api.auth_init()

        _logger.debug('2. auth get qr')
        result = train_auth_api.auth_qr_get(cookies=cookie_dict)
        assert isinstance(result, dict)
        qr_uuid = result['uuid']
        qr_img_path = '/tmp/12306/booking/login-qr-%s.jpeg' % uuid.uuid1().hex

        if not os.path.exists(os.path.dirname(qr_img_path)):
            os.makedirs(os.path.dirname(qr_img_path))

        with open(qr_img_path, 'wb') as f:
            f.write(base64.b64decode(result['image']))

        im = Image.open(qr_img_path)
        im.show()

        _logger.debug('3. auth check qr')
        for _ in range(6):
            _logger.info('请扫描二维码登录！')
            qr_check_result = train_auth_api.auth_qr_check(qr_uuid, cookies=cookie_dict)
            _logger.debug('check qr result. %s' % json.dumps(qr_check_result, ensure_ascii=False))
            if qr_check_result['result_code'] == "2":
                _logger.debug('qr check success result. %s' % json.dumps(qr_check_result, ensure_ascii=False))
                _logger.info('二维码扫描成功！')
                break

            time.sleep(3)
        else:
            _logger.error('scan qr login error and exit.')
            _logger.error('二维码扫描失败，请重新运行程序！')
            os._exists(-1)

        uamtk_result = train_auth_api.auth_uamtk(qr_check_result['uamtk'], cookies=cookie_dict)
        _logger.debug('4. auth uamtk result. %s' % json.dumps(uamtk_result, ensure_ascii=False))

        uamauth_result = train_auth_api.auth_uamauth(uamtk_result['newapptk'], cookies=cookie_dict)
        _logger.debug('5. auth uamauth result. %s' % json.dumps(uamauth_result, ensure_ascii=False))

        cookies = {
            'tk': uamauth_result['apptk']
        }
        cookies.update(**cookie_dict)
        user_info_result = TrainUserAPI().user_info(cookies=cookies)
        _logger.debug('%s login successfully.' % user_info_result['name'])
        _logger.debug('cookies. %s' % json.dumps(cookies, ensure_ascii=False,))
        _logger.info('%s 登录成功。' % user_info_result['name'])

        return cookies
    finally:
        if os.path.exists(qr_img_path):
            os.remove(qr_img_path)
