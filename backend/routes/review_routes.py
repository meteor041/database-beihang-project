from flask import Blueprint, request, jsonify
from datetime import datetime
import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(__file__)))
from db import db_manager

review_bp = Blueprint('review', __name__)

@review_bp.route('/', methods=['POST'])
def create_review():
    """创建评价 - INSERT操作"""
    try:
        data = request.get_json()

        # 验证必填字段
        required_fields = ['order_id', 'reviewer_id', 'rating']
        for field in required_fields:
            if field not in data or data.get(field) is None:
                return jsonify({'error': f'{field} is required'}), 400

        order_id = data['order_id']
        reviewer_id = data['reviewer_id']
        rating = data['rating']
        content = data.get('content', '')

        # 验证评分范围
        if not isinstance(rating, int) or rating < 1 or rating > 5:
            return jsonify({'error': 'Rating must be between 1 and 5'}), 400

        # 获取订单信息
        order_sql = """
        SELECT buyer_id, seller_id, order_status
        FROM `order`
        WHERE order_id = %s
        """
        order_result = db_manager.execute_query(order_sql, (order_id,))

        if not order_result:
            return jsonify({'error': 'Order not found'}), 404

        order = order_result[0]

        # 验证订单状态必须是已完成
        if order['order_status'] != 'completed':
            return jsonify({'error': 'Can only review completed orders'}), 400

        # 验证评价者必须是买家或卖家
        if reviewer_id not in [order['buyer_id'], order['seller_id']]:
            return jsonify({'error': 'Only buyer or seller can review this order'}), 403

        # 确定被评价者
        if reviewer_id == order['buyer_id']:
            reviewee_id = order['seller_id']
        else:
            reviewee_id = order['buyer_id']

        # 检查是否已经评价过
        check_sql = """
        SELECT review_id FROM review
        WHERE order_id = %s AND reviewer_id = %s
        """
        existing = db_manager.execute_query(check_sql, (order_id, reviewer_id))

        if existing:
            return jsonify({'error': 'You have already reviewed this order'}), 400

        # 创建评价
        insert_sql = """
        INSERT INTO review (order_id, reviewer_id, reviewee_id, rating, content)
        VALUES (%s, %s, %s, %s, %s)
        """

        review_id = db_manager.execute_insert(insert_sql, (
            order_id,
            reviewer_id,
            reviewee_id,
            rating,
            content
        ))

        # 根据评分更新被评价者的信用分
        # 1分: -10, 2分: -3, 3分: 0, 4分: +1, 5分: +3
        credit_change = {5: 3, 4: 1, 3: 0, 2: -3, 1: -10}
        change = credit_change.get(rating, 0)

        if change != 0:
            if change > 0:
                update_credit_sql = """
                UPDATE user SET credit_score = LEAST(100, COALESCE(credit_score, 80) + %s)
                WHERE user_id = %s
                """
            else:
                update_credit_sql = """
                UPDATE user SET credit_score = GREATEST(0, COALESCE(credit_score, 80) + %s)
                WHERE user_id = %s
                """
            db_manager.execute_update(update_credit_sql, (change, reviewee_id))

        return jsonify({
            'message': 'Review created successfully',
            'review_id': review_id
        }), 201

    except Exception as e:
        return jsonify({'error': str(e)}), 500

@review_bp.route('/order/<int:order_id>', methods=['GET'])
def get_order_reviews(order_id):
    """获取订单的所有评价"""
    try:
        sql = """
        SELECT r.*,
               reviewer.username as reviewer_name,
               reviewer.avatar as reviewer_avatar,
               reviewee.username as reviewee_name
        FROM review r
        JOIN user reviewer ON r.reviewer_id = reviewer.user_id
        JOIN user reviewee ON r.reviewee_id = reviewee.user_id
        WHERE r.order_id = %s
        ORDER BY r.review_time DESC
        """

        reviews = db_manager.execute_query(sql, (order_id,))

        return jsonify({'reviews': reviews}), 200

    except Exception as e:
        return jsonify({'error': str(e)}), 500

@review_bp.route('/user/<int:user_id>', methods=['GET'])
def get_user_reviews(user_id):
    """获取用户收到的评价"""
    try:
        page = int(request.args.get('page', 1))
        limit = int(request.args.get('limit', 20))
        offset = (page - 1) * limit

        # 获取评价列表
        sql = """
        SELECT r.*,
               reviewer.username as reviewer_name,
               reviewer.avatar as reviewer_avatar,
               o.order_number,
               i.title as item_title
        FROM review r
        JOIN user reviewer ON r.reviewer_id = reviewer.user_id
        JOIN `order` o ON r.order_id = o.order_id
        JOIN item i ON o.item_id = i.item_id
        WHERE r.reviewee_id = %s
        ORDER BY r.review_time DESC
        LIMIT %s OFFSET %s
        """

        reviews = db_manager.execute_query(sql, (user_id, limit, offset))

        # 获取统计数据
        stats_sql = """
        SELECT
            COUNT(*) as total_reviews,
            AVG(rating) as average_rating,
            COUNT(CASE WHEN rating = 5 THEN 1 END) as five_star,
            COUNT(CASE WHEN rating = 4 THEN 1 END) as four_star,
            COUNT(CASE WHEN rating = 3 THEN 1 END) as three_star,
            COUNT(CASE WHEN rating = 2 THEN 1 END) as two_star,
            COUNT(CASE WHEN rating = 1 THEN 1 END) as one_star
        FROM review
        WHERE reviewee_id = %s
        """

        stats = db_manager.execute_query(stats_sql, (user_id,))

        return jsonify({
            'reviews': reviews,
            'stats': stats[0] if stats else {}
        }), 200

    except Exception as e:
        return jsonify({'error': str(e)}), 500

@review_bp.route('/check', methods=['GET'])
def check_review_status():
    """检查用户是否已评价某订单"""
    try:
        order_id = request.args.get('order_id')
        user_id = request.args.get('user_id')

        if not order_id or not user_id:
            return jsonify({'error': 'order_id and user_id are required'}), 400

        sql = """
        SELECT review_id, rating, content, review_time
        FROM review
        WHERE order_id = %s AND reviewer_id = %s
        """

        result = db_manager.execute_query(sql, (order_id, user_id))

        if result:
            return jsonify({
                'has_reviewed': True,
                'review': result[0]
            }), 200
        else:
            return jsonify({
                'has_reviewed': False
            }), 200

    except Exception as e:
        return jsonify({'error': str(e)}), 500
