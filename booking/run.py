# encoding: utf8
"""
run.py
@author Meng.yangyang
@description Booking entry point
@created Tue Jan 08 2019 19:38:32 GMT+0800 (CST)
@last-modified Wed Jan 09 2019 12:22:46 GMT+0800 (CST)
"""

import os
import re
import time
import logging
import logging.config
from hack12306.constants import (BANK_ID_WX, BANK_ID_MAP, SEAT_TYPE_CODE_MAP,)
from hack12306.exceptions import TrainUserNotLogin, TrainBaseException

from . import settings
from .pay import pay_order
from .order import order_submit
from .auth import auth_qr, auth_is_login
from .query import query_left_tickets, query_station_code_map

_logger = logging.getLogger('booking')


BOOKING_STATUS_QUERY_LEFT_TICKET = 2
BOOKING_STATUS_ORDER_SUBMIT = 3
BOOKING_STATUS_PAY_ORDER = 4


def initialize():
    """
    Initialization.
    """
    if settings.INIT_DONE:
        return

    settings.STATION_CODE_MAP = query_station_code_map()
    logging.config.dictConfig(settings.LOGGING)
    settings.INIT_DONE = True


def run(train_date, train_name, seat_types, from_station, to_station, pay_channel=BANK_ID_WX, **kwargs):
    """
    Booking entry point.
    """
    initialize()
    assert settings.INIT_DONE is True, 'No Initialization'

    date_patten = re.compile(r'^\d{4}-\d{2}-\d{2}$')
    assert date_patten.match(train_date), 'Invalid train_date param. %s' % train_date

    assert isinstance(seat_types, (list, tuple)), u'Invalid seat_types param. %s' % seat_types
    assert frozenset(seat_types) <= frozenset(dict(SEAT_TYPE_CODE_MAP).keys()
                                              ), u'Invalid seat_types param. %s' % seat_types

    assert from_station in settings.STATION_CODE_MAP.values(), 'Invalid from_station param. %s' % from_station
    assert to_station in settings.STATION_CODE_MAP.values(), 'Invalid to_station param. %s' % to_station
    assert pay_channel in dict(BANK_ID_MAP).keys(), 'Invalid pay_channel param. %s' % pay_channel

    train_info = {}
    order_no = None
    booking_status = BOOKING_STATUS_QUERY_LEFT_TICKET

    while True:
        try:
            # auth
            if not settings.COOKIES or not auth_is_login(settings.COOKIES):
                cookies = auth_qr()
                settings.COOKIES = cookies

            # query left tickets
            if booking_status == BOOKING_STATUS_QUERY_LEFT_TICKET:
                train_info = query_left_tickets(train_date, from_station, to_station, seat_types, train_name)
                booking_status = BOOKING_STATUS_ORDER_SUBMIT

            # subit order
            elif booking_status == BOOKING_STATUS_ORDER_SUBMIT:
                order_no = order_submit(**train_info)
                booking_status = BOOKING_STATUS_PAY_ORDER

            # pay
            elif booking_status == BOOKING_STATUS_PAY_ORDER:
                pay_order(order_no, pay_channel)
                # pay success and exit
                return
            else:
                assert 'Unkown booking status. %s' % booking_status

            time.sleep(0.4)
        except TrainUserNotLogin:
            _logger.warn('用户未登录，请重新扫码登录')
            continue

        except TrainBaseException as e:
            _logger.error(e)
            _logger.exception(e)

        except Exception as e:
            _logger.exception(e)
            if isinstance(e, AssertionError):
                _logger.error('系统内部运行异常，请重新执行程序！')
                os._exit(-1)
