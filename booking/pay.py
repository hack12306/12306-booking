# encoding: utf8
"""
pay.py
@author Meng.yangyang
@description 支付
@created Mon Jan 07 2019 17:33:55 GMT+0800 (CST)
"""

import os
import json
import copy
import logging
import datetime
import platform

from hack12306 import constants
from hack12306.pay import TrainPayAPI
from hack12306.utils import tomorrow, JSONEncoder

from . import settings
from . import exceptions
from .order import order_no_complete
from .utils import get_public_ip

_logger = logging.getLogger('booking')

__all__ = ('pay_order', )


def pay_order(bank_id=constants.BANK_ID_WX, **kwargs):
    """
    支付订单
    :param sequence_no 订单后
    :bank_id 支付渠道ID
    :return None
    """
    train_pay_api = TrainPayAPI()

    # 0.查询未支付订单
    sequence_no = order_no_complete()
    if not sequence_no:
        raise exceptions.BookingOrderNoExists('')

    # 1.支付未完成订单
    pay_no_complete_order_result = train_pay_api.pay_no_complete_order(sequence_no, cookies=settings.COOKIES)
    _logger.debug('pay no complete order result. %s' % json.dumps(pay_no_complete_order_result, ensure_ascii=False,))
    if pay_no_complete_order_result['existError'] != 'N':
        raise exceptions.BookingOrderNoExists('%s订单不存在' % sequence_no)

    # 2.支付初始化
    train_pay_api.pay_init(cookies=settings.COOKIES)

    # 3.发起支付
    pay_check_new_result = train_pay_api.pay_check_new(cookies=settings.COOKIES)
    _logger.debug('pay check new result. %s' % json.dumps(pay_check_new_result, ensure_ascii=False))

    # 4.交易
    pay_business_result = train_pay_api.pay_web_business(
        pay_check_new_result['payForm']['tranData'],
        pay_check_new_result['payForm']['merSignMsg'],
        pay_check_new_result['payForm']['transType'],
        get_public_ip(), pay_check_new_result['payForm']['tranDataParsed']['order_timeout_date'],
        bank_id, cookies=settings.COOKIES)
    _logger.debug('pay business result. %s' % json.dumps(pay_business_result, ensure_ascii=False))

    # 5.跳转第三方支付
    pay_business_third_pay_resp = train_pay_api.submit(
        pay_business_result['url'],
        pay_business_result['params'],
        method=pay_business_result['method'],
        parse_resp=False,
        cookies=settings.COOKIES,
        allow_redirects=True)
    _logger.debug('pay third resp status code. %s' % pay_business_third_pay_resp.status_code)
    _logger.debug('pay third resp. %s' % pay_business_third_pay_resp.content)

    # 6.打开浏览器扫码完成支付
    try:
        pay_filepath = settings.PAY_FILEPATH.format(date=datetime.date.today().strftime('%Y%m%d'),
                                                    order_no=sequence_no, bank_id=bank_id)
        if not os.path.exists(os.path.dirname(pay_filepath)):
            os.makedirs(os.path.dirname(pay_filepath))

        with open(pay_filepath, 'w') as f:
            f.write(pay_business_third_pay_resp.content)

        _logger.info('请用浏览器打开%s，完成支付！' % pay_filepath)
    finally:
        if os.path.exists(pay_filepath):
            if platform.mac_ver()[0]:
                os.system('open %s' % pay_filepath)

            os.remove(pay_filepath)
