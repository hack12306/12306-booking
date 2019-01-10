# encoding: utf8
"""
query.py
@author Meng.yangyang
@description 信息查询
@created Mon Jan 07 2019 16:50:59 GMT+0800 (CST)
@last-modified Thu Jan 10 2019 10:25:57 GMT+0800 (CST)
"""

import re
import copy
import json
import logging

from hack12306.constants import SEAT_TYPE_CODE_MAP
from hack12306.query import TrainInfoQueryAPI
from hack12306.constants import SEAT_TYPE_CODE_MAP

from . import exceptions

_logger = logging.getLogger('booking')


def query_left_tickets(train_date, from_station, to_station, seat_types, train_name=None):
    """
    信息查询-剩余车票
    :param train_date
    :param from_station
    :param to_station
    :param seat_types
    :param train_name
    :return JSON 对象
    """
    date_pattern = re.compile(r'^\d{4}-\d{2}-\d{2}$')
    assert date_pattern.match(train_date), 'Invalid train_date param. %s' % train_date

    assert isinstance(seat_types, list), u'Invalid seat_types param. %s' % seat_types
    assert frozenset(seat_types) <= frozenset(dict(SEAT_TYPE_CODE_MAP).keys()
                                              ), u'Invalid seat_types param. %s' % seat_types

    train_info = {}

    trains = TrainInfoQueryAPI().info_query_left_tickets(train_date, from_station, to_station)
    # _logger.debug('query left tickets. %s' % json.dumps(trains, ensure_ascii=False))
    if train_name:
        for train in trains:
            if train['train_name'] == train_name:
                train_info = copy.deepcopy(train)
                break
        else:
            raise exceptions.BookingTrainNoLeftTicket()
    else:
        # TODO Optimize multiple trains select type
        for train in trains:
            for seat_type in seat_types:
                if train.get(seat_type, ''):
                    train_info = copy.deepcopy(train)
                    break
        else:
            raise exceptions.BookingTrainNoLeftTicket()

    if not  train_info:
        raise exceptions.BookingTrainNoLeftTicket()

    _logger.debug('query left tickets train info. %s' % json.dumps(train_info, ensure_ascii=False))

    select_seat_type = None
    for seat_type in seat_types:
        seat_type_left_ticket = train_info.get(seat_type, '')
        if seat_type_left_ticket and seat_type_left_ticket != u'无':
            select_seat_type = seat_type
            break
    else:
        raise exceptions.BookingTrainNoLeftTicket()

    result = {
        'train_date': train_date,
        'from_station': train_info['from_station'],
        'to_station': train_info['to_station'],
        'seat_type': select_seat_type,
        'seat_type_code': dict(SEAT_TYPE_CODE_MAP)[select_seat_type],
        'departure_time': train_info['departure_time'],
        'arrival_time': train_info['arrival_time'],
        'secret': train_info['secret'],
        'train_name': train_info['train_name'],
        'duration': train_info['duration'],
        'train_num': train_info['train_num']
    }
    return result


def query_station_code_map():
    """
    信息查询-查询车站编码列表
    :return JSON对象
    """
    station_code_map = {}

    stations = TrainInfoQueryAPI().info_query_station_list()
    for station in stations:
        station_code_map[station['name']] = station['code']

    return station_code_map
