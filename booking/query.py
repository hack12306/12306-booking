# encoding: utf8
"""
query.py
@author Meng.yangyang
@description 信息查询
@created Mon Jan 07 2019 16:50:59 GMT+0800 (CST)
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

__all__ = ('query_left_tickets', 'query_station_code_map',)


def _check_seat_type_is_booking(left_ticket):
    if left_ticket and left_ticket != u'无' and left_ticket != u'*':
        return True
    else:
        return False


def _select_train_and_seat_type(train_names, seat_types, query_trains):
    """
    选择订票车次、席别
    :param train_names 预定的车次列表
    :param seat_types 预定席别列表
    :param query_trains 查询到火车车次列表
    :return select_train, select_seat_type
    """
    def _select_trains(query_trains, train_names=None):
        if train_names:
            select_trains = []
            # 根据订票车次次序，选择车次
            for train_name in train_names:
                for train in query_trains:
                    if train['train_name'] == train_name:
                        select_trains.append(copy.deepcopy(train))
            return select_trains
        else:
            return query_trains

    def _select_types(trains, seat_types):
        select_train = None
        select_seat_type = None

        for train in trains:
            for seat_type in seat_types:
                seat_type_left_ticket = train.get(seat_type, '')
                if _check_seat_type_is_booking(seat_type_left_ticket):
                    select_seat_type = seat_type
                    select_train = copy.deepcopy(train)
                    return select_train, select_seat_type
        else:
            return None, None

    _logger.debug('train_names:%s seat_types:%s' % (json.dumps(train_names, ensure_ascii=False),
                                                    json.dumps(seat_types, ensure_ascii=False)))
    trains = _select_trains(query_trains, train_names)
    # debug trains
    for i in range(min(len(trains), len(train_names or ['']))):
        _logger.debug('query left tickets train info. %s' % json.dumps(trains[i], ensure_ascii=False))

    return _select_types(trains, seat_types)


def query_left_tickets(train_date, from_station, to_station, seat_types, train_names=None):
    """
    信息查询-剩余车票
    :param train_date
    :param from_station
    :param to_station
    :param seat_types
    :param train_names
    :return JSON 对象
    """
    date_pattern = re.compile(r'^\d{4}-\d{2}-\d{2}$')
    assert date_pattern.match(train_date), 'Invalid train_date param. %s' % train_date

    assert isinstance(seat_types, list), u'Invalid seat_types param. %s' % seat_types
    assert frozenset(seat_types) <= frozenset(dict(SEAT_TYPE_CODE_MAP).keys()
                                              ), u'Invalid seat_types param. %s' % seat_types

    train_info = {}

    trains = TrainInfoQueryAPI().info_query_left_tickets(train_date, from_station, to_station)
    train_info, select_seat_type = _select_train_and_seat_type(train_names, seat_types, trains)

    if not train_info or not select_seat_type:
        raise exceptions.BookingTrainNoLeftTicket()

    _logger.debug('select train info. %s' % json.dumps(train_info, ensure_ascii=False))

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
