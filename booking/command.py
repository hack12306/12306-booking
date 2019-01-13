# encoding: utf8

"""
command.py
@author Meng.yangyang
@description 
@created Tue Jan 08 2019 23:39:26 GMT+0800 (CST)
"""

import re
import json
import click
import logging
import datetime

from .run import initialize, run as booking_run_loop
from .utils import check_seat_types
from .query import query_station_code_map
from hack12306.constants import BANK_ID_WX, BANK_ID_ALIPAY

_logger = logging.getLogger('booking')


@click.command()
@click.option('--train-date', required=True, help=u'乘车日期，格式：YYYY-mm-dd')
@click.option('--train-names', required=True, help=u'车次')
@click.option('--seat-types', required=True, help=u'座位席别， 例如：硬卧,硬座')
@click.option('--from-station', required=True, help=u'始发站')
@click.option('--to-station', required=True, help=u'到达站')
@click.option('--pay-channel', type=click.Choice(['微信', '支付宝']), default='微信', help=u'支付通道，微信，支付宝')
@click.option('--passengers', help='乘客，例如：任正非,王石')
def booking(train_date, train_names, seat_types, from_station, to_station, pay_channel, passengers):
    initialize()

    date_pattern = re.compile(r'^\d{4}-\d{2}-\d{2}$')
    assert date_pattern.match(train_date), '乘车日期无效. %s' % train_date

    today = datetime.date.today()
    train_date_time = datetime.datetime.strptime(train_date, '%Y-%m-%d').date()
    assert train_date_time >= today, u'无效的乘车日期，乘车日期必须大于今天. %s' % train_date

    train_names = train_names.split(',')

    assert check_seat_types(seat_types.split(',')), u'无效的座席. %s' % seat_types
    seat_types = seat_types.split(',')

    station_code_map = query_station_code_map()
    assert from_station in station_code_map.keys(), u'未找到车站. %s' % from_station
    assert to_station in station_code_map.keys(), u'未找到车站. %s' % to_station
    from_station = station_code_map[from_station]
    to_station = station_code_map[to_station]

    assert pay_channel in ('微信', '支付宝'), '不支持的支付通道. %s' % pay_channel
    if pay_channel == '微信':
        pay_channel = BANK_ID_WX
    elif pay_channel == '支付宝':
        pay_channel = BANK_ID_ALIPAY
    else:
        assert False

    if passengers:
        passengers = passengers.split(',')

    _logger.info(u'订票信息。乘车日期：%s 车次：%s 座席：%s 始发站:%s to_station:%s 支付通道：%s' %
                 (train_date, json.dumps(train_names, ensure_ascii=False),
                  json.dumps(seat_types, ensure_ascii=False),
                  from_station, to_station, pay_channel))

    booking_run_loop(train_date, train_names, seat_types, from_station, to_station, pay_channel, passengers=passengers)
