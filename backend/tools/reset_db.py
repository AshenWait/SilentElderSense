"""
数据库重建脚本
用于删除旧数据库并重新创建表结构
"""
import os
import sys

# 添加项目根目录到路径
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from config import DATA_DIR
from auth.models import Base, User

DB_NAME = "db.sqlite3"
db_path = os.path.join(DATA_DIR, DB_NAME)

# 确保 data 目录存在
os.makedirs(DATA_DIR, exist_ok=True)

# 删除旧数据库
if os.path.exists(db_path):
    os.remove(db_path)
    print(f"已删除旧数据库: {db_path}")
else:
    print(f"数据库不存在，跳过删除")

# 创建引擎并建表
engine = create_engine(f"sqlite:///{db_path}")
Base.metadata.create_all(engine)
print(f"已创建新表: {db_path}")

# 创建默认管理员
Session = sessionmaker(bind=engine)
db = Session()

admin = User(
    username='admin',
    email='admin@example.com',
    is_admin=True
)
admin.set_password('123456')
db.add(admin)
db.commit()
print("已创建默认管理员: admin / 123456")

db.close()
print("数据库重建完成")