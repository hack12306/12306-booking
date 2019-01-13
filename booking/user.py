# encoding: utf8
"""
user.py
@author Meng.yangyang
@description User
@created Wed Jan 09 2019 21:17:23 GMT+0800 (CST)
"""

import json
import logging
from hack12306.user import TrainUserAPI

from . import settings

__all__ = ('user_passengers',)

_logger = logging.getLogger('booking')


def user_passengers():
    """
    User passengers
    """
    passengers = TrainUserAPI().user_passengers(cookies=settings.COOKIES)
    _logger.debug(json.dumps(passengers, ensure_ascii=False))
    return passengers
