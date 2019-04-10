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
import requests
import prettytable

from .run import initialize, run as booking_run_loop
from .utils import check_seat_types, time_to_str
from .query import query_station_code_map, query_code_station_map
from hack12306.constants import BANK_ID_WX, BANK_ID_ALIPAY
from hack12306.query import TrainInfoQueryAPI

_logger = logging.getLogger('booking')


@click.group()
def cli():
    pass


def do_booking(train_date, train_names, seat_types, from_station, to_station, pay_channel, passengers):
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

    assert pay_channel in (u'微信', u'支付宝'), u'不支持的支付通道. %s' % pay_channel
    if pay_channel == u'微信':
        pay_channel = BANK_ID_WX
    elif pay_channel == u'支付宝':
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


@cli.command('booking')
@click.option('--train-date', required=True, help=u'乘车日期，格式：YYYY-mm-dd')
@click.option('--train-names', required=True, help=u'车次')
@click.option('--seat-types', required=True, help=u'座位席别， 例如：硬卧,硬座')
@click.option('--from-station', required=True, help=u'始发站')
@click.option('--to-station', required=True, help=u'到达站')
@click.option('--pay-channel', type=click.Choice([u'微信', u'支付宝']), default=u'微信', help=u'支付通道，微信，支付宝')
@click.option('--passengers', help=u'乘客，例如：任正非,王石')
def booking_sub_cmd(train_date, train_names, seat_types, from_station, to_station, pay_channel, passengers):
    """
    定火车票
    """
    do_booking(train_date, train_names, seat_types, from_station, to_station, pay_channel, passengers)


@cli.command('qtrain')
@click.argument('train-code', metavar=u'<车次>')
def query_train(train_code):
    """
    查询车次
    """
    def _query_train_code(train_code):
        resp = requests.get('http://trip.kdreader.com/api/v1/train/%s/' % train_code)
        return json.loads(resp.content)

    def _query_train_schedule(train_code):
        resp = requests.get('http://trip.kdreader.com/api/v1/train/schedule/%s/' % train_code)
        return json.loads(resp.content)

    train_code = train_code.encode('utf8')
    # train_info = _query_train_code(train_code)
    train_schedule = _query_train_schedule(train_code)

    pt = prettytable.PrettyTable(
        field_names=['车次', '站次', '站名', '到达时间', '开车时间', '停车时间', '运行时间'],
        border=True,)

    for station in train_schedule:
        duration_time = time_to_str(station['duration_time'])
        pt.add_row([station['train_code'], station['station_no'], station['station_name'], station['arrive_time'][:5],
                    station['start_time'][:5], station['stopover_time'], duration_time])

    print '%s车次，%s从【%s】出发，运行%s, %s到达【%s】' % (
        train_code,
        train_schedule[0]['start_time'][:5].encode('utf8'),
        train_schedule[0]['station_name'].encode('utf8'),
        time_to_str(train_schedule[-1]['duration_time']),
        train_schedule[-1]['start_time'][:5].encode('utf8'),
        train_schedule[-1]['station_name'].encode('utf8'))

    print '途径车站列表：'
    print pt


@cli.command('qticket')
@click.option('--date', help=u'乘车日期，格式：YYYY-mm-dd')
@click.argument('from_station', metavar=u'<始发站>')
@click.argument('to_station', metavar=u'<终点站>')
def query_left_ticket(from_station, to_station, date):
    """
    查询余票
    """
    print '正在查询【%s】到【%s】的车票信息，请稍等...' % (from_station.encode('utf8'), to_station.encode('utf8'))

    station_code_map = query_station_code_map()
    if from_station not in station_code_map.keys():
        print '未找到【%s】车站' % from_station
        return

    from_station = station_code_map[from_station]
    if to_station not in station_code_map.keys():
        print u'未找到【%s】车站' % to_station
        return

    to_station = station_code_map[to_station]

    if date:
        date_pattern = re.compile(r'^\d{4}-\d{2}-\d{2}$')
        assert date_pattern.match(date), '乘车日期无效. %s' % date
    else:
        date = (datetime.date.today() + datetime.timedelta(days=1)).strftime('%Y-%m-%d')

    try_times = 3
    while try_times > 0:
        try:
            trains = TrainInfoQueryAPI().info_query_left_tickets(date, from_station, to_station)
            break
        except Exception as e:
            pass
        try_times -= 1
    else:
        print '网络请求失败，请重试...'
        return

    pt = prettytable.PrettyTable(
        field_names=['车次', '始发站', '目的站', '运行时间', '发车时间', '到达时间',
                     '商务座', '一等座', '二等座', '软卧', '硬卧', '软座', '硬座', '无座', '备注'],
        border=True)

    code_station_map = query_code_station_map()
    for train in trains:
        from_station = code_station_map[train['from_station']]
        to_station = code_station_map[train['to_station']]
        pt.add_row([train['train_name'], from_station, to_station,
                    train['duration'], train['departure_time'], train['arrival_time'],
                    train[u'商务座'] or '--', train[u'一等座'] or '--', train[u'二等座'] or '--',
                    train[u'软卧'] or '--', train[u'硬卧'] or '---', train[u'软座'] or '--',
                    train[u'硬座'] or '--', train[u'无座'] or '--', train[u'remark'] or '--'])

    print pt


@click.command('booking')
@click.option('--train-date', required=True, help=u'乘车日期，格式：YYYY-mm-dd')
@click.option('--train-names', required=True, help=u'车次')
@click.option('--seat-types', required=True, help=u'座位席别， 例如：硬卧,硬座')
@click.option('--from-station', required=True, help=u'始发站')
@click.option('--to-station', required=True, help=u'到达站')
@click.option('--pay-channel', type=click.Choice([u'微信', u'支付宝']), default=u'微信', help=u'支付通道，微信，支付宝')
@click.option('--passengers', help=u'乘客，例如：任正非,王石')
def booking(train_date, train_names, seat_types, from_station, to_station, pay_channel, passengers):
    """
    定火车票
    """
    do_booking(train_date, train_names, seat_types, from_station, to_station, pay_channel, passengers)
