# encoding: utf8
"""
query.py
@author Meng.yangyang
@description 信息查询
@created Mon Jan 07 2019 16:50:59 GMT+0800 (CST)
@last-modified Tue Jan 08 2019 20:59:23 GMT+0800 (CST)
"""

import re
from hack12306.query import TrainInfoQueryAPI
from hack12306.constants import SEAT_TYPE_CODE_MAP


def query_left_tickets(train_date, from_station, to_station, seat_types, trains=None):
    """
    信息查询-剩余车票
    :param train_date
    :param from_station
    :param to_station
    :param seat_types
    :param trains
    :return JSON 对象
    """
    date_pattern = re.compile(r'^\d{4}-\d{2}-\d{2}$')
    assert date_pattern.match(train_date), 'Invalid train_date param. %s' % train_date

    assert isinstance(seat_types, list), 'Invalid seat_types param. %s' % seat_types
    assert frozenset(seat_types) <= frozenset(dict(SEAT_TYPE_CODE_MAP).keys()
                                              ), 'Invalid seat_types param. %s' % seat_types

    result = TrainInfoQueryAPI().info_query_left_tickets(train_date, from_station, to_station)

    # TODO seat_type_code => result
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
