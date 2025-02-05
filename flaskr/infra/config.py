import os
from dotenv import load_dotenv

load_dotenv()

class Config:
    # Flask
    SECRET_KEY = os.getenv('SECRET_KEY', 'dev')
    ENV =  os.getenv('ENV', 'default_env')
    DEBUG = os.getenv('DEBUG', 'True').lower() == 'true'
    TESTING = os.getenv('TESTING', 'False').lower() == 'true'
    
    # MongoDB
    MONGO_URI = os.getenv('MONGO_URI', 'mongodb://mongo:27017/task_manager')
    MONGO_DBNAME = os.getenv('MONGO_DBNAME', 'task_manager')
    
    # Redis
    REDIS_URL = os.getenv('REDIS_URL', 'redis://redis:6379/0')
    REDIS_TTL = int(os.getenv('REDIS_TTL', 300))
    
    # Email
    MAIL_SERVER = os.getenv('MAIL_SERVER', 'smtp.gmail.com')
    MAIL_PORT = int(os.getenv('MAIL_PORT', 587))
    MAIL_USE_TLS = os.getenv('MAIL_USE_TLS', 'True').lower() == 'true'
    MAIL_USERNAME = os.getenv('MAIL_USERNAME')
    MAIL_PASSWORD = os.getenv('MAIL_PASSWORD')
    MAIL_DEFAULT_SENDER = os.getenv('MAIL_DEFAULT_SENDER')
    
    # JWT
    JWT_SECRET_KEY = os.getenv('JWT_SECRET_KEY', SECRET_KEY)
    JWT_EXPIRATION = int(os.getenv('JWT_EXPIRATION', 300))
    
    # CORS
    CORS_ORIGINS = os.getenv('CORS_ORIGINS', 'http://localhost:9000').split(',')
