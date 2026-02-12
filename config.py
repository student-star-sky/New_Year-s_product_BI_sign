import os

class Config:
    BASE_DIR = os.path.abspath(os.path.dirname(__file__))
    SECRET_KEY = os.environ.get('SECRET_KEY') or 'dev-secret-key-change-in-production' # 使用默认值 用于加密会话
    SQLALCHEMY_DATABASE_URI = 'sqlite:///'+os.path.join(BASE_DIR, 'utils_file', 'app.db') # 配置 sqlite3 数据库
    SQLALCHEMY_TRACK_MODIFICATIONS = False                                             # 关闭 orm 的跟踪修改
    JWT_SECRET_KEY = os.environ.get('JWT_SECRET_KEY') or 'jwt-secret-key-change-in-production'  # 使用默认密钥
    # 日志配置
    LOG_LEVEL = os.environ.get('LOG_LEVEL', 'INFO')  # 日志级别
    LOG_FILE = os.environ.get('LOG_FILE', 'logs/app.log')  # 日志文件路径
    LOG_MAX_BYTES = 5242880  # 单个日志文件最大字节 (5MB)
    LOG_BACKUP_COUNT = 5  # 保留的备份文件数
