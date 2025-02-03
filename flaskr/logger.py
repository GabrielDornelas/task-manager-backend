import logging
import json
from datetime import datetime
from flask import request, g

class StructuredLogger:
    def __init__(self, app):
        self.logger = logging.getLogger('task_manager')
        self.logger.setLevel(logging.INFO)
        
        handler = logging.StreamHandler()
        handler.setFormatter(logging.Formatter('%(message)s'))
        self.logger.addHandler(handler)
        
        @app.before_request
        def before_request():
            g.start_time = datetime.now()
        
        @app.after_request
        def after_request(response):
            if hasattr(g, 'start_time'):
                duration = (datetime.now() - g.start_time).total_seconds()
                
                log_data = {
                    'timestamp': datetime.now().isoformat(),
                    'method': request.method,
                    'path': request.path,
                    'status': response.status_code,
                    'duration': duration,
                    'ip': request.remote_addr,
                    'user_id': str(g.user._id) if hasattr(g, 'user') else None
                }
                
                self.logger.info(json.dumps(log_data))
            
            return response 