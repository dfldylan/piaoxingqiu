import time

import request
import config

'''
目前仅支持【无需选座】的项目
'''
show_id = config.show_id
want_buy_count = config.buy_count
audience_idx = config.audience_idx
deliver_method = config.deliver_method
acceptable_price = [2380, 1280]

# 准备阶段：获取观演人信息
while True:
    try:
        audiences = request.get_audiences()
        audience_ids = [audiences[i]["id"] for i in range(len(audiences))]
        print('audience_ids:', audience_ids)
        if len(audience_ids) != 0:
            break
        else:
            raise Exception('audience_ids is null')
    except Exception as e:
        print('获取观演人信息:', e)
        time.sleep(0.1)
        continue

# 准备阶段：获取默认收货地址
while True:
    try:
        address = request.get_address()
        address_id = address["addressId"]  # 地址id
        location_city_id = address["locationId"]  # 460102
        receiver = address["username"]  # 收件人
        cellphone = address["cellphone"]  # 电话
        detail_address = address["detailAddress"]  # 详细地址
        break
    except Exception as e:
        print('获取默认收货地址:', e)
        time.sleep(0.1)
        continue

time.sleep(0.1)

while True:
    # 第一阶段：session_id_list
    try:
        sessions = request.get_sessions(show_id)
        session_id_list = []
        if sessions:
            for i in sessions:
                if i["sessionStatus"] == 'ON_SALE':
                    session_id = i["bizShowSessionId"]
                    session_id_list.append(session_id)
        print('session_id_list: ', session_id_list)
        if len(session_id_list) == 0:
            raise Exception('session_id_list is null')
            # if session_id:
            #     break
            # else:
            #     print("未获取到在售状态且符合购票数量需求的session_id")
    except Exception as e:
        print(e)
        time.sleep(0.1)
        continue

    time.sleep(0.1)

    for session_id in session_id_list:
        print('session_id: ', session_id)
        # 第二阶段：seat_plan_id_list
        try:
            seat_plans = request.get_seat_plans(show_id, session_id)
            seat_plan_id_list = []
            for price in acceptable_price:
                for j in seat_plans:
                    if j["originalPrice"] == price:
                        seat_plan_id_list.append([j["seatPlanId"],j["originalPrice"]])
                        break
            print('seat_plan_id_list: ', seat_plan_id_list)
            if len(seat_plan_id_list) == 0:
                raise Exception('seat_plan_id_list is null')
        except Exception as e:
            print(e)
            time.sleep(0.1)
            continue

        time.sleep(0.1)

        # 第三阶段：order_list
        try:
            seat_count = request.get_seat_count(show_id, session_id)
            order_list = []
            for j in range(len(seat_plan_id_list)):
                [seat_plan_id,price] = seat_plan_id_list[j]
                for i in seat_count:
                    if i["seatPlanId"] == seat_plan_id:
                        print(f'seat_plan_id: {seat_plan_id}, price: {price}, remain: {i["canBuyCount"]}')
                        if i["canBuyCount"] >= want_buy_count:
                            order_list.append([seat_plan_id, price, want_buy_count])
                        elif i["canBuyCount"] > 0:
                            order_list.append([seat_plan_id, price, 1])
                        break
            print('order_list:', order_list)
            if len(order_list) == 0:
                raise Exception('order_list is null')
        except Exception as e:
            print(e)
            time.sleep(0.1)
            continue

        time.sleep(0.1)

        for order in order_list:
            [seat_plan_id, price, buy_count] = order
            while not deliver_method:
                try:
                    deliver_method = request.get_deliver_method(show_id, session_id, seat_plan_id, price, buy_count)
                    print("deliver_method:" + deliver_method)
                except:
                    print("get deliver_method failed")
                    time.sleep(0.1)
                    continue

            # 第四阶段：
            try:
                if deliver_method == "VENUE_E":
                    request.create_order(show_id, session_id, seat_plan_id, price, buy_count, deliver_method, 0, None,
                                         None, None, None, None, [])
                    exit(0)
                else:
                    if deliver_method == "EXPRESS":
                        # 获取快递费用
                        express_fee = request.get_express_fee(show_id, session_id, seat_plan_id, price, buy_count,
                                                              location_city_id)
                        print('express_fee:', express_fee)
                        # 下单
                        if not audience_idx:
                            audience_idx = audience_idx[:buy_count]
                            audience_ids = [audience_ids[i] for i in audience_idx]
                        else:
                            audience_ids = audience_ids[:buy_count]
                        request.create_order(show_id, session_id, seat_plan_id, price, buy_count, deliver_method,
                                             express_fee["priceItemVal"], receiver, cellphone, address_id,
                                             detail_address, location_city_id, audience_ids)
                        exit(0)
                    elif deliver_method == "VENUE" or deliver_method == "E_TICKET":
                        request.create_order(show_id, session_id, seat_plan_id, price, buy_count, deliver_method, 0,
                                             None, None, None, None, None, audience_ids)
                        exit(0)
                    else:
                        print("不支持的deliver_method:" + deliver_method)
                        exit(-1)
            except Exception as e:
                print(e)
                time.sleep(0.1)
                continue
