from flask import Blueprint, request, jsonify
from datetime import datetime
import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(__file__)))
from db import db_manager
from media import parse_json_array, to_public_url

wishlist_bp = Blueprint('wishlist', __name__)

@wishlist_bp.route('/', methods=['POST'])
def add_to_wishlist():
    """添加收藏 - INSERT操作"""
    try:
        data = request.get_json()
        
        # 验证必填字段
        required_fields = ['user_id', 'item_id']
        for field in required_fields:
            if not data.get(field):
                return jsonify({'error': f'{field} is required'}), 400
        
        user_id = data['user_id']
        item_id = data['item_id']
        notes = data.get('notes', '')
        
        # 验证商品是否存在且可收藏
        item_check_sql = """
        SELECT user_id, status 
        FROM item 
        WHERE item_id = %s
        """
        item_result = db_manager.execute_query(item_check_sql, (item_id,))
        
        if not item_result:
            return jsonify({'error': 'Item not found'}), 404
        
        item = item_result[0]
        
        # 不能收藏自己发布的商品
        if item['user_id'] == user_id:
            return jsonify({'error': 'Cannot add your own item to wishlist'}), 400
        
        # 检查是否已经收藏
        check_sql = """
        SELECT wishlist_id 
        FROM wishlist 
        WHERE user_id = %s AND item_id = %s
        """
        existing = db_manager.execute_query(check_sql, (user_id, item_id))
        
        if existing:
            return jsonify({'error': 'Item already in wishlist'}), 409
        
        # 验证备注长度
        if len(notes) > 200:
            return jsonify({'error': 'Notes must be less than 200 characters'}), 400
        
        # 添加到收藏
        insert_sql = """
        INSERT INTO wishlist (user_id, item_id, notes)
        VALUES (%s, %s, %s)
        """
        
        wishlist_id = db_manager.execute_insert(insert_sql, (user_id, item_id, notes))
        
        return jsonify({
            'message': 'Item added to wishlist successfully',
            'wishlist_id': wishlist_id
        }), 201
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@wishlist_bp.route('/<int:user_id>', methods=['GET'])
def get_wishlist(user_id):
    """获取用户收藏列表"""
    try:
        page = int(request.args.get('page', 1))
        limit = int(request.args.get('limit', 20))
        category_id = request.args.get('category_id')
        sort_by = request.args.get('sort_by', 'add_time')  # add_time, price
        sort_order = request.args.get('sort_order', 'DESC')
        
        offset = (page - 1) * limit
        
        # 构建WHERE条件
        where_conditions = ["w.user_id = %s", "i.status != 'removed'"]
        params = [user_id]
        
        if category_id:
            where_conditions.append("i.category_id = %s")
            params.append(category_id)
        
        where_clause = " AND ".join(where_conditions)
        
        # 验证排序字段
        valid_sort_fields = ['add_time', 'price']
        if sort_by not in valid_sort_fields:
            sort_by = 'add_time'
        
        if sort_order.upper() not in ['ASC', 'DESC']:
            sort_order = 'DESC'
        
        # 查询收藏列表
        sql = f"""
        SELECT w.wishlist_id, w.add_time, w.notes,
               i.item_id, i.title, i.price, i.images, i.status, i.view_count,
               i.condition_level, i.location,
               u.username as seller_name, u.credit_score,
               c.category_name
        FROM wishlist w
        JOIN item i ON w.item_id = i.item_id
        JOIN user u ON i.user_id = u.user_id
        JOIN category c ON i.category_id = c.category_id
        WHERE {where_clause}
        ORDER BY w.{sort_by} {sort_order}
        LIMIT %s OFFSET %s
        """
        
        params.extend([limit, offset])
        wishlist_items = db_manager.execute_query(sql, params)
        
        # 处理图片JSON
        for item in wishlist_items:
            images = parse_json_array(item.get('images'))
            item['images'] = [to_public_url(img, request.host_url) for img in images]
        
        # 获取总数
        count_sql = f"""
        SELECT COUNT(*) as total
        FROM wishlist w
        JOIN item i ON w.item_id = i.item_id
        WHERE {where_clause}
        """
        count_result = db_manager.execute_query(count_sql, params[:-2])  # 排除limit和offset参数
        total = count_result[0]['total']
        
        return jsonify({
            'wishlist': wishlist_items,
            'pagination': {
                'page': page,
                'limit': limit,
                'total': total,
                'pages': (total + limit - 1) // limit
            }
        }), 200
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@wishlist_bp.route('/', methods=['DELETE'])
def remove_from_wishlist():
    """取消收藏 - DELETE操作"""
    try:
        data = request.get_json()
        user_id = data.get('user_id')
        item_id = data.get('item_id')
        
        if not user_id or not item_id:
            return jsonify({'error': 'user_id and item_id are required'}), 400
        
        # 删除收藏
        delete_sql = """
        DELETE FROM wishlist 
        WHERE user_id = %s AND item_id = %s
        """
        
        rows_affected = db_manager.execute_update(delete_sql, (user_id, item_id))
        
        if rows_affected == 0:
            return jsonify({'error': 'Item not found in wishlist'}), 404
        
        return jsonify({'message': 'Item removed from wishlist successfully'}), 200
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@wishlist_bp.route('/check', methods=['GET'])
def check_wishlist_status():
    """检查商品是否已收藏"""
    try:
        user_id = request.args.get('user_id')
        item_id = request.args.get('item_id')
        
        if not user_id or not item_id:
            return jsonify({'error': 'user_id and item_id are required'}), 400
        
        check_sql = """
        SELECT wishlist_id, add_time, notes
        FROM wishlist 
        WHERE user_id = %s AND item_id = %s
        """
        
        result = db_manager.execute_query(check_sql, (user_id, item_id))
        
        if result:
            return jsonify({
                'is_favorited': True,
                'wishlist_info': result[0]
            }), 200
        else:
            return jsonify({'is_favorited': False}), 200
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@wishlist_bp.route('/batch', methods=['DELETE'])
def batch_remove_from_wishlist():
    """批量删除收藏"""
    try:
        data = request.get_json()
        user_id = data.get('user_id')
        item_ids = data.get('item_ids', [])
        
        if not user_id or not item_ids:
            return jsonify({'error': 'user_id and item_ids are required'}), 400
        
        if len(item_ids) > 100:
            return jsonify({'error': 'Maximum 100 items can be removed at once'}), 400
        
        # 构建批量删除SQL
        placeholders = ','.join(['%s'] * len(item_ids))
        delete_sql = f"""
        DELETE FROM wishlist 
        WHERE user_id = %s AND item_id IN ({placeholders})
        """
        
        params = [user_id] + item_ids
        rows_affected = db_manager.execute_update(delete_sql, params)
        
        return jsonify({
            'message': 'Items removed from wishlist successfully',
            'removed_count': rows_affected
        }), 200
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@wishlist_bp.route('/<int:wishlist_id>/notes', methods=['PUT'])
def update_wishlist_notes(wishlist_id):
    """更新收藏备注"""
    try:
        data = request.get_json()
        user_id = data.get('user_id')
        notes = data.get('notes', '')
        
        if not user_id:
            return jsonify({'error': 'user_id is required'}), 400
        
        # 验证备注长度
        if len(notes) > 200:
            return jsonify({'error': 'Notes must be less than 200 characters'}), 400
        
        # 验证是否为用户的收藏
        check_sql = "SELECT user_id FROM wishlist WHERE wishlist_id = %s"
        result = db_manager.execute_query(check_sql, (wishlist_id,))
        
        if not result:
            return jsonify({'error': 'Wishlist item not found'}), 404
        
        if result[0]['user_id'] != user_id:
            return jsonify({'error': 'Permission denied'}), 403
        
        # 更新备注
        update_sql = "UPDATE wishlist SET notes = %s WHERE wishlist_id = %s"
        db_manager.execute_update(update_sql, (notes, wishlist_id))
        
        return jsonify({'message': 'Wishlist notes updated successfully'}), 200
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@wishlist_bp.route('/statistics/<int:user_id>', methods=['GET'])
def get_wishlist_statistics(user_id):
    """获取收藏统计信息"""
    try:
        # 总收藏数
        total_sql = """
        SELECT COUNT(*) as total_count
        FROM wishlist w
        JOIN item i ON w.item_id = i.item_id
        WHERE w.user_id = %s AND i.status != 'removed'
        """
        
        # 按分类统计
        category_sql = """
        SELECT c.category_name, COUNT(*) as count
        FROM wishlist w
        JOIN item i ON w.item_id = i.item_id
        JOIN category c ON i.category_id = c.category_id
        WHERE w.user_id = %s AND i.status != 'removed'
        GROUP BY c.category_id, c.category_name
        ORDER BY count DESC
        """
        
        # 按状态统计
        status_sql = """
        SELECT i.status, COUNT(*) as count
        FROM wishlist w
        JOIN item i ON w.item_id = i.item_id
        WHERE w.user_id = %s
        GROUP BY i.status
        """
        
        total_result = db_manager.execute_query(total_sql, (user_id,))
        category_stats = db_manager.execute_query(category_sql, (user_id,))
        status_stats = db_manager.execute_query(status_sql, (user_id,))
        
        return jsonify({
            'total_count': total_result[0]['total_count'] if total_result else 0,
            'category_stats': category_stats,
            'status_stats': status_stats
        }), 200
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@wishlist_bp.route('/item/<int:item_id>/count', methods=['GET'])
def get_item_wishlist_count(item_id):
    """获取商品被收藏次数"""
    try:
        sql = """
        SELECT COUNT(*) as wishlist_count
        FROM wishlist 
        WHERE item_id = %s
        """
        
        result = db_manager.execute_query(sql, (item_id,))
        count = result[0]['wishlist_count'] if result else 0
        
        return jsonify({'wishlist_count': count}), 200
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500
