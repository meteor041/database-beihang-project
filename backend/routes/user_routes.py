from flask import Blueprint, request, jsonify
from datetime import datetime
import re
import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(__file__)))
from db import db_manager

user_bp = Blueprint('user', __name__)
INITIAL_CREDIT_SCORE = 80

def validate_email(email):
    """验证邮箱格式"""
    pattern = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
    return re.match(pattern, email) is not None

def validate_phone(phone):
    """验证手机号格式"""
    pattern = r'^1[3-9][0-9]{9}$'
    return re.match(pattern, phone) is not None

def validate_password(password):
    """验证密码强度"""
    if len(password) < 8:
        return False
    has_letter = re.search(r'[a-zA-Z]', password)
    has_number = re.search(r'[0-9]', password)
    return has_letter and has_number

@user_bp.route('/register', methods=['POST'])
def register():
    """用户注册 - INSERT操作"""
    try:
        data = request.get_json()
        
        # 验证必填字段
        required_fields = ['student_id', 'username', 'password', 'real_name', 'phone', 'email']
        for field in required_fields:
            if not data.get(field):
                return jsonify({'error': f'{field} is required'}), 400
        
        # 验证数据格式
        if not validate_email(data['email']):
            return jsonify({'error': 'Invalid email format'}), 400
        
        if not validate_phone(data['phone']):
            return jsonify({'error': 'Invalid phone format'}), 400
        
        if not validate_password(data['password']):
            return jsonify({'error': 'Password must be at least 8 characters with letters and numbers'}), 400
        
        # 检查学号和用户名是否已存在
        check_sql = """
        SELECT user_id FROM user 
        WHERE student_id = %s OR username = %s OR phone = %s OR email = %s
        """
        existing = db_manager.execute_query(check_sql, 
            (data['student_id'], data['username'], data['phone'], data['email']))
        
        if existing:
            return jsonify({'error': 'Student ID, username, phone or email already exists'}), 409
        
        # 插入新用户
        insert_sql = """
        INSERT INTO user (student_id, username, password, real_name, phone, email, avatar, credit_score)
        VALUES (%s, %s, %s, %s, %s, %s, %s, %s)
        """
        hashed_password = db_manager.hash_password(data['password'])
        
        user_id = db_manager.execute_insert(insert_sql, (
            data['student_id'],
            data['username'],
            hashed_password,
            data['real_name'],
            data['phone'],
            data['email'],
            data.get('avatar'),
            INITIAL_CREDIT_SCORE
        ))
        
        return jsonify({
            'message': 'User registered successfully',
            'user_id': user_id
        }), 201
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@user_bp.route('/login', methods=['POST'])
def login():
    """用户登录"""
    try:
        data = request.get_json()
        login_field = data.get('login_field')  # 用户名/学号/手机号
        password = data.get('password')
        
        if not login_field or not password:
            return jsonify({'error': 'Login field and password are required'}), 400
        
        # 查询用户
        login_sql = """
        SELECT user_id, username, password, real_name, phone, email, avatar, 
               credit_score, status, last_login
        FROM user 
        WHERE username = %s OR student_id = %s OR phone = %s
        """
        users = db_manager.execute_query(login_sql, (login_field, login_field, login_field))
        
        if not users:
            return jsonify({'error': 'User not found'}), 404
        
        user = users[0]
        
        # 验证密码
        hashed_password = db_manager.hash_password(password)
        if user['password'] != hashed_password:
            return jsonify({'error': 'Invalid password'}), 401
        
        # 检查账户状态
        if user['status'] != 'active':
            return jsonify({'error': 'Account is not active'}), 403
        
        # 更新最后登录时间
        update_sql = "UPDATE user SET last_login = %s WHERE user_id = %s"
        db_manager.execute_update(update_sql, (datetime.now(), user['user_id']))
        
        # 返回用户信息（不包含密码）
        user_info = {
            'user_id': user['user_id'],
            'username': user['username'],
            'real_name': user['real_name'],
            'phone': user['phone'],
            'email': user['email'],
            'avatar': user['avatar'],
            'credit_score': user['credit_score'],
            'last_login': user['last_login']
        }
        
        return jsonify({
            'message': 'Login successful',
            'user': user_info
        }), 200
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@user_bp.route('/<int:user_id>', methods=['GET'])
def get_user(user_id):
    """查询用户信息 - SELECT操作"""
    try:
        sql = """
        SELECT user_id, student_id, username, real_name, phone, email, avatar,
               credit_score, registration_date, last_login, status
        FROM user 
        WHERE user_id = %s AND status != 'deleted'
        """
        users = db_manager.execute_query(sql, (user_id,))
        
        if not users:
            return jsonify({'error': 'User not found'}), 404
        
        return jsonify({'user': users[0]}), 200
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@user_bp.route('/<int:user_id>', methods=['PUT'])
def update_user(user_id):
    """修改用户信息 - UPDATE操作"""
    try:
        data = request.get_json()
        
        # 可更新的字段
        updatable_fields = ['username', 'real_name', 'phone', 'email', 'avatar']
        update_data = {}
        
        for field in updatable_fields:
            if field in data:
                # 验证格式
                if field == 'email' and not validate_email(data[field]):
                    return jsonify({'error': 'Invalid email format'}), 400
                if field == 'phone' and not validate_phone(data[field]):
                    return jsonify({'error': 'Invalid phone format'}), 400
                
                update_data[field] = data[field]
        
        if not update_data:
            return jsonify({'error': 'No valid fields to update'}), 400
        
        # 检查用户名、手机号、邮箱是否已被其他用户使用
        if 'username' in update_data or 'phone' in update_data or 'email' in update_data:
            check_conditions = []
            check_params = []
            
            if 'username' in update_data:
                check_conditions.append("username = %s")
                check_params.append(update_data['username'])
            if 'phone' in update_data:
                check_conditions.append("phone = %s")
                check_params.append(update_data['phone'])
            if 'email' in update_data:
                check_conditions.append("email = %s")
                check_params.append(update_data['email'])
            
            check_sql = f"""
            SELECT user_id FROM user 
            WHERE ({' OR '.join(check_conditions)}) AND user_id != %s
            """
            check_params.append(user_id)
            
            existing = db_manager.execute_query(check_sql, check_params)
            if existing:
                return jsonify({'error': 'Username, phone or email already exists'}), 409
        
        # 构建更新SQL
        set_clause = ', '.join([f"{field} = %s" for field in update_data.keys()])
        update_sql = f"UPDATE user SET {set_clause} WHERE user_id = %s"
        
        params = list(update_data.values()) + [user_id]
        rows_affected = db_manager.execute_update(update_sql, params)
        
        if rows_affected == 0:
            return jsonify({'error': 'User not found'}), 404
        
        return jsonify({'message': 'User updated successfully'}), 200
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@user_bp.route('/<int:user_id>', methods=['DELETE'])
def delete_user(user_id):
    """用户注销 - DELETE操作（软删除）"""
    try:
        # 软删除：将状态设为deleted
        sql = "UPDATE user SET status = 'deleted' WHERE user_id = %s AND status != 'deleted'"
        rows_affected = db_manager.execute_update(sql, (user_id,))
        
        if rows_affected == 0:
            return jsonify({'error': 'User not found or already deleted'}), 404
        
        return jsonify({'message': 'User deleted successfully'}), 200
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@user_bp.route('/search', methods=['GET'])
def search_users():
    """搜索用户"""
    try:
        keyword = request.args.get('keyword', '')
        page = int(request.args.get('page', 1))
        limit = int(request.args.get('limit', 20))
        offset = (page - 1) * limit
        
        if keyword:
            sql = """
            SELECT user_id, username, real_name, avatar, credit_score
            FROM user
            WHERE (username LIKE %s OR real_name LIKE %s) AND status = 'active'
            ORDER BY credit_score DESC
            LIMIT %s OFFSET %s
            """
            keyword_pattern = f"%{keyword}%"
            users = db_manager.execute_query(sql, (keyword_pattern, keyword_pattern, limit, offset))

            # 获取总数
            count_sql = """
            SELECT COUNT(*) as total FROM user
            WHERE (username LIKE %s OR real_name LIKE %s) AND status = 'active'
            """
            count_result = db_manager.execute_query(count_sql, (keyword_pattern, keyword_pattern))
        else:
            sql = """
            SELECT user_id, username, real_name, avatar, credit_score
            FROM user
            WHERE status = 'active'
            ORDER BY registration_date DESC
            LIMIT %s OFFSET %s
            """
            users = db_manager.execute_query(sql, (limit, offset))

            # 获取总数
            count_sql = "SELECT COUNT(*) as total FROM user WHERE status = 'active'"
            count_result = db_manager.execute_query(count_sql)

        total = count_result[0]['total'] if count_result else 0

        return jsonify({
            'users': users,
            'pagination': {
                'page': page,
                'limit': limit,
                'total': total,
                'pages': (total + limit - 1) // limit
            }
        }), 200
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@user_bp.route('/<int:user_id>/credit', methods=['PUT'])
def update_credit(user_id):
    """更新用户信用分"""
    try:
        data = request.get_json()
        change = data.get('change', 0)
        
        sql = """
        UPDATE user 
        SET credit_score = GREATEST(0, LEAST(100, COALESCE(credit_score, 80) + %s))
        WHERE user_id = %s
        """
        rows_affected = db_manager.execute_update(sql, (change, user_id))
        
        if rows_affected == 0:
            return jsonify({'error': 'User not found'}), 404
        
        return jsonify({'message': 'Credit score updated successfully'}), 200
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500
