from flask import Blueprint, jsonify
from ..models.user import User
from ..models.task import Task
from ..infra.db import get_db
from datetime import datetime, timedelta
import time
from functools import wraps
from ..controllers.auth_controller import login_required


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

@metrics_bp.route('/metrics')
@login_required
def get_metrics():
    """Endpoint para métricas básicas do sistema"""
    db = get_db()
    
    # Active users (logged in in the last 24 hours)
    active_users = User.count_active_users(hours=24)
    
    # Tasks by status
    tasks_by_status = Task.count_by_status()
    
    # Average response time (out of the last 100 requests)
    avg_response_time = 0
    if hasattr(metrics_bp, 'response_times') and metrics_bp.response_times:
        avg_response_time = sum(metrics_bp.response_times) / len(metrics_bp.response_times)
    
    # Error rate (last 24h)
    error_rate = Task.get_error_rate(hours=24)
    
    return jsonify({
        'active_users': active_users,
        'tasks_by_status': tasks_by_status,
        'avg_response_time': round(avg_response_time, 3),
        'error_rate': error_rate,
        'timestamp': datetime.utcnow().isoformat()
    })
