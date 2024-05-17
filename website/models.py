from flask_login import UserMixin
from datetime import datetime
from sqlalchemy import Integer, Column, String, DateTime, Float, ForeignKey, Boolean
from sqlalchemy.orm import relationship

from . import db


class BaseUser(db.Model, UserMixin):
    __abstract__ = True
    id = Column(Integer, primary_key=True)
    email = Column(String(120), unique=True, nullable=False)
    password = Column(String(128), nullable=False)
    name = Column(String(64), nullable=True)
    address = Column(String(128), nullable=False)
    type = Column(String(50))  # Column to store 'customer' or 'restaurant'

    __mapper_args__ = {
        'polymorphic_identity': 'type',
        'polymorphic_on': type
    }


class Customer(BaseUser):
    __tablename__ = 'customers'
    __mapper_args__ = {'polymorphic_identity': 'customer'}

    membership = db.Column(db.Boolean, default=False)
    membership_type = db.Column(db.String(50), nullable=True)

    orders = relationship('Order', backref='customer', lazy='dynamic')  # One-to-many relationship with Order


    def __init__(self, email, password, name, address, membership=False, membership_type=None):
        super().__init__(email=email, password=password, name=name, address=address, type='customer')  # Call parent
        # constructor


        self.membership = membership
        self.membership_type = membership_type


class Restaurant(BaseUser):
    __tablename__ = 'restaurants'
    __mapper_args__ = {'polymorphic_identity': 'restaurant'}

    category = Column(String(64), nullable=False)
    average_rating = Column(Float, default=0.0)

    menu_items = relationship('MenuItem', backref='restaurant',
                              lazy='dynamic')  # One-to-many relationship with MenuItem
    orders = relationship('Order', backref='restaurant', lazy='dynamic')  # One-to-many relationship with Order

    def __init__(self, email, password, name, category, address, type):
        super().__init__(email=email, password=password, name=name, type='restaurant')  # Call parent constructor
        self.category = category
        self.address = address


class MenuItem(db.Model):
    __tablename__ = 'menu_items'

    id = Column(Integer, primary_key=True)
    name = Column(String(128), nullable=False)
    description = Column(String(128), nullable=False)
    price = Column(Float, nullable=False)
    restaurant_id = Column(Integer, ForeignKey('restaurants.id'))
    image_path = db.Column(db.String(255))

    def __init__(self, name, description, price, restaurant_id, image_path):
        self.name = name
        self.description = description
        self.price = price
        self.restaurant_id = restaurant_id
        self.image_path = image_path


class OrderItem(db.Model):
    id = Column(Integer, primary_key=True)
    order_id = Column(Integer, ForeignKey('orders.id'))
    menu_item_id = Column(Integer, ForeignKey('menu_items.id'))
    quantity = Column(Integer, nullable=False)

    menu_item = db.relationship('MenuItem', backref='order_items')

    def __init__(self, order_id, menu_item_id, quantity):
        self.order_id = order_id
        self.menu_item_id = menu_item_id
        self.quantity = quantity


class Order(db.Model):
    __tablename__ = 'orders'

    id = Column(Integer, primary_key=True)
    customer_id = Column(Integer, ForeignKey('customers.id'), nullable=False)
    restaurant_id = Column(Integer, ForeignKey('restaurants.id'), nullable=False)
    items = relationship('OrderItem', backref='order', lazy='dynamic')  # Many-to-many relationship with OrderItem
    total_price = Column(Float, nullable=False)
    service_option = Column(String(64), nullable=False)  # e.g., "Membership", "Pay-on-Demand"
    status = Column(String(64), nullable=False)  # e.g., "Pending", "Accepted", "Rejected", "Completed"
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)  # Timestamp for order creation

    def __init__(self, customer_id, restaurant_id, items, total_price, service_option, status):
        self.customer_id = customer_id
        self.restaurant_id = restaurant_id
        self.items = items  # List of OrderItem objects
        self.total_price = total_price
        self.service_option = service_option
        self.status = status # Set initial status to pending
