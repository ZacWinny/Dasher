from flask_login import UserMixin
from sqlalchemy import Integer, String, Date, Time, Float

from . import db


class UserTypeMixin:
    user_type = db.Column(String(64), nullable=True)


class User(db.Model, UserMixin):
    id = db.Column(Integer, primary_key=True)
    email = db.Column(String(120), unique=True, nullable=False)
    password = db.Column(String(128), nullable=False)
    name = db.Column(String(64), nullable=True)

    def __init__(self, email, password, name):
        self.email = email
        self.password = password
        self.name = name


class Customer(User):
    __tablename__ = 'customers'

    def __init__(self, email, password, name, user_type):
        super().__init__(email, password, name)
        self.user_type = user_type


class Restaurant(User, UserTypeMixin):
    __tablename__ = 'restaurants'

    def __init__(self, email, password, name, user_type):
        super().__init__(email, password, name)
        self.user_type = user_type


class Order(db.Model):
    __tablename__ = 'orders'

    order_num = db.Column(Integer, primary_key=True, autoincrement=True)
    customer_num = db.Column(Integer, nullable=False)
    restaurant_num = db.Column(Integer, nullable=False)
    order_date = db.Column(Date, nullable=False)
    delivery_date = db.Column(Date, nullable=False)
    delivery_time = db.Column(Time, nullable=False)
    total = db.Column(Float, nullable=False)
    status = db.Column(String(50), nullable=False)


class Feedback(db.Model):
    __tablename__ = 'feedback'

    feedback_num = db.Column(Integer, primary_key=True, autoincrement=True)
    order_num = db.Column(Integer, nullable=False)
    customer_name = db.Column(String(50), nullable=False)
    restaurant_num = db.Column(Integer, nullable=False)
    feedback_date = db.Column(Date, nullable=False)
    feedback_text = db.Column(String(500), nullable=False)  #
    rating = db.Column(Integer, nullable=False)


class FoodItem(db.Model):
    __tablename__ = 'food_items'

    food_num = db.Column(Integer, primary_key=True, autoincrement=True)
    restaurant_num = db.Column(Integer, nullable=False)
    name = db.Column(String(50), nullable=False)
    price = db.Column(Float, nullable=False)
    category = db.Column(String(50), nullable=False)
