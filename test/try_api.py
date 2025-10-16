import pymysql
import os
import configparser

# 读取配置文件
config = configparser.ConfigParser()
config_path = os.path.join(os.path.dirname(os.path.dirname(__file__)), 'config.ini')
config.read(config_path, encoding='utf-8')

# 配置数据库连接参数
instance_ip = config.get('database', 'host')
instance_port = config.getint('database', 'port')
database_name = config.get('database', 'database')
username = config.get('database', 'username')
password = config.get('database', 'password')

# SSL 配置（使用 CA Bundle 验证服务器证书）
ssl_config = {
    'ca': os.path.join(os.path.dirname(os.path.dirname(__file__)), config.get('ssl', 'ca_file')),
    'check_hostname': config.getboolean('ssl', 'check_hostname')
}

conn = None
try:
    # 建立数据库连接
    conn = pymysql.connect(
        host=instance_ip,
        port=instance_port,
        user=username,
        password=password,
        database=database_name,
        ssl=ssl_config,
        charset='utf8mb4'
    )

    print("Database connected (SSL with CA verification)")

    with conn.cursor() as cursor:
        # 测试连接 - 获取数据库版本
        cursor.execute("SELECT VERSION();")
        db_version = cursor.fetchone()
        print(f"GaussDB Version: {db_version[0]}")
        
        # 查看当前数据库中的表
        cursor.execute("SHOW TABLES;")
        tables = cursor.fetchall()
        print(f"\nTables in database:")
        
        if tables:
            for table in tables:
                print(f"  - {table[0]}")
            
            # 如果有表，查询第一个表的数据
            first_table = tables[0][0]
            sql = f"SELECT * FROM {first_table} LIMIT 5"
            cursor.execute(sql)
            
            # 获取并打印结果
            results = cursor.fetchall()
            print(f"\nFetching data from {first_table}:")
            if results:
                for row in results:
                    print(row)
            else:
                print("  No data found in table.")
        else:
            print("  No tables found in database.")

except pymysql.Error as e:
    print(f"Database connection error: {e}")
except Exception as e:
    print(f"Unexpected error: {e}")
finally:
    # 关闭数据库连接
    if conn and conn.open:
        conn.close()
        print("Database connection closed")