import os
from flask import Flask
from .config import Config
from .routes.task_routes import task_bp

def create_app(test_config=None):
    # create and configure the app
    app = Flask(__name__, instance_relative_config=True)
    app.config.from_object(Config)

    # ensure the instance folder exists
    try:
        os.makedirs(app.instance_path)
    except OSError:
        pass

    # Initialize database
    from . import db
    db.init_app(app)

    # Register blueprints
    from . import auth
    app.register_blueprint(auth.bp)
    
    app.register_blueprint(task_bp)
    
    # a simple page that says hello
    @app.route('/hello')
    def hello():
        return 'Hello, World!'
    # for rule in app.url_map.iter_rules():
    #     print(f"Endpoint: {rule.endpoint}\nURL: {rule.rule}")
    return app
