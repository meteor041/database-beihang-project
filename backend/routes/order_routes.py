from flask import Blueprint, request, jsonify
from datetime import datetime, timedelta
import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(__file__)))
from db import db_manager

order_bp = Blueprint('order', __name__)

@order_bp.route('/', methods=['POST'])
def create_order():
    """订单创建 - INSERT操作"""
    try:
        data = request.get_json()
        
        # 验证必填字段
        required_fields = ['buyer_id', 'item_id', 'payment_method', 'delivery_method']
        for field in required_fields:
            if not data.get(field):
                return jsonify({'error': f'{field} is required'}), 400

        buyer_id = data['buyer_id']
        item_id = data['item_id']
        delivery_method = data['delivery_method']
        address_id = data.get('address_id')  # 可选字段

        # 如果是快递配送，地址必填
        if delivery_method == 'express' and not address_id:
            return jsonify({'error': 'address_id is required for express delivery'}), 400
        
        # 获取商品信息
        item_sql = """
        SELECT user_id as seller_id, price, status, title
        FROM item 
        WHERE item_id = %s
        """
        item_result = db_manager.execute_query(item_sql, (item_id,))
        
        if not item_result:
            return jsonify({'error': 'Item not found'}), 404
        
        item = item_result[0]
        
        # 验证商品状态
        if item['status'] != 'available':
            return jsonify({'error': 'Item is not available'}), 400
        
        # 验证不能购买自己的商品
        if item['seller_id'] == buyer_id:
            return jsonify({'error': 'Cannot buy your own item'}), 400

        # 验证地址是否属于买家（仅当提供了地址时）
        if address_id:
            address_sql = "SELECT user_id FROM address WHERE address_id = %s"
            address_result = db_manager.execute_query(address_sql, (address_id,))

            if not address_result or address_result[0]['user_id'] != buyer_id:
                return jsonify({'error': 'Invalid address'}), 400
        
        # 生成订单号
        order_number = db_manager.generate_order_number()
        
        # 创建订单
        insert_sql = """
        INSERT INTO `order` (order_number, buyer_id, seller_id, item_id, address_id,
                           total_amount, payment_method, delivery_method, notes)
        VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s)
        """
        
        order_id = db_manager.execute_insert(insert_sql, (
            order_number,
            buyer_id,
            item['seller_id'],
            item_id,
            address_id,
            item['price'],
            data['payment_method'],
            data['delivery_method'],
            data.get('notes')
        ))
        
        # 更新商品状态为已售出
        update_item_sql = "UPDATE item SET status = 'sold' WHERE item_id = %s"
        db_manager.execute_update(update_item_sql, (item_id,))
        
        return jsonify({
            'message': 'Order created successfully',
            'order_id': order_id,
            'order_number': order_number
        }), 201
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@order_bp.route('/<int:order_id>', methods=['GET'])
def get_order(order_id):
    """订单查询 - SELECT操作"""
    try:
        sql = """
        SELECT o.*,
               i.title as item_title, i.images as item_images, i.location as item_location,
               buyer.username as buyer_name, buyer.phone as buyer_phone,
               seller.username as seller_name, seller.phone as seller_phone,
               a.recipient_name, a.phone as address_phone, a.province, a.city,
               a.district, a.detailed_address
        FROM `order` o
        JOIN item i ON o.item_id = i.item_id
        JOIN user buyer ON o.buyer_id = buyer.user_id
        JOIN user seller ON o.seller_id = seller.user_id
        LEFT JOIN address a ON o.address_id = a.address_id
        WHERE o.order_id = %s
        """
        
        orders = db_manager.execute_query(sql, (order_id,))
        
        if not orders:
            return jsonify({'error': 'Order not found'}), 404
        
        order = orders[0]
        
        # 处理图片JSON
        if order['item_images']:
            import json
            order['item_images'] = json.loads(order['item_images'])
        else:
            order['item_images'] = []
        
        return jsonify({'order': order}), 200
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@order_bp.route('/user/<int:user_id>', methods=['GET'])
def get_user_orders(user_id):
    """获取用户订单列表"""
    try:
        role = request.args.get('role', 'buyer')  # buyer or seller
        status = request.args.get('status')
        page = int(request.args.get('page', 1))
        limit = int(request.args.get('limit', 20))
        offset = (page - 1) * limit
        
        # 构建WHERE条件
        where_conditions = []
        params = []
        
        if role == 'buyer':
            where_conditions.append("o.buyer_id = %s")
        else:
            where_conditions.append("o.seller_id = %s")
        params.append(user_id)
        
        if status:
            where_conditions.append("o.order_status = %s")
            params.append(status)
        
        where_clause = " AND ".join(where_conditions)
        
        sql = f"""
        SELECT o.order_id, o.order_number, o.total_amount, o.payment_method,
               o.delivery_method, o.order_status, o.create_time,
               i.title as item_title, i.images as item_images,
               buyer.username as buyer_name,
               seller.username as seller_name
        FROM `order` o
        JOIN item i ON o.item_id = i.item_id
        JOIN user buyer ON o.buyer_id = buyer.user_id
        JOIN user seller ON o.seller_id = seller.user_id
        WHERE {where_clause}
        ORDER BY o.create_time DESC
        LIMIT %s OFFSET %s
        """
        
        params.extend([limit, offset])
        orders = db_manager.execute_query(sql, params)
        
        # 处理图片JSON
        for order in orders:
            if order['item_images']:
                import json
                order['item_images'] = json.loads(order['item_images'])
            else:
                order['item_images'] = []
        
        return jsonify({'orders': orders}), 200
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@order_bp.route('/<int:order_id>/status', methods=['PUT'])
def update_order_status(order_id):
    """订单状态更新 - UPDATE操作"""
    try:
        data = request.get_json()
        new_status = data.get('status')
        user_id = data.get('user_id')
        
        if not new_status or not user_id:
            return jsonify({'error': 'status and user_id are required'}), 400
        
        # 获取订单信息
        order_sql = """
        SELECT buyer_id, seller_id, order_status, payment_method
        FROM `order` 
        WHERE order_id = %s
        """
        order_result = db_manager.execute_query(order_sql, (order_id,))
        
        if not order_result:
            return jsonify({'error': 'Order not found'}), 404
        
        order = order_result[0]
        current_status = order['order_status']
        
        # 验证权限
        if user_id not in [order['buyer_id'], order['seller_id']]:
            return jsonify({'error': 'Permission denied'}), 403
        
        # 验证状态流转
        valid_transitions = {
            'pending_payment': ['paid', 'cancelled'],
            'paid': ['shipped', 'cancelled'],
            'shipped': ['completed'],
            'completed': [],
            'cancelled': []
        }
        
        if new_status not in valid_transitions.get(current_status, []):
            return jsonify({'error': f'Invalid status transition from {current_status} to {new_status}'}), 400
        
        # 更新订单状态
        update_fields = ['order_status = %s']
        params = [new_status]
        
        # 根据状态更新相应的时间字段
        if new_status == 'paid':
            update_fields.append('payment_time = %s')
            params.append(datetime.now())
        elif new_status == 'shipped':
            update_fields.append('ship_time = %s')
            params.append(datetime.now())
        elif new_status == 'completed':
            update_fields.append('complete_time = %s')
            params.append(datetime.now())
        
        update_sql = f"""
        UPDATE `order` 
        SET {', '.join(update_fields)}
        WHERE order_id = %s
        """
        params.append(order_id)
        
        db_manager.execute_update(update_sql, params)
        
        # 如果订单取消，恢复商品状态
        if new_status == 'cancelled':
            restore_item_sql = "UPDATE item SET status = 'available' WHERE item_id = (SELECT item_id FROM `order` WHERE order_id = %s)"
            db_manager.execute_update(restore_item_sql, (order_id,))
        
        # 如果订单完成，更新用户信用分
        if new_status == 'completed':
            # 买家和卖家都增加信用分
            update_credit_sql = "UPDATE user SET credit_score = LEAST(100, credit_score + 5) WHERE user_id IN (%s, %s)"
            db_manager.execute_update(update_credit_sql, (order['buyer_id'], order['seller_id']))
        
        return jsonify({'message': 'Order status updated successfully'}), 200
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@order_bp.route('/<int:order_id>/payment', methods=['PUT'])
def update_payment_status(order_id):
    """更新支付状态"""
    try:
        data = request.get_json()
        payment_status = data.get('payment_status')
        user_id = data.get('user_id')
        
        if not payment_status or not user_id:
            return jsonify({'error': 'payment_status and user_id are required'}), 400
        
        # 验证是否为买家
        check_sql = "SELECT buyer_id FROM `order` WHERE order_id = %s"
        result = db_manager.execute_query(check_sql, (order_id,))
        
        if not result or result[0]['buyer_id'] != user_id:
            return jsonify({'error': 'Permission denied'}), 403
        
        # 更新支付状态
        update_sql = """
        UPDATE `order` 
        SET payment_status = %s, payment_time = %s, order_status = %s
        WHERE order_id = %s
        """
        
        new_order_status = 'paid' if payment_status == 'paid' else 'pending_payment'
        payment_time = datetime.now() if payment_status == 'paid' else None
        
        db_manager.execute_update(update_sql, (payment_status, payment_time, new_order_status, order_id))
        
        return jsonify({'message': 'Payment status updated successfully'}), 200
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@order_bp.route('/<int:order_id>/cancel', methods=['PUT'])
def cancel_order(order_id):
    """取消订单"""
    try:
        data = request.get_json()
        user_id = data.get('user_id')
        
        if not user_id:
            return jsonify({'error': 'user_id is required'}), 400
        
        # 获取订单信息
        order_sql = """
        SELECT buyer_id, seller_id, order_status, item_id
        FROM `order` 
        WHERE order_id = %s
        """
        order_result = db_manager.execute_query(order_sql, (order_id,))
        
        if not order_result:
            return jsonify({'error': 'Order not found'}), 404
        
        order = order_result[0]
        
        # 验证权限
        if user_id not in [order['buyer_id'], order['seller_id']]:
            return jsonify({'error': 'Permission denied'}), 403
        
        # 验证是否可以取消
        if order['order_status'] in ['completed', 'cancelled']:
            return jsonify({'error': 'Order cannot be cancelled'}), 400
        
        # 取消订单
        cancel_sql = """
        UPDATE `order` 
        SET order_status = 'cancelled'
        WHERE order_id = %s
        """
        db_manager.execute_update(cancel_sql, (order_id,))
        
        # 恢复商品状态
        restore_item_sql = "UPDATE item SET status = 'available' WHERE item_id = %s"
        db_manager.execute_update(restore_item_sql, (order['item_id'],))
        
        return jsonify({'message': 'Order cancelled successfully'}), 200
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@order_bp.route('/statistics', methods=['GET'])
def get_order_statistics():
    """订单统计"""
    try:
        user_id = request.args.get('user_id')
        
        if not user_id:
            return jsonify({'error': 'user_id is required'}), 400
        
        # 买家统计
        buyer_stats_sql = """
        SELECT 
            COUNT(*) as total_orders,
            COUNT(CASE WHEN order_status = 'completed' THEN 1 END) as completed_orders,
            COUNT(CASE WHEN order_status = 'pending_payment' THEN 1 END) as pending_orders,
            COALESCE(SUM(CASE WHEN order_status = 'completed' THEN total_amount END), 0) as total_spent
        FROM `order`
        WHERE buyer_id = %s
        """
        
        # 卖家统计
        seller_stats_sql = """
        SELECT 
            COUNT(*) as total_sales,
            COUNT(CASE WHEN order_status = 'completed' THEN 1 END) as completed_sales,
            COUNT(CASE WHEN order_status = 'pending_payment' THEN 1 END) as pending_sales,
            COALESCE(SUM(CASE WHEN order_status = 'completed' THEN total_amount END), 0) as total_earned
        FROM `order`
        WHERE seller_id = %s
        """
        
        buyer_stats = db_manager.execute_query(buyer_stats_sql, (user_id,))
        seller_stats = db_manager.execute_query(seller_stats_sql, (user_id,))
        
        return jsonify({
            'buyer_stats': buyer_stats[0] if buyer_stats else {},
            'seller_stats': seller_stats[0] if seller_stats else {}
        }), 200
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500