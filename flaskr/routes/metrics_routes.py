from flask import Blueprint, jsonify
from ..models.user import User
from ..models.task import Task
from ..infra.db import get_db
from datetime import datetime, timedelta
import time
from functools import wraps

metrics_bp = Blueprint('metrics', __name__)

# Decorator para medir tempo de resposta
def measure_time():
    def decorator(f):
        @wraps(f)
        def wrapper(*args, **kwargs):
            start = time.time()
            result = f(*args, **kwargs)
            end = time.time()
            
            # Armazenar tempo no contexto da aplicação
            if not hasattr(metrics_bp, 'response_times'):
                metrics_bp.response_times = []
            metrics_bp.response_times.append(end - start)
            # Manter apenas os últimos 100 tempos
            metrics_bp.response_times = metrics_bp.response_times[-100:]
            
            return result
        return wrapper
    return decorator

@metrics_bp.route('/metrics')
def get_metrics():
    """Endpoint para métricas básicas do sistema"""
    db = get_db()
    
    # Usuários ativos (logados nas últimas 24h)
    active_users = User.count_active_users(hours=24)
    
    # Tasks por status
    tasks_by_status = Task.count_by_status()
    
    # Tempo médio de resposta (dos últimos 100 requests)
    avg_response_time = 0
    if hasattr(metrics_bp, 'response_times') and metrics_bp.response_times:
        avg_response_time = sum(metrics_bp.response_times) / len(metrics_bp.response_times)
    
    # Taxa de erros (últimas 24h)
    error_rate = Task.get_error_rate(hours=24)
    
    return jsonify({
        'active_users': active_users,
        'tasks_by_status': tasks_by_status,
        'avg_response_time': round(avg_response_time, 3),
        'error_rate': error_rate,
        'timestamp': datetime.utcnow().isoformat()
    }) 