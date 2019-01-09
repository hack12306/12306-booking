# encoding: utf8

import os

INIT_DONE = False

COOKIES = {}
PAY_FILEPATH = '{date}-{order_no}-{bank_id}.html'
STATION_CODE_MAP = {}


LOGGING = {
    'version': 1,
    'formatters': {
        'default': {
            'format': '%(asctime)s|%(levelname)s|%(module)s|%(funcName)s|%(lineno)d|%(message)s'
        },
    },
    'handlers': {
        'console': {
            'class': 'logging.StreamHandler',
            'formatter': 'default',
        },
    },
    'loggers': {
        'booking': {
            'handlers': ['console'],
            'level': os.getenv('BOOKING_LOG_LEVEL', 'INFO'),
        }
    },
}