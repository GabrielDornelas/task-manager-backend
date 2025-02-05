from flask import Blueprint, jsonify
from ..models.user import User
from ..models.task import Task
from ..infra.db import get_db
from datetime import datetime
from ..controllers.auth_controller import login_required
from ..controllers.metrics_controller import measure_time


metrics_bp = Blueprint('metrics', __name__)

@metrics_bp.route('/metrics')
@login_required
@measure_time()
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
