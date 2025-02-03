from prometheus_flask_exporter import PrometheusMetrics
from flask import request, Response
from functools import wraps
import time
from datetime import datetime
from typing import Any, Callable, Dict, Optional, Union, TypeVar, cast
from werkzeug.local import LocalProxy

# Tipo para o decorator
F = TypeVar('F', bound=Callable[..., Any])

# Variável global tipada
metrics: Optional[PrometheusMetrics] = None

# Extensão do tipo Request para incluir atributos dinâmicos
class ExtendedRequest:
    cache_type: str
    task_operation: str
    task_status: str
    status_code: int

# Cast do request para nosso tipo estendido
extended_request = cast(ExtendedRequest, request)

def init_metrics(app) -> PrometheusMetrics:
    global metrics
    metrics = PrometheusMetrics(app)

    # Métricas estáticas
    metrics.info('app_info', 'Application info', version='1.0.0')

    # Métricas por rota com latência
    metrics.register_default(
        metrics.histogram(
            'flask_http_request_duration_seconds',
            'Flask HTTP request duration in seconds',
            labels={
                'path': lambda: cast(LocalProxy, request).path,
                'method': lambda: cast(LocalProxy, request).method
            }
        )
    )

    # Contadores personalizados
    metrics.counter(
        'user_login_total', 'Total number of user logins',
        labels={'status': lambda: 'success' if extended_request.status_code < 400 else 'failed'}
    )
    metrics.counter(
        'user_register_total', 'Total number of user registrations'
    )
    metrics.counter(
        'password_reset_total', 'Total number of password reset requests'
    )

    # Métricas de cache
    metrics.counter(
        'cache_hit_total', 'Total number of cache hits',
        labels={'cache_type': lambda: extended_request.cache_type}
    )
    metrics.counter(
        'cache_miss_total', 'Total number of cache misses',
        labels={'cache_type': lambda: extended_request.cache_type}
    )

    # Métricas específicas para tasks
    metrics.counter(
        'task_operations_total',
        'Total number of task operations',
        labels={
            'operation': lambda: extended_request.task_operation,
            'status': lambda: 'success' if extended_request.status_code < 400 else 'failed'
        }
    )
    
    metrics.gauge(
        'tasks_by_status',
        'Number of tasks by status',
        labels={'status': lambda: extended_request.task_status}
    )

    metrics.histogram(
        'task_age_days',
        'Task age in days',
        buckets=[1, 7, 30, 90, float('inf')]
    )

    return metrics

def track_cache_hit(cache_type: str = 'default') -> None:
    """Incrementa contador de cache hit"""
    if metrics:
        setattr(extended_request, 'cache_type', cache_type)
        metrics.counter('cache_hit_total', 'Total number of cache hits').inc()

def track_cache_miss(cache_type: str = 'default') -> None:
    """Incrementa contador de cache miss"""
    if metrics:
        setattr(extended_request, 'cache_type', cache_type)
        metrics.counter('cache_miss_total', 'Total number of cache misses').inc()

def track_task_operation(operation: str) -> None:
    """Registra operação de task"""
    if metrics:
        setattr(extended_request, 'task_operation', operation)
        metrics.counter('task_operations_total', 'Total number of task operations').inc()

def update_task_status_metrics(status_counts: Dict[str, int]) -> None:
    """Atualiza métricas de status das tasks"""
    if metrics:
        for status, count in status_counts.items():
            setattr(extended_request, 'task_status', status)
            metrics.gauge('tasks_by_status', 'Number of tasks by status').set(count)

def track_task_age(created_date: datetime) -> None:
    """Registra idade da task"""
    if metrics:
        age = (datetime.now() - created_date).days
        metrics.histogram('task_age_days', 'Task age in days').observe(age)

def monitor_endpoint(name: Optional[str] = None) -> Callable[[F], F]:
    """Decorator para monitorar endpoints específicos"""
    def decorator(f: F) -> F:
        endpoint = name or f.__name__
        
        @wraps(f)
        def wrapped(*args: Any, **kwargs: Any) -> Union[Response, tuple[Response, int]]:
            start_time = time.time()
            response = f(*args, **kwargs)
            duration = time.time() - start_time
            
            if metrics:
                metrics.histogram(
                    'endpoint_duration_seconds',
                    'Endpoint execution time in seconds',
                    labels={'endpoint': endpoint}
                ).observe(duration)
                
                status = response[1] if isinstance(response, tuple) else 200
                metrics.counter(
                    'endpoint_calls_total',
                    'Total calls to endpoint',
                    labels={'endpoint': endpoint, 'status': status}
                ).inc()
            
            return response
        return wrapped  # type: ignore
    return decorator 