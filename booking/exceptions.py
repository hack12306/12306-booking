# encoding: utf8

class BookingBaseException(Exception):
    """
    订票异常
    """


class BookingOrderNoExists(BookingBaseException):
    """
    订单不存在
    """
