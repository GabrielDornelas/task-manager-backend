import os
from flask import Flask
from .config import Config
from .routes.task_routes import task_bp
from .routes.auth_routes import auth_bp

def create_app(test_config=None):
    # create and configure the app
    app = Flask(__name__, instance_relative_config=True)
    app.config.from_object(Config)

    # Initialize database
    from . import db
    db.init_app(app)

    # a simple page that says hello
    @app.route('/hello')
    def hello():
        return 'Hello, World!'

    # Register blueprints
    app.register_blueprint(task_bp)
    app.register_blueprint(auth_bp)
    
    # Lista as rotas
    # for rule in app.url_map.iter_rules():
    #     print(f"Endpoint: {rule.endpoint}\nURL: {rule.rule}")
    return app
