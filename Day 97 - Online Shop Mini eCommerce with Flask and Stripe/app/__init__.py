import os
import stripe
from flask import Flask, session
from flask_sqlalchemy import SQLAlchemy
from flask_bcrypt import Bcrypt
from flask_login import LoginManager
from flask_mail import Mail
from config import config

db = SQLAlchemy()
bcrypt = Bcrypt()
login_manager = LoginManager()
mail = Mail()

login_manager.login_view = 'auth.login'
login_manager.login_message = 'Por favor, faça login para acessar esta página.'
login_manager.login_message_category = 'info'


def create_app(config_name='default'):
    """
    Fábrica de Aplicação (Application Factory)
    """
    app = Flask(__name__)

    app.config.from_object(config[config_name])

    stripe.api_key = app.config['STRIPE_SECRET_KEY']

    db.init_app(app)
    bcrypt.init_app(app)
    login_manager.init_app(app)
    mail.init_app(app)

    from app.main.routes import main_bp
    app.register_blueprint(main_bp)

    from app.auth.routes import auth_bp
    app.register_blueprint(auth_bp)

    from app.admin.routes import admin_bp
    app.register_blueprint(admin_bp)

    from app import models

    @app.context_processor
    def inject_cart_count():
        cart = session.get('cart', {})
        if isinstance(cart, dict):
            total_items = sum(cart.values())
            return dict(cart_item_count=total_items)
        return dict(cart_item_count=0)

    return app
