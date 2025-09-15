import os
from dotenv import load_dotenv
from datetime import datetime, timedelta

basedir = os.path.abspath(os.path.dirname(__file__))
load_dotenv(os.path.join(basedir, '.env'))

class Config:
    SECRET_KEY = os.environ.get('SECRET_KEY') or 'you-will-never-guess'
    SQLALCHEMY_DATABASE_URI = os.environ.get('DATABASE_URL') or \
        'sqlite:///' + os.path.join(basedir, 'app.db')
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    
    # 启用SQLite多线程支持
    SQLALCHEMY_ENGINE_OPTIONS = {
        'connect_args': {
            'check_same_thread': False  # 允许SQLite在多线程中使用
        }
    }
    
    ADMIN_USERNAME = os.environ.get('ADMIN_USERNAME') or 'admin'
    ADMIN_EMAIL = os.environ.get('ADMIN_EMAIL') or 'admin@example.com'
    ADMIN_PASSWORD = os.environ.get('ADMIN_PASSWORD') or 'admin123'
    INVITATION_CODE_LENGTH = 8
    
    # 设置 session 有效期为 30 天
    PERMANENT_SESSION_LIFETIME = timedelta(days=30)
    
    # CSRF令牌配置
    WTF_CSRF_TIME_LIMIT = 24 * 60 * 60  # CSRF令牌有效期24小时（秒）
    WTF_CSRF_SSL_STRICT = False  # 不强制要求HTTPS 
    
    # URL配置 - 用于解决代理服务器端口显示问题
    PREFERRED_URL_SCHEME = os.environ.get('PREFERRED_URL_SCHEME') or 'https'
    SERVER_NAME = os.environ.get('SERVER_NAME')  # 例如: 'www.twoleaf.cn' 