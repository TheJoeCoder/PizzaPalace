from flask import Flask
from flask_appconfig import AppConfig
from flask_bootstrap import Bootstrap

from .frontend import frontend
from .nav import nav


def create_app(configfile=None):
    app = Flask(__name__)

    # Flask-Appconfig
    AppConfig(app)

    # Install Bootstrap
    Bootstrap(app)

    # Register blueprints
    app.register_blueprint(frontend)

    # Disable CDN Support
    app.config['BOOTSTRAP_SERVE_LOCAL'] = True

    # Init navigation
    nav.init_app(app)

    return app