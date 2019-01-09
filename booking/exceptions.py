# encoding: utf8
"""
exceptions.py
@author Meng.yangyang
@description 异常
@created Mon Jan 07 2019 17:48:48 GMT+0800 (CST)
@last-modified Wed Jan 09 2019 16:25:29 GMT+0800 (CST)
"""


class BookingBaseException(Exception):
    """
    订票异常
    """


class BookingOrderNoExists(BookingBaseException):
    """
    订单不存在
    """


class BookingTrainNoLeftTicket(BookingBaseException):
    """
    无票
    """
