# encoding: utf8

"""
command.py
@author Meng.yangyang
@description 
@created Tue Jan 08 2019 23:39:26 GMT+0800 (CST)
@last-modified Wed Jan 09 2019 00:17:48 GMT+0800 (CST)
"""

import re
import click
import logging
import datetime

from .run import run as booking_run_loop
from .utils import check_seat_types
from .query import query_station_code_map
from hack12306.constants import BANK_ID_WX, BANK_ID_ALIPAY

_logger = logging.getLogger('booking')


@click.command()
@click.argument('train_date', type=click.DateTime(formats='%Y-%m-%d'), help='乘车日期，格式：YYYY-mm-dd')
@click.argument('train_name', help='车次')
@click.argument('seat_types', help='座位席别')
@click.argument('from_station', help='始发站')
@click.argument('to_station', help='到达站')
@click.option('pay_channel', help='支付通道， 1：微信，2：支付宝')
def booking(train_date, train_name, seat_types, from_station, to_station, pay_channel):
    date_pattern = re.compile(r'^\d{4}-\d{2}-\d{2}$')
    assert date_pattern.match(train_date), '乘车日期无效. %s' % train_date

    today = datetime.date.today()
    train_date_time = datetime.datetime.strptime(train_date, '%Y-%m-%d')
    assert train_date_time < today, '无效的乘车日期，乘车日期必须大于今天. %s' % train_date

    assert check_seat_types(seat_types.split(',')), '无效的座席. %s' % seat_types
    seat_types = seat_types.split(',')

    station_code_map = query_station_code_map()
    assert from_station in station_code_map.keys(), '未找到车站. %s' % from_station
    assert to_station in station_code_map.keys(), '未找到车站. %s' % to_station
    from_station = station_code_map[from_station]
    to_station = station_code_map[to_station]

    assert pay_channel in ('1', '2'), '不支持的支付通道. %s' % pay_channel
    if pay_channel == '1':
        pay_channel = BANK_ID_WX
    elif pay_channel == '2':
        pay_channel = BANK_ID_ALIPAY
    else:
        assert False

    _logger.info('订票信息。乘车日期：%s 车次：%s 座席：%s 始发站:%s to_station:%s 支付通道：%s' %
                 (train_date, train_name, seat_types, from_station, to_station, pay_channel))

    booking_run_loop(train_date, train_date, seat_types, from_station, to_station, pay_channel)
