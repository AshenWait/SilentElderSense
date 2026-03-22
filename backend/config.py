import os

BASE_DIR = os.path.dirname(os.path.abspath(__file__))

DATA_DIR = os.path.join(os.path.dirname(os.path.abspath(__file__)), "data")

class Config:
    SECRET_KEY = 'your-secret-key-here'
    SQLALCHEMY_DATABASE_URI = f'sqlite:///{os.path.join(DATA_DIR, "db.sqlite3")}'
    SQLALCHEMY_TRACK_MODIFICATIONS = False
