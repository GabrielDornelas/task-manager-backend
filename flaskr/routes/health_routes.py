from flask import Blueprint, jsonify
from ..infra.db import get_db
from ..infra.redis_client import get_redis

health_bp = Blueprint('health', __name__)

@health_bp.route('/health')
def health_check():
    health_status = {
        'status': 'healthy',
        'checks': {
            'database': check_database(),
            'redis': check_redis(),
            'api': True
        }
    }
    return jsonify(health_status)

def check_database():
    try:
        db = get_db()
        db.command('ping')
        return True
    except:
        return False

def check_redis():
    try:
        redis = get_redis()
        redis.ping()
        return True
    except:
        return False
