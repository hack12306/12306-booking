"""
order.py
@author Meng.yangyang
@description 下单
@created Tue Jan 08 2019 17:56:17 GMT+0800 (CST)
@last-modified Tue Jan 08 2019 19:55:43 GMT+0800 (CST)
"""

# encoding: utf8

import json
import copy
import logging

from hack12306 import constants
from hack12306.order import TrainOrderAPI
from hack12306.query import TrainInfoQueryAPI
from hack12306.user import TrainUserAPI
from hack12306.utils import (tomorrow, JSONEncoder,
                             gen_old_passenge_tuple, gen_passenger_ticket_tuple)

from . import settings

_logger = logging.getLogger('booking')

confirm_submit_order = False


def order_submit(**train_info):
    """
    订单-提交订单
    """
    assert isinstance(train_info, dict), 'Invalid train_info param' % train_info

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
    passenger_info = passengers[0]
    passenger_ticket = gen_passenger_ticket_tuple(
        train_info['seat_type_code'],
        passenger_info['passenger_flag'],
        passenger_info['passenger_type'],
        passenger_info['passenger_name'],
        passenger_info['passenger_id_type_code'],
        passenger_info['passenger_id_no'],
        passenger_info['mobile_no'])
    old_passenger = gen_old_passenge_tuple(passenger_info['passenger_name'], passenger_info['passenger_id_type_code'],
                                           passenger_info['passenger_id_no'])
    check_order_result = train_order_api.order_confirm_passenger_check_order(
        confirm_passenger_result['token'],
        passenger_ticket, old_passenger, cookies=settings.COOKIES)
    _logger.debug('order check order result. %s' % json.dumps(check_order_result, ensure_ascii=False, cls=JSONEncoder))

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
        passenger_ticket, old_passenger,
        confirm_passenger_result['ticket_info']['queryLeftTicketRequestDTO']['purpose_codes'],
        confirm_passenger_result['ticket_info']['key_check_isChange'],
        confirm_passenger_result['ticket_info']['leftTicketStr'],
        confirm_passenger_result['ticket_info']['train_location'],
        confirm_passenger_result['token'], cookies=settings.COOKIES)
    _logger.debug('order confirm passenger confirm ticket result. %s' % json.dumps(
        confirm_ticket_result, ensure_ascii=False, cls=JSONEncoder))

    # 6. 下单-查询订单
    query_order_result = train_order_api.order_confirm_passenger_query_order(confirm_passenger_result['token'])
    _logger.debug('order confirm passenger query order result. %s' % json.dumps(
        query_order_result, ensure_ascii=False, cls=JSONEncoder))

    # 7. 下单-订单结果查询
    order_result = train_order_api.order_confirm_passenger_result_order(
        query_order_result['orderId'], confirm_passenger_result['token'])
    _logger.debug('order result. %s' % json.dumps(order_result, ensure_ascii=False))

    _logger.info('恭喜你！抢票成功。订单号：%s 车次：%s 座位席别：%s 乘车日期：%s 出发站：%s 到达站：%s 历时:%s')

    return query_order_result['orderId']
