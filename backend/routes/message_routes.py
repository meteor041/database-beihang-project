from flask import Blueprint, request, jsonify
from datetime import datetime
import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(__file__)))
from db import db_manager

message_bp = Blueprint('message', __name__)

@message_bp.route('/', methods=['POST'])
def send_message():
    """消息发送 - INSERT操作"""
    try:
        data = request.get_json()
        
        # 验证必填字段
        required_fields = ['sender_id', 'receiver_id', 'item_id', 'content']
        for field in required_fields:
            if not data.get(field):
                return jsonify({'error': f'{field} is required'}), 400
        
        sender_id = data['sender_id']
        receiver_id = data['receiver_id']
        item_id = data['item_id']
        content = data['content']
        message_type = data.get('message_type', 'text')
        reply_to = data.get('reply_to')
        
        # 验证不能给自己发消息
        if sender_id == receiver_id:
            return jsonify({'error': 'Cannot send message to yourself'}), 400
        
        # 验证消息内容长度
        if len(content) > 500:
            return jsonify({'error': 'Message content must be less than 500 characters'}), 400
        
        # 验证商品是否存在
        item_check_sql = "SELECT item_id FROM item WHERE item_id = %s"
        item_result = db_manager.execute_query(item_check_sql, (item_id,))
        if not item_result:
            return jsonify({'error': 'Item not found'}), 404
        
        # 验证接收者是否存在
        user_check_sql = "SELECT user_id FROM user WHERE user_id = %s AND status = 'active'"
        user_result = db_manager.execute_query(user_check_sql, (receiver_id,))
        if not user_result:
            return jsonify({'error': 'Receiver not found or inactive'}), 404
        
        # 插入消息
        insert_sql = """
        INSERT INTO message (sender_id, receiver_id, item_id, content, message_type, reply_to)
        VALUES (%s, %s, %s, %s, %s, %s)
        """
        
        message_id = db_manager.execute_insert(insert_sql, (
            sender_id, receiver_id, item_id, content, message_type, reply_to
        ))
        
        return jsonify({
            'message': 'Message sent successfully',
            'message_id': message_id
        }), 201
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@message_bp.route('/conversations/<int:user_id>', methods=['GET'])
def get_conversations(user_id):
    """获取用户的会话列表"""
    try:
        sql = """
        SELECT 
            CASE 
                WHEN m.sender_id = %s THEN m.receiver_id 
                ELSE m.sender_id 
            END as other_user_id,
            u.username as other_username,
            u.avatar as other_avatar,
            m.item_id,
            i.title as item_title,
            i.images as item_images,
            MAX(m.send_time) as last_message_time,
            (SELECT content FROM message m2 
             WHERE ((m2.sender_id = %s AND m2.receiver_id = other_user_id) OR 
                    (m2.sender_id = other_user_id AND m2.receiver_id = %s))
               AND m2.item_id = m.item_id
             ORDER BY m2.send_time DESC LIMIT 1) as last_message,
            COUNT(CASE WHEN m.receiver_id = %s AND m.is_read = FALSE THEN 1 END) as unread_count
        FROM message m
        JOIN user u ON (CASE WHEN m.sender_id = %s THEN m.receiver_id ELSE m.sender_id END) = u.user_id
        JOIN item i ON m.item_id = i.item_id
        WHERE m.sender_id = %s OR m.receiver_id = %s
        GROUP BY other_user_id, m.item_id, u.username, u.avatar, i.title, i.images
        ORDER BY last_message_time DESC
        """
        
        conversations = db_manager.execute_query(sql, (user_id, user_id, user_id, user_id, user_id, user_id, user_id))
        
        # 处理图片JSON
        for conv in conversations:
            if conv['item_images']:
                import json
                conv['item_images'] = json.loads(conv['item_images'])
            else:
                conv['item_images'] = []
        
        return jsonify({'conversations': conversations}), 200
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@message_bp.route('/conversation', methods=['GET'])
def get_conversation_messages():
    """获取具体会话的消息列表"""
    try:
        user_id = request.args.get('user_id')
        other_user_id = request.args.get('other_user_id')
        item_id = request.args.get('item_id')
        page = int(request.args.get('page', 1))
        limit = int(request.args.get('limit', 50))
        
        if not all([user_id, other_user_id, item_id]):
            return jsonify({'error': 'user_id, other_user_id and item_id are required'}), 400
        
        offset = (page - 1) * limit
        
        sql = """
        SELECT m.message_id, m.sender_id, m.receiver_id, m.content, m.message_type,
               m.send_time, m.is_read, m.reply_to,
               u.username as sender_name, u.avatar as sender_avatar
        FROM message m
        JOIN user u ON m.sender_id = u.user_id
        WHERE ((m.sender_id = %s AND m.receiver_id = %s) OR 
               (m.sender_id = %s AND m.receiver_id = %s))
          AND m.item_id = %s
        ORDER BY m.send_time DESC
        LIMIT %s OFFSET %s
        """
        
        messages = db_manager.execute_query(sql, (
            user_id, other_user_id, other_user_id, user_id, item_id, limit, offset
        ))
        
        # 标记消息为已读
        mark_read_sql = """
        UPDATE message 
        SET is_read = TRUE 
        WHERE receiver_id = %s AND sender_id = %s AND item_id = %s AND is_read = FALSE
        """
        db_manager.execute_update(mark_read_sql, (user_id, other_user_id, item_id))
        
        return jsonify({'messages': messages}), 200
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@message_bp.route('/<int:message_id>/read', methods=['PUT'])
def mark_message_read(message_id):
    """标记消息为已读"""
    try:
        data = request.get_json()
        user_id = data.get('user_id')
        
        if not user_id:
            return jsonify({'error': 'user_id is required'}), 400
        
        # 验证是否为消息接收者
        check_sql = "SELECT receiver_id FROM message WHERE message_id = %s"
        result = db_manager.execute_query(check_sql, (message_id,))
        
        if not result:
            return jsonify({'error': 'Message not found'}), 404
        
        if result[0]['receiver_id'] != user_id:
            return jsonify({'error': 'Permission denied'}), 403
        
        # 标记为已读
        update_sql = "UPDATE message SET is_read = TRUE WHERE message_id = %s"
        db_manager.execute_update(update_sql, (message_id,))
        
        return jsonify({'message': 'Message marked as read'}), 200
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@message_bp.route('/unread/<int:user_id>', methods=['GET'])
def get_unread_count(user_id):
    """获取未读消息数量"""
    try:
        sql = """
        SELECT COUNT(*) as unread_count
        FROM message 
        WHERE receiver_id = %s AND is_read = FALSE
        """
        
        result = db_manager.execute_query(sql, (user_id,))
        unread_count = result[0]['unread_count'] if result else 0
        
        return jsonify({'unread_count': unread_count}), 200
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@message_bp.route('/search', methods=['GET'])
def search_messages():
    """搜索消息"""
    try:
        user_id = request.args.get('user_id')
        keyword = request.args.get('keyword', '')
        item_id = request.args.get('item_id')
        
        if not user_id:
            return jsonify({'error': 'user_id is required'}), 400
        
        # 构建WHERE条件
        where_conditions = ["(m.sender_id = %s OR m.receiver_id = %s)"]
        params = [user_id, user_id]
        
        if keyword:
            where_conditions.append("m.content LIKE %s")
            params.append(f"%{keyword}%")
        
        if item_id:
            where_conditions.append("m.item_id = %s")
            params.append(item_id)
        
        where_clause = " AND ".join(where_conditions)
        
        sql = f"""
        SELECT m.message_id, m.sender_id, m.receiver_id, m.content, m.send_time,
               m.item_id, i.title as item_title,
               sender.username as sender_name,
               receiver.username as receiver_name
        FROM message m
        JOIN user sender ON m.sender_id = sender.user_id
        JOIN user receiver ON m.receiver_id = receiver.user_id
        JOIN item i ON m.item_id = i.item_id
        WHERE {where_clause}
        ORDER BY m.send_time DESC
        LIMIT 100
        """
        
        messages = db_manager.execute_query(sql, params)
        
        return jsonify({'messages': messages}), 200
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@message_bp.route('/<int:message_id>', methods=['DELETE'])
def delete_message(message_id):
    """删除消息（仅发送者可删除）"""
    try:
        data = request.get_json()
        user_id = data.get('user_id')
        
        if not user_id:
            return jsonify({'error': 'user_id is required'}), 400
        
        # 验证是否为消息发送者
        check_sql = "SELECT sender_id, send_time FROM message WHERE message_id = %s"
        result = db_manager.execute_query(check_sql, (message_id,))
        
        if not result:
            return jsonify({'error': 'Message not found'}), 404
        
        message = result[0]
        
        if message['sender_id'] != user_id:
            return jsonify({'error': 'Permission denied'}), 403
        
        # 检查是否在2分钟内（撤回时间限制）
        send_time = message['send_time']
        time_diff = datetime.now() - send_time
        if time_diff.total_seconds() > 120:  # 2分钟
            return jsonify({'error': 'Message can only be deleted within 2 minutes'}), 400
        
        # 删除消息
        delete_sql = "DELETE FROM message WHERE message_id = %s"
        db_manager.execute_update(delete_sql, (message_id,))
        
        return jsonify({'message': 'Message deleted successfully'}), 200
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@message_bp.route('/batch-read', methods=['PUT'])
def batch_mark_read():
    """批量标记消息为已读"""
    try:
        data = request.get_json()
        user_id = data.get('user_id')
        other_user_id = data.get('other_user_id')
        item_id = data.get('item_id')
        
        if not all([user_id, other_user_id, item_id]):
            return jsonify({'error': 'user_id, other_user_id and item_id are required'}), 400
        
        # 批量标记为已读
        sql = """
        UPDATE message 
        SET is_read = TRUE 
        WHERE receiver_id = %s AND sender_id = %s AND item_id = %s AND is_read = FALSE
        """
        
        rows_affected = db_manager.execute_update(sql, (user_id, other_user_id, item_id))
        
        return jsonify({
            'message': 'Messages marked as read',
            'count': rows_affected
        }), 200
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500