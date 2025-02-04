import os
from flask import Flask
from .infra.config import Config
from .routes.task_routes import task_bp
from .routes.auth_routes import auth_bp
from .routes.health_routes import health_bp
from flask_mail import Mail
from .infra import redis_client
from flask_swagger_ui import get_swaggerui_blueprint
from flask_cors import CORS

def create_app(test_config=None):
    # create and configure the app
    app = Flask(__name__, instance_relative_config=True)
    app.config.from_object(Config)

    # Initialize database
    from .infra import db
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
    
    # Swagger UI
    SWAGGER_URL = '/api/docs'
    API_URL = '/static/swagger.json'
    swagger_bp = get_swaggerui_blueprint(
        SWAGGER_URL,
        API_URL,
        config={'app_name': "Task Manager API"}
    )
    app.register_blueprint(swagger_bp, url_prefix=SWAGGER_URL)
    
    # List as rotas
    # for rule in app.url_map.iter_rules():
    #     print(f"Endpoint: {rule.endpoint}\nURL: {rule.rule}")

    CORS(app, resources={
        r"/auth/*": {"origins": ["http://localhost:3000"]},
        r"/task/*": {"origins": ["http://localhost:3000"]}
    })

    return app
