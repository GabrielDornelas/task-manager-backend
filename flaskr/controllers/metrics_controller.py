import time
from functools import wraps
from flask import jsonify
from ..models.user import User
from ..models.task import Task
from ..infra.db import get_db
from datetime import datetime
from flask import Blueprint

metrics_bp = Blueprint('metrics', __name__)

# Decorator to measure response time
def measure_time():
    def decorator(f):
        @wraps(f)
        def wrapper(*args, **kwargs):
            start = time.time()
            result = f(*args, **kwargs)
            end = time.time()
            
            # Store time in the context of the application
            if not hasattr(metrics_bp, 'response_times'):
                metrics_bp.response_times = []
            metrics_bp.response_times.append(end - start)
            # Keep only the last 100 times
            metrics_bp.response_times = metrics_bp.response_times[-100:]
            
            return result
        return wrapper
    return decorator


@measure_time()
def get_metrics():
    """Endpoint for basic system metrics"""
    db = get_db()

    # Active users (logged in in the last 24 hours)
    active_users = User.count_active_users(hours=24)

    # Tasks by status
    tasks_by_status = Task.count_by_status()

    # Average response time (out of the last 100 requests)
    avg_response_time = 0
    if hasattr(metrics_bp, 'response_times') and metrics_bp.response_times:
        avg_response_time = sum(metrics_bp.response_times) / len(metrics_bp.response_times)

    return jsonify({
        'active_users': active_users,
        'tasks_by_status': tasks_by_status,
        'avg_response_time': round(avg_response_time, 3),
        'timestamp': datetime.utcnow().isoformat()
    })
