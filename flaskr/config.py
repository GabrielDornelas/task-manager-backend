import os
from dotenv import load_dotenv

load_dotenv()

class Config:
    SECRET_KEY = os.getenv('SECRET_KEY', 'dev')
    ENV =  os.getenv('ENV', 'default_env')
    REDIS_URL = os.getenv('REDIS_URI', 'redis://redis:6379/0')
    MONGO_URI = os.getenv('MONGO_URI', 'mongodb://mongo:27017/taskmanager')
    MONGO_DBNAME = os.getenv('MONGO_DBNAME', 'mydatabase')
