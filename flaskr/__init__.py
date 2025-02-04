from gevent import monkey
monkey.patch_all()

import os
from flask import Flask
from .infra.config import Config
from .routes.task_routes import task_bp
from .routes.auth_routes import auth_bp
from .routes.health_routes import health_bp
from .routes.metrics_routes import metrics_bp
from flask_mail import Mail
from .infra import redis_client, db
from flask_swagger_ui import get_swaggerui_blueprint
from flask_cors import CORS

def create_app(test_config=None):
    # create and configure the app
    app = Flask(__name__, instance_relative_config=True)
    app.config.from_object(Config)

    # Configuração CORS
    app.config['CORS_HEADERS'] = 'Content-Type'
    CORS(app, 
         resources={r"/*": {
             "origins": ["http://localhost:8080"],
             "methods": ["GET", "POST", "PUT", "DELETE", "OPTIONS"],
             "allow_headers": [
                 "Content-Type", 
                 "Authorization",
                 "Cache-Control",
                 "Pragma"
             ],
             "supports_credentials": True
         }})

    # Initialize database
    db.init_app(app)

    # Initialize Redis
    redis_client.init_redis(app)

    # Initialize Flask-Mail
    Mail(app)

    # a simple page that says hello
    @app.route('/hello')
    def hello():
        return 'Hello, World!'

    # Register blueprints
    app.register_blueprint(task_bp)
    app.register_blueprint(auth_bp)
    app.register_blueprint(health_bp)
    app.register_blueprint(metrics_bp)
    
    # Swagger UI
    SWAGGER_URL = '/api/docs'
    API_URL = '/static/swagger.json'
    swagger_bp = get_swaggerui_blueprint(
        SWAGGER_URL,
        API_URL,
        config={'app_name': "Task Manager API"}
    )
    app.register_blueprint(swagger_bp, url_prefix=SWAGGER_URL)

    return app
