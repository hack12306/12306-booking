# encoding: utf8

"""
_logging.py
@author Meng.yangyang
@description 
@created Thu Jan 10 2019 10:14:02 GMT+0800 (CST)
"""

import logging

__all__ = ('LogLevelFilter',)


class LogLevelFilter(logging.Filter):
    def __init__(self, log_level_no=logging.INFO):
        self._log_level_no = log_level_no

    def filter(self, record):
        if record.levelno == self._log_level_no:
            return 1
        else:
            return 0
