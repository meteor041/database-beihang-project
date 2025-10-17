import pymysql
import os
import configparser
from contextlib import contextmanager
import hashlib
import uuid
from datetime import datetime

class DatabaseManager:
    def __init__(self):
        self.config = configparser.ConfigParser()
        config_path = os.path.join(os.path.dirname(os.path.dirname(__file__)), 'config.ini')
        self.config.read(config_path, encoding='utf-8')
        
        # 数据库连接参数
        self.host = self.config.get('database', 'host')
        self.port = self.config.getint('database', 'port')
        self.database = self.config.get('database', 'database')
        self.username = self.config.get('database', 'username')
        self.password = self.config.get('database', 'password')
        
        # SSL配置
        self.ssl_config = {
            'ca': os.path.join(os.path.dirname(os.path.dirname(__file__)), 
                              self.config.get('ssl', 'ca_file')),
            'check_hostname': self.config.getboolean('ssl', 'check_hostname')
        }

    @contextmanager
    def get_connection(self):
        """获取数据库连接的上下文管理器"""
        conn = None
        try:
            conn = pymysql.connect(
                host=self.host,
                port=self.port,
                user=self.username,
                password=self.password,
                database=self.database,
                ssl=self.ssl_config,
                charset='utf8mb4',
                cursorclass=pymysql.cursors.DictCursor
            )
            yield conn
        except Exception as e:
            if conn:
                conn.rollback()
            raise e
        finally:
            if conn:
                conn.close()

    def execute_query(self, sql, params=None):
        """执行查询语句"""
        with self.get_connection() as conn:
            with conn.cursor() as cursor:
                cursor.execute(sql, params)
                return cursor.fetchall()

    def execute_update(self, sql, params=None):
        """执行更新语句"""
        with self.get_connection() as conn:
            with conn.cursor() as cursor:
                cursor.execute(sql, params)
                conn.commit()
                return cursor.rowcount

    def execute_insert(self, sql, params=None):
        """执行插入语句并返回插入的ID"""
        with self.get_connection() as conn:
            with conn.cursor() as cursor:
                cursor.execute(sql, params)
                conn.commit()
                return cursor.lastrowid

    @staticmethod
    def hash_password(password):
        """密码加密"""
        return hashlib.sha256(password.encode()).hexdigest()

    @staticmethod
    def generate_order_number():
        """生成32位订单号"""
        return str(uuid.uuid4()).replace('-', '')

# 全局数据库管理器实例
db_manager = DatabaseManager()