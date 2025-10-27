from flask import Flask, request, jsonify
from flask_cors import CORS
import os
import sys
from datetime import datetime

# 添加当前目录到Python路径
sys.path.append(os.path.dirname(__file__))

from db import db_manager
from routes.user_routes import user_bp
from routes.item_routes import item_bp
from routes.order_routes import order_bp
from routes.message_routes import message_bp
from routes.wishlist_routes import wishlist_bp
from routes.address_routes import address_bp

app = Flask(__name__)
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
    print("API文档: http://localhost:5000/")
    print("健康检查: http://localhost:5000/api/health")
    print("=" * 50)

    app.run(debug=True, host='0.0.0.0', port=5000)