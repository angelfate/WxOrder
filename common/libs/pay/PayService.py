# -*- coding: utf-8 -*-
import hashlib, time, random, decimal, json
from application import app, db
from common.models.food.Food import Food
from common.models.food.FoodSaleChangeLog import FoodSaleChangeLog
from common.models.pay.PayOrder import PayOrder
from common.models.pay.PayOrderItem import PayOrderItem
from common.models.pay.PayOrderCallbackData import PayOrderCallbackDatum
from common.libs.Helper import getCurrentData
# from common.libs.queue.QueueService import QueueService
from common.libs.food.FoodService import FoodService


class PayService():

    def __init__(self):
        pass

    def createOrder(self, member_id, items=None, params=None):  # 创建订单（哪个用户，商品列表，params额外字段[留言] ）
        """
        实现下单并发，库存减少
        :param member_id:
        :param items:
        :param params:
        :return:
        """
        resp = {'code': 200, 'msg': '操作成功~', 'data': {}}
        pay_price = decimal.Decimal(0.00)   # 商品总价格
        continue_cnt = 0
        food_ids = []
        for item in items:  # 遍历所有下单的商品
            if decimal.Decimal(item['price']) < 0:  # 如果有的商品价格<0。那么统计次数，并且跳过
                continue_cnt += 1
                continue

            pay_price = pay_price + decimal.Decimal(item['price']) * int(item['number'])  # 此时的，商品总价格。就是，初始价格0.00 + 上面跳过的商品价格 * 下单数量
            food_ids.append(item['id'])  # 在这里面添加，通过的商品的 id

        if continue_cnt >= len(items):  # 如果跳过的次数 >= 下单商品的数量。说明没有选择商品
            resp['code'] = -1
            resp['msg'] = '商品items为空~~'
            return resp

        yun_price = params['yun_price'] if params and 'yun_price' in params else 0
        note = params['note'] if params and 'note' in params else ''
        express_address_id = params['express_address_id'] if params and 'express_address_id' in params else 0
        express_info = params['express_info'] if params and 'express_info' in params else {}
        yun_price = decimal.Decimal(yun_price)
        total_price = pay_price + yun_price

        # 并发处理 乐观锁和悲观锁。这里采用的是观锁。（悲观锁：锁数据表行记录。乐观锁：数据表增加一个字段，每次更新时对它进行判断 ）
        try:
            # 为了防止并发库存出问题了，我们坐下selectfor update, 这里可以给大家演示下
            tmp_food_list = db.session.query(Food).filter(Food.id.in_(food_ids)) \
                .with_for_update().all()  # 锁定所有本次下单的商品id，行记录

            tmp_food_stock_mapping = {}  # 临时的商品库存 map，方便对比
            for tmp_item in tmp_food_list:
                tmp_food_stock_mapping[tmp_item.id] = tmp_item.stock  # 被锁定的商品 库存

            model_pay_order = PayOrder()
            model_pay_order.order_sn = self.geneOrderSn()  # 随机订单号，通过随机算法算出
            model_pay_order.member_id = member_id
            model_pay_order.total_price = total_price
            model_pay_order.yun_price = yun_price
            model_pay_order.pay_price = pay_price
            model_pay_order.note = note  # 备注信息
            model_pay_order.status = -8  # 默认状态：-8待付款
            model_pay_order.express_status = -8  # 待支付
            model_pay_order.express_address_id = express_address_id
            model_pay_order.express_info = json.dumps(express_info)
            model_pay_order.updated_time = model_pay_order.created_time = getCurrentData()
            db.session.add(model_pay_order)
            db.session.flush()

            for item in items:  # 第一次判断，剩下的商品（跳出的商品）
                tmp_left_stock = tmp_food_stock_mapping[item['id']]

                if decimal.Decimal(item['price']) < 0:  # 如果是价格<=0，就停止本次操作，继续
                    continue

                if int(item['number']) > int(tmp_left_stock):  # 如果下单的商品数量 > 库存
                    raise Exception("您购买的这美食太火爆了，剩余：%s,您购买%s~~" % (tmp_left_stock, item['number']))

                tmp_ret = Food.query.filter_by(id=item['id']).update({
                    "stock": int(tmp_left_stock) - int(item['number'])
                })  # 更新库存
                if not tmp_ret:
                    raise Exception("下单失败请重新下单")

                tmp_pay_item = PayOrderItem()  # 生成订单
                tmp_pay_item.pay_order_id = model_pay_order.id
                tmp_pay_item.member_id = member_id
                tmp_pay_item.quantity = item['number']  # 下单数量
                tmp_pay_item.price = item['price']  # 商品单价
                tmp_pay_item.food_id = item['id']  # 商品id
                tmp_pay_item.note = note   # 备注信息
                tmp_pay_item.updated_time = tmp_pay_item.created_time = getCurrentData()
                db.session.add(tmp_pay_item)
                db.session.flush()

                FoodService.setStockChangeLog(item['id'], -item['number'], "在线购买")  # 商品变更记录。商品id，-数量，备注
            db.session.commit()  # 直到完成本次提交，行锁才解开
            resp['data'] = {  # 下单成功，返回数据
                'id': model_pay_order.id,
                'order_sn': model_pay_order.order_sn,
                'total_price': str(total_price)
            }
        except Exception as e:
            pass
            db.session.rollback()  # 如果出现异常，数据回滚，回到操作前的状态
            print("*"*50,e)
            resp['code'] = -1
            resp['msg'] = "下单失败请重新下单"
            resp['msg'] = str(e)
            return resp
        return resp

    # def closeOrder(self, pay_order_id=0):
    #     if pay_order_id < 1:
    #         return False
    #     pay_order_info = PayOrder.query.filter_by(id=pay_order_id, status=-8).first()
    #     if not pay_order_info:
    #         return False
    #
    #     pay_order_items = PayOrderItem.query.filter_by(pay_order_id=pay_order_id).all()
    #     if pay_order_items:
    #         # 需要归还库存
    #         for item in pay_order_items:
    #             tmp_food_info = Food.query.filter_by(id=item.food_id).first()
    #             if tmp_food_info:
    #                 tmp_food_info.stock = tmp_food_info.stock + item.quantity
    #                 tmp_food_info.updated_time = getCurrentData()
    #                 db.session.add(tmp_food_info)
    #                 db.session.commit()
    #                 FoodService.setStockChangeLog(item.food_id, item.quantity, "订单取消")
    #
    #     pay_order_info.status = 0
    #     pay_order_info.updated_time = getCurrentData()
    #     db.session.add(pay_order_info)
    #     db.session.commit()
    #     return True
    #
    # def orderSuccess(self, pay_order_id=0, params=None):
    #     try:
    #         pay_order_info = PayOrder.query.filter_by(id=pay_order_id).first()
    #         if not pay_order_info or pay_order_info.status not in [-8, -7]:
    #             return True
    #
    #         pay_order_info.pay_sn = params['pay_sn'] if params and 'pay_sn' in params else ''
    #         pay_order_info.status = 1
    #         pay_order_info.express_status = -7
    #         pay_order_info.updated_time = getCurrentData()
    #         db.session.add(pay_order_info)
    #
    #         pay_order_items = PayOrderItem.query.filter_by(pay_order_id=pay_order_id).all()
    #         for order_item in pay_order_items:
    #             tmp_model_sale_log = FoodSaleChangeLog()
    #             tmp_model_sale_log.food_id = order_item.food_id
    #             tmp_model_sale_log.quantity = order_item.quantity
    #             tmp_model_sale_log.price = order_item.price
    #             tmp_model_sale_log.member_id = order_item.member_id
    #             tmp_model_sale_log.created_time = getCurrentData()
    #             db.session.add(tmp_model_sale_log)
    #
    #         db.session.commit()
    #     except Exception as e:
    #         db.session.rollback()
    #         print(e)
    #         return False
    #
    #     # 加入通知队列，做消息提醒和
    #     QueueService.addQueue("pay", {
    #         "member_id": pay_order_info.member_id,
    #         "pay_order_id": pay_order_info.id
    #     })
    #     return True
    #
    # def addPayCallbackData(self, pay_order_id=0, type='pay', data=''):
    #     model_callback = PayOrderCallbackData()
    #     model_callback.pay_order_id = pay_order_id
    #     if type == "pay":
    #         model_callback.pay_data = data
    #         model_callback.refund_data = ''
    #     else:
    #         model_callback.refund_data = data
    #         model_callback.pay_data = ''
    #
    #     model_callback.created_time = model_callback.updated_time = getCurrentData()
    #     db.session.add(model_callback)
    #     db.session.commit()
    #     return True
    #
    def geneOrderSn(self):  # 随机订单号（随机产生 md5）
        m = hashlib.md5()
        sn = None
        while True:  # 为什么while true？因为生成的sn是唯一的，所以先到数据库查查存不存在
            str = "%s-%s" % (int(round(time.time() * 1000)), random.randint(0, 9999999))  # 当前时间戳为标准
            m.update(str.encode("utf-8"))  # 生成 md5
            sn = m.hexdigest()  #订单号
            if not PayOrder.query.filter_by(order_sn=sn).first():  # 如果 这个订单号不存在，就跳过这个死循环。否则继续生成新的md5订单号
                break
        return sn  # 返回订单号
