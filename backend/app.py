from flask import Flask, request, jsonify
from flask.json.provider import DefaultJSONProvider
from flask_cors import CORS
import os
import sys
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

if __name__ == '__main__':
    from datetime import datetime
    print("=" * 50)
    print("校内二手物品交易平台后端服务")
    print("=" * 50)
    print(f"启动时间: {datetime.now()}")
    print("API文档: http://localhost:5001/")
    print("健康检查: http://localhost:5001/api/health")
    print("=" * 50)

    app.run(debug=True, host='0.0.0.0', port=5001)
