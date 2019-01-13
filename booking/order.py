# encoding: utf8
"""
order.py
@author Meng.yangyang
@description 下单
@created Tue Jan 08 2019 17:56:17 GMT+0800 (CST)
"""

import re
import json
import copy
import time
import logging

from hack12306 import constants
from hack12306.order import TrainOrderAPI
from hack12306.query import TrainInfoQueryAPI
from hack12306.user import TrainUserAPI
from hack12306.utils import (tomorrow, JSONEncoder,
                             gen_old_passenge_tuple, gen_passenger_ticket_tuple)

from . import settings
from . import exceptions

_logger = logging.getLogger('booking')

__all__ = ('order_check_no_complete', 'order_submit', 'order_no_complete')


def order_no_complete():
    """
    订单-未支付订单
    """
    orders = TrainOrderAPI().order_query_no_complete(cookies=settings.COOKIES)
    _logger.debug('order no complete orders. %s' % json.dumps(orders, ensure_ascii=False))
    if not orders:
        return None
    return orders[0]['sequence_no']


def order_check_no_complete():
    """
    订单-检查是有未支付订单
    :return True:有支付订单 False:没有未支付订单
    """
    if order_no_complete():
        return True
    else:
        return False


def order_submit(passenger_id_nos, **train_info):
    """
    订单-提交订单
    :param passenger_id_nos 乘客身份证列表
    :param **train_info 乘车信息
    :return order_no 订单号
    """

    assert isinstance(
        passenger_id_nos, (list, tuple)), 'Invalid passenger_id_nos param. %s' % json.dumps(
        passenger_id_nos, ensure_ascii=False)
    assert passenger_id_nos, 'Invalid passenger_id_nos param. %s' % json.dumps(passenger_id_nos, ensure_ascii=False)

    train_order_api = TrainOrderAPI()

    # 1. 下单-提交订单
    submit_order_result = train_order_api.order_submit_order(
        train_info['secret'],
        train_info['train_date'],
        cookies=settings.COOKIES)
    _logger.debug('order submit order result. %s' % submit_order_result)

    # 2. 下单-确认乘客
    confirm_passenger_result = train_order_api.order_confirm_passenger(cookies=settings.COOKIES)
    _logger.debug('order confirm passenger result. %s' % json.dumps(
        confirm_passenger_result, ensure_ascii=False, cls=JSONEncoder))

    # 3. 下单-检查订单信息
    passengers = TrainUserAPI().user_passengers(cookies=settings.COOKIES)
    select_passengers = []
    for passenger in passengers:
        if passenger['passenger_id_no'] in passenger_id_nos:
            select_passengers.append(copy.deepcopy(passenger))

    assert select_passengers, '乘客不存在. %s' % json.dumps(passenger_id_nos, ensure_ascii=False)

    passenger_ticket_list = []
    old_passenger_list = []
    for passenger_info in select_passengers:
        passenger_ticket_list.append(gen_passenger_ticket_tuple(
            train_info['seat_type_code'],
            passenger_info['passenger_flag'],
            passenger_info['passenger_type'],
            passenger_info['passenger_name'],
            passenger_info['passenger_id_type_code'],
            passenger_info['passenger_id_no'],
            passenger_info['mobile_no']))
        old_passenger_list.append(
            gen_old_passenge_tuple(
                passenger_info['passenger_name'],
                passenger_info['passenger_id_type_code'],
                passenger_info['passenger_id_no'],
                passenger_info['passenger_type']))

    passenger_ticket_str = '_'.join([','.join(p) for p in passenger_ticket_list])
    old_passenger_str = ''.join([','.join(p) for p in old_passenger_list])

    check_order_result = train_order_api.order_confirm_passenger_check_order(
        confirm_passenger_result['token'],
        passenger_ticket_str, old_passenger_str, cookies=settings.COOKIES)
    _logger.debug('order check order result. %s' % json.dumps(check_order_result, ensure_ascii=False, cls=JSONEncoder))
    if not check_order_result['submitStatus']:
        raise exceptions.BookingSubmitOrderError(check_order_result.get('errMsg', u'提交订单失败').encode('utf8'))

    # 4. 下单-获取排队数量
    queue_count_result = train_order_api.order_confirm_passenger_get_queue_count(
        train_info['train_date'],
        train_info['train_num'],
        train_info['seat_type_code'],
        train_info['from_station'],
        train_info['to_station'],
        confirm_passenger_result['ticket_info']['leftTicketStr'],
        confirm_passenger_result['token'],
        confirm_passenger_result['order_request_params']['station_train_code'],
        confirm_passenger_result['ticket_info']['queryLeftTicketRequestDTO']['purpose_codes'],
        confirm_passenger_result['ticket_info']['train_location'],
        cookies=settings.COOKIES,
    )
    _logger.debug('order confirm passenger get queue count result. %s' % json.dumps(
        queue_count_result, ensure_ascii=False, cls=JSONEncoder))

    # 5. 下单-确认车票
    confirm_ticket_result = train_order_api.order_confirm_passenger_confirm_single_for_queue(
        passenger_ticket_str, old_passenger_str,
        confirm_passenger_result['ticket_info']['queryLeftTicketRequestDTO']['purpose_codes'],
        confirm_passenger_result['ticket_info']['key_check_isChange'],
        confirm_passenger_result['ticket_info']['leftTicketStr'],
        confirm_passenger_result['ticket_info']['train_location'],
        confirm_passenger_result['token'], cookies=settings.COOKIES)
    _logger.debug('order confirm passenger confirm ticket result. %s' % json.dumps(
        confirm_ticket_result, ensure_ascii=False, cls=JSONEncoder))

    # 6. 下单-查询订单
    try_times = 4
    while try_times > 0:
        query_order_result = train_order_api.order_confirm_passenger_query_order(
            confirm_passenger_result['token'], cookies=settings.COOKIES)
        _logger.debug('order confirm passenger query order result. %s' % json.dumps(
            query_order_result, ensure_ascii=False, cls=JSONEncoder))

        if query_order_result['orderId']:
            # order submit successfully
            break
        else:
            # 今日订单取消次数超限，无法继续订票
            error_code = query_order_result.get('errorcode')
            error_msg = query_order_result.get('msg', '').encode('utf8')
            order_cancel_exceed_limit_pattern = re.compile(r'取消次数过多')

            if error_code == '0' and order_cancel_exceed_limit_pattern.search(error_msg):
               raise exceptions.BookingOrderCancelExceedLimit(query_order_result['msg'].encode('utf8'))

        time.sleep(0.5)
        try_times -= 1
    else:
        raise exceptions.BookingOrderQueryTimeOut()


    # 7. 下单-订单结果查询
    order_result = train_order_api.order_confirm_passenger_result_order(
        query_order_result['orderId'], confirm_passenger_result['token'], cookies=settings.COOKIES)
    _logger.debug('order result. %s' % json.dumps(order_result, ensure_ascii=False))

    _logger.info(
        '恭喜你！抢票成功。订单号：%s 车次：%s 座位席别：%s 乘车日期：%s 出发站：%s 到达站：%s 历时:%s' %
        (query_order_result['orderId'],
         train_info['train_name'],
         train_info['seat_type'],
         train_info['train_date'],
         train_info['from_station'],
         train_info['to_station'],
         train_info['duration']))

    return query_order_result['orderId']
