from sqlalchemy import create_engine, Column, Integer, String, DateTime, Boolean
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
from datetime import datetime
import bcrypt
from enum import Enum

Base = declarative_base()


class UserRole(Enum):
    """用户角色"""
    ADMIN = 'admin'           # 管理员
    FAMILY = 'family'         # 家属/监护人
    VISITOR = 'visitor'       # 访客


class User(Base):
    __tablename__ = 'users'

    id = Column(Integer, primary_key=True)
    username = Column(String(80), unique=True, nullable=False)
    email = Column(String(120), unique=True, nullable=False)
    password_hash = Column(String(128), nullable=False)
    role = Column(String(16), default='family')  # admin, family, visitor
    is_active = Column(Boolean, default=True)
    created_at = Column(DateTime, default=datetime.utcnow)

    def set_password(self, password):
        """密码加密"""
        self.password_hash = bcrypt.hashpw(password.encode(), bcrypt.gensalt()).decode()

    def check_password(self, password):
        """验证密码"""
        return bcrypt.checkpw(password.encode(), self.password_hash.encode())

    @property
    def is_admin(self):
        return self.role == 'admin'

    @property
    def is_family(self):
        return self.role == 'family'

    @property
    def is_visitor(self):
        return self.role == 'visitor'

    def to_dict(self):
        return {
            'id': self.id,
            'username': self.username,
            'email': self.email,
            'role': self.role,
            'is_active': self.is_active,
            'created_at': self.created_at.isoformat() if self.created_at else None
        }


# 数据库引擎和会话
engine = None
SessionLocal = None


def init_db(app):
    global engine, SessionLocal
    database_url = app.config['SQLALCHEMY_DATABASE_URI']
    engine = create_engine(database_url, echo=True)
    SessionLocal = sessionmaker(bind=engine)
    Base.metadata.create_all(engine)


def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()