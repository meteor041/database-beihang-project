from flask import Blueprint, request, jsonify
from datetime import datetime
import json
import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(__file__)))
from db import db_manager

item_bp = Blueprint('item', __name__)

@item_bp.route('/', methods=['POST'])
def create_item():
    """商品发布 - INSERT操作"""
    try:
        data = request.get_json()
        
        # 验证必填字段
        required_fields = ['user_id', 'category_id', 'title', 'description', 'price', 'condition_level', 'location']
        for field in required_fields:
            if not data.get(field):
                return jsonify({'error': f'{field} is required'}), 400
        
        # 验证价格
        if float(data['price']) <= 0:
            return jsonify({'error': 'Price must be greater than 0'}), 400
        
        # 验证原价
        if data.get('original_price') and float(data['original_price']) < float(data['price']):
            return jsonify({'error': 'Original price must be greater than or equal to current price'}), 400
        
        # 验证标题和描述长度
        if len(data['title']) > 100:
            return jsonify({'error': 'Title must be less than 100 characters'}), 400
        if len(data['description']) > 1000:
            return jsonify({'error': 'Description must be less than 1000 characters'}), 400
        
        # 处理图片数组
        images = data.get('images', [])
        if len(images) > 9:
            return jsonify({'error': 'Maximum 9 images allowed'}), 400
        
        # 插入商品
        insert_sql = """
        INSERT INTO item (user_id, category_id, title, description, price, original_price, 
                         condition_level, images, location)
        VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s)
        """
        
        item_id = db_manager.execute_insert(insert_sql, (
            data['user_id'],
            data['category_id'],
            data['title'],
            data['description'],
            data['price'],
            data.get('original_price'),
            data['condition_level'],
            json.dumps(images) if images else None,
            data['location']
        ))
        
        return jsonify({
            'message': 'Item created successfully',
            'item_id': item_id
        }), 201
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@item_bp.route('/', methods=['GET'])
def get_items():
    """商品浏览 - SELECT with JOIN操作"""
    try:
        page = int(request.args.get('page', 1))
        limit = int(request.args.get('limit', 20))
        category_id = request.args.get('category_id')
        status = request.args.get('status', 'available')
        sort_by = request.args.get('sort_by', 'publish_date')  # publish_date, price, view_count
        sort_order = request.args.get('sort_order', 'DESC')
        min_price = request.args.get('min_price')
        max_price = request.args.get('max_price')

        offset = (page - 1) * limit

        # 构建WHERE条件
        where_conditions = ["i.status = %s"]
        params = [status]

        if category_id:
            where_conditions.append("i.category_id = %s")
            params.append(category_id)

        if min_price:
            where_conditions.append("i.price >= %s")
            params.append(float(min_price))

        if max_price:
            where_conditions.append("i.price <= %s")
            params.append(float(max_price))

        where_clause = " AND ".join(where_conditions)
        
        # 验证排序字段
        valid_sort_fields = ['publish_date', 'price', 'view_count']
        if sort_by not in valid_sort_fields:
            sort_by = 'publish_date'
        
        if sort_order.upper() not in ['ASC', 'DESC']:
            sort_order = 'DESC'
        
        # 查询商品列表（JOIN用户和分类表）
        sql = f"""
        SELECT i.item_id, i.title, i.description, i.price, i.original_price,
               i.condition_level, i.images, i.location, i.publish_date, i.view_count,
               u.username, u.avatar, u.credit_score,
               c.category_name
        FROM item i
        JOIN user u ON i.user_id = u.user_id
        JOIN category c ON i.category_id = c.category_id
        WHERE {where_clause}
        ORDER BY i.{sort_by} {sort_order}
        LIMIT %s OFFSET %s
        """
        
        params.extend([limit, offset])
        items = db_manager.execute_query(sql, params)
        
        # 处理图片JSON
        for item in items:
            if item['images']:
                item['images'] = json.loads(item['images'])
            else:
                item['images'] = []
        
        # 获取总数
        count_sql = f"""
        SELECT COUNT(*) as total
        FROM item i
        WHERE {where_clause}
        """
        count_result = db_manager.execute_query(count_sql, params[:-2])  # 排除limit和offset参数
        total = count_result[0]['total']
        
        return jsonify({
            'items': items,
            'pagination': {
                'page': page,
                'limit': limit,
                'total': total,
                'pages': (total + limit - 1) // limit
            }
        }), 200
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@item_bp.route('/search', methods=['GET'])
def search_items():
    """商品搜索 - SELECT with JOIN和全文搜索"""
    try:
        keyword = request.args.get('keyword', '')
        category_id = request.args.get('category_id')
        min_price = request.args.get('min_price')
        max_price = request.args.get('max_price')
        condition_level = request.args.get('condition_level')
        page = int(request.args.get('page', 1))
        limit = int(request.args.get('limit', 20))
        sort_by = request.args.get('sort_by', 'publish_date')
        sort_order = request.args.get('sort_order', 'DESC')
        
        offset = (page - 1) * limit
        
        # 构建WHERE条件
        where_conditions = ["i.status = 'available'"]
        params = []
        
        if keyword:
            where_conditions.append("(i.title LIKE %s OR i.description LIKE %s)")
            keyword_pattern = f"%{keyword}%"
            params.extend([keyword_pattern, keyword_pattern])
        
        if category_id:
            where_conditions.append("i.category_id = %s")
            params.append(category_id)
        
        if min_price:
            where_conditions.append("i.price >= %s")
            params.append(float(min_price))
        
        if max_price:
            where_conditions.append("i.price <= %s")
            params.append(float(max_price))
        
        if condition_level:
            where_conditions.append("i.condition_level = %s")
            params.append(condition_level)
        
        where_clause = " AND ".join(where_conditions)
        
        # 验证排序字段
        valid_sort_fields = ['publish_date', 'price', 'view_count']
        if sort_by not in valid_sort_fields:
            sort_by = 'publish_date'
        
        if sort_order.upper() not in ['ASC', 'DESC']:
            sort_order = 'DESC'
        
        # 搜索查询
        sql = f"""
        SELECT i.item_id, i.title, i.description, i.price, i.original_price,
               i.condition_level, i.images, i.location, i.publish_date, i.view_count,
               u.username, u.avatar, u.credit_score,
               c.category_name
        FROM item i
        JOIN user u ON i.user_id = u.user_id
        JOIN category c ON i.category_id = c.category_id
        WHERE {where_clause}
        ORDER BY i.{sort_by} {sort_order}
        LIMIT %s OFFSET %s
        """
        
        params.extend([limit, offset])
        items = db_manager.execute_query(sql, params)
        
        # 处理图片JSON
        for item in items:
            if item['images']:
                item['images'] = json.loads(item['images'])
            else:
                item['images'] = []
        
        return jsonify({'items': items}), 200
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@item_bp.route('/<int:item_id>', methods=['GET'])
def get_item(item_id):
    """获取商品详情并增加浏览次数"""
    try:
        # 增加浏览次数
        update_view_sql = "UPDATE item SET view_count = view_count + 1 WHERE item_id = %s"
        db_manager.execute_update(update_view_sql, (item_id,))
        
        # 获取商品详情
        sql = """
        SELECT i.*, u.username, u.avatar, u.credit_score, u.phone,
               c.category_name
        FROM item i
        JOIN user u ON i.user_id = u.user_id
        JOIN category c ON i.category_id = c.category_id
        WHERE i.item_id = %s
        """
        
        items = db_manager.execute_query(sql, (item_id,))
        
        if not items:
            return jsonify({'error': 'Item not found'}), 404
        
        item = items[0]
        
        # 处理图片JSON
        if item['images']:
            item['images'] = json.loads(item['images'])
        else:
            item['images'] = []
        
        return jsonify({'item': item}), 200
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@item_bp.route('/<int:item_id>', methods=['PUT'])
def update_item(item_id):
    """商品信息修改 - UPDATE操作"""
    try:
        data = request.get_json()
        user_id = data.get('user_id')  # 验证是否为商品发布者
        
        if not user_id:
            return jsonify({'error': 'user_id is required'}), 400
        
        # 验证是否为商品发布者
        check_sql = "SELECT user_id FROM item WHERE item_id = %s"
        result = db_manager.execute_query(check_sql, (item_id,))
        
        if not result:
            return jsonify({'error': 'Item not found'}), 404
        
        if result[0]['user_id'] != user_id:
            return jsonify({'error': 'Permission denied'}), 403
        
        # 可更新的字段
        updatable_fields = ['title', 'description', 'price', 'original_price', 
                           'condition_level', 'images', 'location']
        update_data = {}
        
        for field in updatable_fields:
            if field in data:
                if field == 'price' and float(data[field]) <= 0:
                    return jsonify({'error': 'Price must be greater than 0'}), 400
                if field == 'title' and len(data[field]) > 100:
                    return jsonify({'error': 'Title must be less than 100 characters'}), 400
                if field == 'description' and len(data[field]) > 1000:
                    return jsonify({'error': 'Description must be less than 1000 characters'}), 400
                if field == 'images' and len(data[field]) > 9:
                    return jsonify({'error': 'Maximum 9 images allowed'}), 400
                
                if field == 'images':
                    update_data[field] = json.dumps(data[field]) if data[field] else None
                else:
                    update_data[field] = data[field]
        
        if not update_data:
            return jsonify({'error': 'No valid fields to update'}), 400
        
        # 构建更新SQL
        set_clause = ', '.join([f"{field} = %s" for field in update_data.keys()])
        update_sql = f"UPDATE item SET {set_clause}, update_date = %s WHERE item_id = %s"
        
        params = list(update_data.values()) + [datetime.now(), item_id]
        db_manager.execute_update(update_sql, params)
        
        return jsonify({'message': 'Item updated successfully'}), 200
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@item_bp.route('/<int:item_id>', methods=['DELETE'])
def delete_item(item_id):
    """商品下架 - DELETE操作（软删除）"""
    try:
        data = request.get_json()
        user_id = data.get('user_id')
        
        if not user_id:
            return jsonify({'error': 'user_id is required'}), 400
        
        # 验证是否为商品发布者
        check_sql = "SELECT user_id FROM item WHERE item_id = %s"
        result = db_manager.execute_query(check_sql, (item_id,))
        
        if not result:
            return jsonify({'error': 'Item not found'}), 404
        
        if result[0]['user_id'] != user_id:
            return jsonify({'error': 'Permission denied'}), 403
        
        # 软删除：将状态设为removed
        sql = "UPDATE item SET status = 'removed' WHERE item_id = %s"
        db_manager.execute_update(sql, (item_id,))
        
        return jsonify({'message': 'Item removed successfully'}), 200
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@item_bp.route('/categories', methods=['GET'])
def get_categories():
    """获取商品分类"""
    try:
        sql = """
        SELECT c.category_id, c.category_name, c.parent_category_id, c.description,
               COUNT(i.item_id) as item_count
        FROM category c
        LEFT JOIN item i ON c.category_id = i.category_id AND i.status = 'available'
        GROUP BY c.category_id, c.category_name, c.parent_category_id, c.description
        ORDER BY c.sort_order, c.category_name
        """
        
        categories = db_manager.execute_query(sql)
        
        # 构建分类树
        category_tree = []
        category_map = {}
        
        # 先创建所有分类的映射
        for cat in categories:
            category_map[cat['category_id']] = {
                'category_id': cat['category_id'],
                'category_name': cat['category_name'],
                'description': cat['description'],
                'item_count': cat['item_count'],
                'children': []
            }
        
        # 构建树结构
        for cat in categories:
            if cat['parent_category_id'] is None:
                category_tree.append(category_map[cat['category_id']])
            else:
                parent = category_map.get(cat['parent_category_id'])
                if parent:
                    parent['children'].append(category_map[cat['category_id']])
        
        return jsonify({'categories': category_tree}), 200
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@item_bp.route('/user/<int:user_id>', methods=['GET'])
def get_user_items(user_id):
    """获取用户发布的商品"""
    try:
        status = request.args.get('status', 'available')
        page = int(request.args.get('page', 1))
        limit = int(request.args.get('limit', 20))
        offset = (page - 1) * limit
        
        sql = """
        SELECT i.item_id, i.title, i.price, i.images, i.status, i.publish_date, i.view_count,
               c.category_name
        FROM item i
        JOIN category c ON i.category_id = c.category_id
        WHERE i.user_id = %s AND i.status = %s
        ORDER BY i.publish_date DESC
        LIMIT %s OFFSET %s
        """
        
        items = db_manager.execute_query(sql, (user_id, status, limit, offset))
        
        # 处理图片JSON
        for item in items:
            if item['images']:
                item['images'] = json.loads(item['images'])
            else:
                item['images'] = []
        
        return jsonify({'items': items}), 200
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500