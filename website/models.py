from . import db
from flask_login import UserMixin
from sqlalchemy import Integer, Column, String
from werkzeug.security import generate_password_hash, check_password_hash

class User(db.Model, UserMixin):
    id = db.Column(Integer, primary_key=True)
    email = db.Column(String(120), unique=True, nullable=False)
    password_hash = db.Column(String(128), nullable=False)
    name = db.Column(String(64), nullable=True)
    type = db.Column(String(64), nullable=False)

    def __init__(self, email, password, type):
        self.email = email
        self.password_hash = generate_password_hash(password)
        self.type = type

    def verify_password(self, password):
        return check_password_hash(self.password_hash, password)

class Customer(User):
    __tablename__ = 'customers'  # Define separate table name

    def __init__(self, email, password, name, type):
        super().__init__(email, password, type)
        self.name = name

class Restaurant(User):
    __tablename__ = 'restaurants'  # Define separate table name

    def __init__(self, email, password, name, type):
        super().__init__(email, password, type)
        self.name = name

