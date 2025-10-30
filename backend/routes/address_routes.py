from flask import Blueprint, request, jsonify
import re
import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(__file__)))
from db import db_manager

address_bp = Blueprint('address', __name__)

def validate_phone(phone):
    """验证手机号格式"""
    pattern = r'^1[3-9][0-9]{9}$'
    return re.match(pattern, phone) is not None

def validate_postal_code(postal_code):
    """验证邮政编码格式"""
    if not postal_code:
        return True  # 邮政编码可以为空
    pattern = r'^[0-9]{6}$'
    return re.match(pattern, postal_code) is not None

@address_bp.route('/', methods=['POST'])
def add_address():
    """地址添加 - INSERT操作"""
    try:
        data = request.get_json()
        
        # 验证必填字段
        required_fields = ['user_id', 'recipient_name', 'phone', 'province', 'city', 'district', 'detailed_address']
        for field in required_fields:
            if not data.get(field):
                return jsonify({'error': f'{field} is required'}), 400
        
        # 验证手机号格式
        if not validate_phone(data['phone']):
            return jsonify({'error': 'Invalid phone format'}), 400
        
        # 验证邮政编码格式
        postal_code = data.get('postal_code')
        if postal_code and not validate_postal_code(postal_code):
            return jsonify({'error': 'Invalid postal code format'}), 400
        
        # 验证详细地址长度
        if len(data['detailed_address']) > 200:
            return jsonify({'error': 'Detailed address must be less than 200 characters'}), 400
        
        # 检查用户地址数量限制
        count_sql = "SELECT COUNT(*) as count FROM address WHERE user_id = %s"
        count_result = db_manager.execute_query(count_sql, (data['user_id'],))
        
        if count_result and count_result[0]['count'] >= 20:
            return jsonify({'error': 'Maximum 20 addresses allowed per user'}), 400
        
        # 如果设置为默认地址，先取消其他默认地址
        is_default = data.get('is_default', False)
        if is_default:
            update_default_sql = "UPDATE address SET is_default = FALSE WHERE user_id = %s"
            db_manager.execute_update(update_default_sql, (data['user_id'],))
        
        # 如果是第一个地址，自动设为默认
        if count_result and count_result[0]['count'] == 0:
            is_default = True
        
        # 插入地址
        insert_sql = """
        INSERT INTO address (user_id, recipient_name, phone, province, city, district,
                           detailed_address, postal_code, is_default, address_type)
        VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
        """
        
        address_id = db_manager.execute_insert(insert_sql, (
            data['user_id'],
            data['recipient_name'],
            data['phone'],
            data['province'],
            data['city'],
            data['district'],
            data['detailed_address'],
            postal_code,
            is_default,
            data.get('address_type', 'dormitory')
        ))
        
        return jsonify({
            'message': 'Address added successfully',
            'address_id': address_id
        }), 201
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@address_bp.route('/user/<int:user_id>', methods=['GET'])
def get_user_addresses(user_id):
    """获取用户地址列表"""
    try:
        sql = """
        SELECT address_id, recipient_name, phone, province, city, district,
               detailed_address, postal_code, is_default, address_type
        FROM address 
        WHERE user_id = %s
        ORDER BY is_default DESC, address_id DESC
        """
        
        addresses = db_manager.execute_query(sql, (user_id,))
        
        return jsonify({'addresses': addresses}), 200
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@address_bp.route('/<int:address_id>', methods=['GET'])
def get_address(address_id):
    """获取单个地址详情"""
    try:
        sql = """
        SELECT address_id, user_id, recipient_name, phone, province, city, district,
               detailed_address, postal_code, is_default, address_type
        FROM address 
        WHERE address_id = %s
        """
        
        addresses = db_manager.execute_query(sql, (address_id,))
        
        if not addresses:
            return jsonify({'error': 'Address not found'}), 404
        
        return jsonify({'address': addresses[0]}), 200
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@address_bp.route('/<int:address_id>', methods=['PUT'])
def update_address(address_id):
    """地址编辑 - UPDATE操作"""
    try:
        data = request.get_json()
        user_id = data.get('user_id')
        
        if not user_id:
            return jsonify({'error': 'user_id is required'}), 400
        
        # 验证地址是否属于该用户
        check_sql = "SELECT user_id FROM address WHERE address_id = %s"
        result = db_manager.execute_query(check_sql, (address_id,))
        
        if not result:
            return jsonify({'error': 'Address not found'}), 404
        
        if result[0]['user_id'] != user_id:
            return jsonify({'error': 'Permission denied'}), 403
        
        # 可更新的字段
        updatable_fields = ['recipient_name', 'phone', 'province', 'city', 'district',
                           'detailed_address', 'postal_code', 'address_type', 'is_default']
        update_data = {}
        
        for field in updatable_fields:
            if field in data:
                # 验证格式
                if field == 'phone' and not validate_phone(data[field]):
                    return jsonify({'error': 'Invalid phone format'}), 400
                if field == 'postal_code' and data[field] and not validate_postal_code(data[field]):
                    return jsonify({'error': 'Invalid postal code format'}), 400
                if field == 'detailed_address' and len(data[field]) > 200:
                    return jsonify({'error': 'Detailed address must be less than 200 characters'}), 400
                
                update_data[field] = data[field]
        
        if not update_data:
            return jsonify({'error': 'No valid fields to update'}), 400
        
        # 如果设置为默认地址，先取消其他默认地址
        if update_data.get('is_default'):
            update_default_sql = "UPDATE address SET is_default = FALSE WHERE user_id = %s AND address_id != %s"
            db_manager.execute_update(update_default_sql, (user_id, address_id))
        
        # 构建更新SQL
        set_clause = ', '.join([f"{field} = %s" for field in update_data.keys()])
        update_sql = f"UPDATE address SET {set_clause} WHERE address_id = %s"
        
        params = list(update_data.values()) + [address_id]
        db_manager.execute_update(update_sql, params)
        
        return jsonify({'message': 'Address updated successfully'}), 200
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@address_bp.route('/<int:address_id>', methods=['DELETE'])
def delete_address(address_id):
    """地址删除 - DELETE操作"""
    try:
        data = request.get_json()
        user_id = data.get('user_id')
        
        if not user_id:
            return jsonify({'error': 'user_id is required'}), 400
        
        # 验证地址是否属于该用户
        check_sql = "SELECT user_id, is_default FROM address WHERE address_id = %s"
        result = db_manager.execute_query(check_sql, (address_id,))
        
        if not result:
            return jsonify({'error': 'Address not found'}), 404
        
        address = result[0]
        
        if address['user_id'] != user_id:
            return jsonify({'error': 'Permission denied'}), 403

        # 检查是否有未完成的订单使用此地址
        order_check_sql = """
        SELECT COUNT(*) as count
        FROM `order`
        WHERE address_id = %s AND order_status NOT IN ('completed', 'cancelled')
        """
        order_result = db_manager.execute_query(order_check_sql, (address_id,))

        if order_result and order_result[0]['count'] > 0:
            return jsonify({'error': 'Cannot delete address with pending orders'}), 400
        
        # 删除地址
        delete_sql = "DELETE FROM address WHERE address_id = %s"
        db_manager.execute_update(delete_sql, (address_id,))
        
        # 如果删除的是默认地址，设置另一个地址为默认
        if address['is_default']:
            set_new_default_sql = """
            UPDATE address 
            SET is_default = TRUE 
            WHERE user_id = %s 
            ORDER BY address_id DESC 
            LIMIT 1
            """
            db_manager.execute_update(set_new_default_sql, (user_id,))
        
        return jsonify({'message': 'Address deleted successfully'}), 200
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@address_bp.route('/<int:address_id>/default', methods=['PUT'])
def set_default_address(address_id):
    """设置默认地址"""
    try:
        data = request.get_json()
        user_id = data.get('user_id')
        
        if not user_id:
            return jsonify({'error': 'user_id is required'}), 400
        
        # 验证地址是否属于该用户
        check_sql = "SELECT user_id FROM address WHERE address_id = %s"
        result = db_manager.execute_query(check_sql, (address_id,))
        
        if not result:
            return jsonify({'error': 'Address not found'}), 404
        
        if result[0]['user_id'] != user_id:
            return jsonify({'error': 'Permission denied'}), 403
        
        # 取消其他默认地址
        update_others_sql = "UPDATE address SET is_default = FALSE WHERE user_id = %s"
        db_manager.execute_update(update_others_sql, (user_id,))
        
        # 设置新的默认地址
        update_default_sql = "UPDATE address SET is_default = TRUE WHERE address_id = %s"
        db_manager.execute_update(update_default_sql, (address_id,))
        
        return jsonify({'message': 'Default address updated successfully'}), 200
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@address_bp.route('/search', methods=['GET'])
def search_addresses():
    """地址搜索"""
    try:
        user_id = request.args.get('user_id')
        keyword = request.args.get('keyword', '')
        
        if not user_id:
            return jsonify({'error': 'user_id is required'}), 400
        
        if keyword:
            sql = """
            SELECT address_id, recipient_name, phone, province, city, district,
                   detailed_address, postal_code, is_default, address_type
            FROM address 
            WHERE user_id = %s AND (
                recipient_name LIKE %s OR 
                phone LIKE %s OR 
                detailed_address LIKE %s OR
                CONCAT(province, city, district) LIKE %s
            )
            ORDER BY is_default DESC, address_id DESC
            """
            keyword_pattern = f"%{keyword}%"
            addresses = db_manager.execute_query(sql, (user_id, keyword_pattern, keyword_pattern, 
                                                     keyword_pattern, keyword_pattern))
        else:
            # 如果没有关键词，返回所有地址
            sql = """
            SELECT address_id, recipient_name, phone, province, city, district,
                   detailed_address, postal_code, is_default, address_type
            FROM address 
            WHERE user_id = %s
            ORDER BY is_default DESC, address_id DESC
            """
            addresses = db_manager.execute_query(sql, (user_id,))
        
        return jsonify({'addresses': addresses}), 200
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@address_bp.route('/default/<int:user_id>', methods=['GET'])
def get_default_address(user_id):
    """获取用户默认地址"""
    try:
        sql = """
        SELECT address_id, recipient_name, phone, province, city, district,
               detailed_address, postal_code, address_type
        FROM address 
        WHERE user_id = %s AND is_default = TRUE
        """
        
        addresses = db_manager.execute_query(sql, (user_id,))
        
        if not addresses:
            # 如果没有默认地址，返回第一个地址
            sql = """
            SELECT address_id, recipient_name, phone, province, city, district,
                   detailed_address, postal_code, address_type
            FROM address 
            WHERE user_id = %s
            ORDER BY address_id DESC
            LIMIT 1
            """
            addresses = db_manager.execute_query(sql, (user_id,))
        
        if addresses:
            return jsonify({'address': addresses[0]}), 200
        else:
            return jsonify({'error': 'No address found'}), 404
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@address_bp.route('/statistics/<int:user_id>', methods=['GET'])
def get_address_statistics(user_id):
    """获取地址统计信息"""
    try:
        # 总地址数
        total_sql = "SELECT COUNT(*) as total_count FROM address WHERE user_id = %s"
        
        # 按类型统计
        type_sql = """
        SELECT address_type, COUNT(*) as count
        FROM address 
        WHERE user_id = %s
        GROUP BY address_type
        """
        
        # 按城市统计
        city_sql = """
        SELECT CONCAT(province, '-', city) as location, COUNT(*) as count
        FROM address 
        WHERE user_id = %s
        GROUP BY province, city
        ORDER BY count DESC
        """
        
        total_result = db_manager.execute_query(total_sql, (user_id,))
        type_stats = db_manager.execute_query(type_sql, (user_id,))
        city_stats = db_manager.execute_query(city_sql, (user_id,))
        
        return jsonify({
            'total_count': total_result[0]['total_count'] if total_result else 0,
            'type_stats': type_stats,
            'city_stats': city_stats
        }), 200
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500