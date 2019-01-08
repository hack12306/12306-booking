"""
exceptions.py
@author Meng.yangyang
@description 异常
@created Mon Jan 07 2019 17:48:48 GMT+0800 (CST)
@last-modified Tue Jan 08 2019 18:12:36 GMT+0800 (CST)
"""

# encoding: utf8

class BookingBaseException(Exception):
    """
    订票异常
    """


class BookingOrderNoExists(BookingBaseException):
    """
    订单不存在
    """
