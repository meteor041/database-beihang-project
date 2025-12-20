from flask import Flask, request, jsonify
from flask.json.provider import DefaultJSONProvider
from flask_cors import CORS
import os
import sys
import threading
import time
from datetime import datetime, date
from decimal import Decimal

# 添加当前目录到Python路径
sys.path.append(os.path.dirname(__file__))

from db import db_manager
from routes.user_routes import user_bp
from routes.item_routes import item_bp
from routes.order_routes import order_bp
from routes.message_routes import message_bp
from routes.wishlist_routes import wishlist_bp
from routes.address_routes import address_bp
from routes.review_routes import review_bp
from routes.upload_routes import upload_bp

# ============================================
# 订单超时自动取消任务
# ============================================
ORDER_TIMEOUT_MINUTES = 60  # 1小时未支付自动取消
CHECK_INTERVAL_SECONDS = 300  # 每5分钟检查一次

def cancel_timeout_orders():
    """取消超时未支付的订单"""
    try:
        # 查找超时订单
        find_sql = """
        SELECT order_id, item_id, buyer_id, order_number
        FROM `order`
        WHERE order_status = 'pending_payment'
          AND TIMESTAMPDIFF(MINUTE, create_time, NOW()) > %s
        """
        timeout_orders = db_manager.execute_query(find_sql, (ORDER_TIMEOUT_MINUTES,))

        if not timeout_orders:
            return 0

        cancelled_count = 0
        for order in timeout_orders:
            try:
                # 更新订单状态为已取消
                update_order_sql = """
                UPDATE `order`
                SET order_status = 'cancelled',
                    notes = CONCAT(IFNULL(notes, ''), ' [系统自动取消：超时未支付]')
                WHERE order_id = %s AND order_status = 'pending_payment'
                """
                rows = db_manager.execute_update(update_order_sql, (order['order_id'],))

                if rows > 0:
                    # 恢复商品状态
                    restore_item_sql = """
                    UPDATE item SET status = 'available' WHERE item_id = %s
                    """
                    db_manager.execute_update(restore_item_sql, (order['item_id'],))
                    cancelled_count += 1
                    print(f"[订单超时] 已取消订单 {order['order_number']}")

            except Exception as e:
                print(f"[订单超时] 取消订单 {order['order_id']} 失败: {e}")

        return cancelled_count

    except Exception as e:
        print(f"[订单超时] 检查超时订单失败: {e}")
        return 0


def order_timeout_checker():
    """后台线程：定期检查超时订单"""
    while True:
        time.sleep(CHECK_INTERVAL_SECONDS)
        try:
            cancelled = cancel_timeout_orders()
            if cancelled > 0:
                print(f"[订单超时] 本次共取消 {cancelled} 个超时订单")
        except Exception as e:
            print(f"[订单超时] 检查任务异常: {e}")


# 自定义JSON编码器，统一处理datetime格式
class CustomJSONProvider(DefaultJSONProvider):
    def default(self, obj):
        if isinstance(obj, datetime):
            # 返回ISO格式字符串，不带时区（假设服务器和客户端在同一时区）
            return obj.strftime('%Y-%m-%d %H:%M:%S')
        if isinstance(obj, date):
            return obj.strftime('%Y-%m-%d')
        if isinstance(obj, Decimal):
            return float(obj)
        return super().default(obj)

app = Flask(__name__)
app.json = CustomJSONProvider(app)  # 使用自定义JSON编码器
app.config['JSON_AS_ASCII'] = False  # 支持中文字符
app.config['MAX_CONTENT_LENGTH'] = 60 * 1024 * 1024  # 允许最多约60MB上传（9*5MB + 余量）

# 配置CORS,允许所有来源(开发环境)
CORS(app,
     origins=['http://localhost:3001', 'http://localhost:5173', 'http://127.0.0.1:3001', 'http://127.0.0.1:5173'],
     supports_credentials=True,
     allow_headers=['Content-Type', 'Authorization'],
     methods=['GET', 'POST', 'PUT', 'DELETE', 'OPTIONS'])

# 注册蓝图
app.register_blueprint(user_bp, url_prefix='/api/users')
app.register_blueprint(item_bp, url_prefix='/api/items')
app.register_blueprint(order_bp, url_prefix='/api/orders')
app.register_blueprint(message_bp, url_prefix='/api/messages')
app.register_blueprint(wishlist_bp, url_prefix='/api/wishlist')
app.register_blueprint(address_bp, url_prefix='/api/addresses')
app.register_blueprint(review_bp, url_prefix='/api/reviews')
app.register_blueprint(upload_bp, url_prefix='/api/uploads')

@app.route('/')
def index():
    return jsonify({
        'message': '校内二手物品交易平台API',
        'version': '1.0',
        'status': 'running'
    })

@app.route('/api/health')
def health_check():
    """健康检查接口"""
    try:
        # 测试数据库连接
        result = db_manager.execute_query("SELECT 1")
        return jsonify({
            'status': 'healthy',
            'database': 'connected',
            'timestamp': str(datetime.now())
        })
    except Exception as e:
        return jsonify({
            'status': 'unhealthy',
            'database': 'disconnected',
            'error': str(e),
            'timestamp': str(datetime.now())
        }), 500

@app.errorhandler(404)
def not_found(error):
    return jsonify({'error': 'API endpoint not found'}), 404

@app.errorhandler(500)
def internal_error(error):
    return jsonify({'error': 'Internal server error'}), 500

# 手动触发超时订单检查的API（用于测试或管理）
@app.route('/api/admin/cancel-timeout-orders', methods=['POST'])
def trigger_cancel_timeout_orders():
    """手动触发超时订单取消"""
    try:
        cancelled = cancel_timeout_orders()
        return jsonify({
            'message': f'成功取消 {cancelled} 个超时订单',
            'cancelled_count': cancelled
        })
    except Exception as e:
        return jsonify({'error': str(e)}), 500

# 获取超时订单列表的API
@app.route('/api/admin/timeout-orders', methods=['GET'])
def get_timeout_orders():
    """获取超时未支付的订单列表"""
    try:
        timeout_minutes = request.args.get('timeout', ORDER_TIMEOUT_MINUTES, type=int)
        sql = """
        SELECT
            o.order_id,
            o.order_number,
            o.buyer_id,
            o.seller_id,
            o.item_id,
            o.total_amount,
            o.create_time,
            TIMESTAMPDIFF(MINUTE, o.create_time, NOW()) as minutes_elapsed,
            buyer.username as buyer_name,
            seller.username as seller_name,
            i.title as item_title
        FROM `order` o
        JOIN user buyer ON o.buyer_id = buyer.user_id
        JOIN user seller ON o.seller_id = seller.user_id
        JOIN item i ON o.item_id = i.item_id
        WHERE o.order_status = 'pending_payment'
          AND TIMESTAMPDIFF(MINUTE, o.create_time, NOW()) > %s
        """
        orders = db_manager.execute_query(sql, (timeout_minutes,))
        return jsonify({
            'timeout_orders': orders,
            'count': len(orders),
            'timeout_minutes': timeout_minutes
        })
    except Exception as e:
        return jsonify({'error': str(e)}), 500

if __name__ == '__main__':
    from datetime import datetime
    print("=" * 50)
    print("校内二手物品交易平台后端服务")
    print("=" * 50)
    print(f"启动时间: {datetime.now()}")
    print("API文档: http://localhost:5001/")
    print("健康检查: http://localhost:5001/api/health")
    print(f"订单超时设置: {ORDER_TIMEOUT_MINUTES} 分钟 ({ORDER_TIMEOUT_MINUTES // 60} 小时)")
    print(f"超时检查间隔: {CHECK_INTERVAL_SECONDS} 秒 ({CHECK_INTERVAL_SECONDS // 60} 分钟)")
    print("=" * 50)

    # 启动后台超时订单检查线程
    timeout_thread = threading.Thread(target=order_timeout_checker, daemon=True)
    timeout_thread.start()
    print("[订单超时] 后台检查任务已启动")

    app.run(debug=True, host='0.0.0.0', port=5001)
