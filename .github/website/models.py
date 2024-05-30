from flask_login import UserMixin
from datetime import datetime
from sqlalchemy import Integer, Column, String, DateTime, Float, ForeignKey, Boolean
from sqlalchemy.orm import relationship

from . import db


class CustomerMixin(UserMixin):
    def get_id(self):
        return self.customer_id  # Assuming your customer model has a 'customer_id' field


class RestaurantMixin(UserMixin):
    def get_id(self):
        return self.restaurant_id


class BaseUser(db.Model):
    __abstract__ = True
    email = Column(String(120), unique=True, nullable=False)
    password = Column(String(128), nullable=False)
    name = Column(String(64), nullable=True)
    address = Column(String(128), nullable=False)
    type = Column(String(50))  # Column to store 'customer' or 'restaurant'

    __mapper_args__ = {
        'polymorphic_identity': 'type',
        'polymorphic_on': type
    }


class Customer(BaseUser, CustomerMixin):
    __tablename__ = 'customers'
    __mapper_args__ = {'polymorphic_identity': 'customer'}

    customer_id = db.Column(Integer, primary_key=True)
    membership = db.Column(db.Boolean, default=False)
    membership_type = db.Column(db.String(50), nullable=True)

    orders = relationship('Order', backref='customer', lazy='dynamic')  # One-to-many relationship with Order

    def __init__(self, email, password, name, address, membership=False, membership_type=None):
        super().__init__(email=email, password=password, name=name, address=address, type='customer')  # Call parent
        # constructor
        self.membership = membership
        self.membership_type = membership_type


def generate_restaurant_id():
    latest_restaurant_id = 100  # Access the global variable
    latest_restaurant_id += 1
    # ... (rest of the ID generation logic)


class Restaurant(BaseUser, RestaurantMixin):
    __tablename__ = 'restaurants'
    __mapper_args__ = {'polymorphic_identity': 'restaurant'}

    restaurant_id = db.Column(Integer, primary_key=True)
    category = Column(String(64), nullable=False)
    average_rating = Column(Float, default=0.0)

    menu_items = relationship('MenuItem', backref='restaurant')  # One-to-many relationship with MenuItem
    orders = relationship('Order', backref='restaurant', lazy='dynamic')  # One-to-many relationship with Order

    def __init__(self, email, password, name, category, address):
        super().__init__(email=email, password=password, name=name, type='restaurant')  # Call parent constructor
        self.category = category
        self.address = address
        self.user_type = "restaurant"


class MenuItem(db.Model):
    __tablename__ = 'menu_items'

    id = Column(Integer, primary_key=True)
    name = Column(String(128), nullable=False)
    description = Column(String(128), nullable=False)
    price = Column(Float, nullable=False)
    restaurant_id = Column(Integer, ForeignKey('restaurants.restaurant_id'))
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
    customer_id = Column(Integer, ForeignKey('customers.customer_id'), nullable=False)
    restaurant_id = Column(Integer, ForeignKey('restaurants.restaurant_id'), nullable=False)
    items = relationship('OrderItem', backref='order', lazy='dynamic')  # Many-to-many relationship with OrderItem
    total_price = Column(Float, nullable=False)
    service_option = Column(String(64), nullable=False)  # e.g., "Membership", "Pay-on-Demand"
    status = Column(String(64), nullable=False)  # e.g., "Pending", "Accepted", "Rejected", "Completed"
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)  # Timestamp for order creation
    reviews = db.relationship('Review', backref='order', lazy=True)

    def __init__(self, customer_id, restaurant_id, items, total_price, service_option, status):
        self.customer_id = customer_id
        self.restaurant_id = restaurant_id
        self.items = items  # List of OrderItem objects
        self.total_price = total_price
        self.service_option = service_option
        self.status = status  # Set initial status to pending

class Review(db.Model):
    __tablename__ = 'reviews'
    id = db.Column(db.Integer, primary_key=True)
    order_id = db.Column(db.Integer, db.ForeignKey('orders.id'), nullable=False)  # Associate with the order
    rating = db.Column(db.Integer, nullable=False)
    comment = db.Column(db.Text)  # Optional comment field