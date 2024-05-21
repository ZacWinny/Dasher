import os

from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_login import LoginManager, current_user
from flask_socketio import SocketIO

db = SQLAlchemy()
DB_NAME = "database.db"
from .models import BaseUser, Customer, Restaurant, MenuItem, OrderItem, Order

global latest_restaurant_id
latest_restaurant_id = 98


def create_app():
    app = Flask(__name__)
    app.config['SECRET_KEY'] = 'dasher dasher'
    app.config['SQLALCHEMY_DATABASE_URI'] = f'sqlite:///{DB_NAME}'
    db.init_app(app)

    from .views import views
    from .auth import auth

    app.register_blueprint(views, url_prefix='/')
    app.register_blueprint(auth, url_prefix='/')

    UPLOAD_FOLDER = 'website/static/images'  # Relative path within the project directory
    app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER

    with app.app_context():
        db.create_all()

    if not os.path.exists(app.config['UPLOAD_FOLDER']):
        os.makedirs(app.config['UPLOAD_FOLDER'])

    login_manager = LoginManager()
    login_manager.login_view = 'auth.login'
    login_manager.init_app(app)

    @login_manager.user_loader
    def load_user(id):
        user = Customer.query.get(int(id))  # First try finding the user as a Customer
        if not user:
            user = Restaurant.query.get(int(id))  # If not found, check the Restaurant table
        return user

    @app.context_processor
    def inject_flask_login():
        return dict(current_user=current_user)

    socketio = SocketIO(app)

    return app
