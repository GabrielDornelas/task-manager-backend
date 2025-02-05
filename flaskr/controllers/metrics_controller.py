import time
from functools import wraps

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
