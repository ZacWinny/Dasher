import pytest
import os
import sys
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from website.models import db, Restaurant, Customer, MenuItem, OrderItem
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

# set up test database
engine = create_engine('sqlite:///:memory:')
Session = sessionmaker(bind=engine)

#init db for testing
db.Model.metadata.create_all(engine)

@pytest.fixture
def session():
    session = Session()
    yield session
    session.close()


def test_restaurant_creation(session):
    restaurant = Restaurant(email="binglee@bing.com", password="sinbad", name="Binglee Snag", category="Outdoor",
                           address="4/23 Bing Street, Lee", type="hardware restaurant")
    session.add(restaurant)
    session.commit()

    assert restaurant.id is not None
    assert restaurant.email == "binglee@bing.com" 
    assert restaurant.name == "Binglee Snag" 
    assert restaurant.category == "Outdoor"
    assert restaurant.address == "4/23 Bing Street, Lee"

def test_customer_creation(session):
    customer = Customer(email="dunkin@dunk.com", name="dunk", password="dunk", address="4/23 Dunk Street, Dunk", membership=True, membership_type="Gold")
    session.add(customer)
    session.commit()

    assert customer.id is not None
    assert customer.email == "dunkin@dunk.com"
    assert customer.name == "dunk"
    assert customer.password == "dunk"
    assert customer.address == "4/23 Dunk Street, Dunk"
    assert customer.membership == True
    assert customer.membership_type == "Gold"


def test_menu_item_creation(session):
    menu_item = MenuItem(name="Burger", description="Delicious Burger", price=10.0, restaurant_id=1, image_path="/static/images/default_food.jpg")
    session.add(menu_item)
    session.commit()

    assert menu_item.id is not None
    assert menu_item.name == "Burger"
    assert menu_item.description == "Delicious Burger"
    assert menu_item.price == 10.0
    assert menu_item.restaurant_id == 1
    assert menu_item.image_path == "/static/images/default_food.jpg"


def test_order_item_creation(session):
    order_item = OrderItem(order_id=1, menu_item_id=1, quantity=2)
    session.add(order_item)
    session.commit()

    assert order_item.id is not None
    assert order_item.order_id == 1
    assert order_item.menu_item_id == 1
    assert order_item.quantity == 2


def test_restaurant_relationship(session):
    # Tests the relationship between Restaurant and MenuItem
    restaurant = Restaurant(email="jasmin1@gmail.com", password="jasmin", name="Jasmin", category="fine-dining", address="4/23 Jasmin Street, Jasmin", type="restaurant")
    menu_item = MenuItem(name="Burger", description="Delicious Burger", price=10.0, restaurant_id=1, image_path="/static/images/default_food.jpg")
    restaurant.menu_items.append(menu_item)
    session.add(restaurant)
    session.commit()

    assert restaurant.menu_items[0].name == "Burger"
    assert restaurant.menu_items[0].description == "Delicious Burger"
    assert restaurant.menu_items[0].price == 10.0
    # first receive the restaurant id
    rest_id = restaurant.id
    assert restaurant.menu_items[0].restaurant_id == rest_id
    assert restaurant.menu_items[0].image_path == "/static/images/default_food.jpg"

email = "werb@gmail.com"
password ="werb"
name = "werb"
address = "4/23 werb Street, werb"
membership = True
membership_type = "Gold"

def test_customer_relationship(session):
    # Tests the relationship between Customer and Order
    customer = Customer(email=email, password=password, name=name, address=address, membership=membership,
                        membership_type=membership_type)
    session.add(customer)
    session.commit()

def test_order_restaurant_relationship(session):
    # Tests the relationship between Order and Restaurant
    restaurant = Restaurant(email=email, password=password, name=name, category="fine-dining", address=address, type="restaurant")
    order = OrderItem(order_id=1, menu_item_id=1, quantity=2)
    restaurant.orders.append(order)
    session.add(restaurant)
    session.commit()

def test_order_customer_relationship(session):
    # Tests the relationship between Order and Customer
    customer = Customer(email=email, password=password, name=name, address=address, membership=membership,
                        membership_type=membership_type)
    order = OrderItem(order_id=1, menu_item_id=1, quantity=2)
    customer.orders.append(order)
    session.add(customer)
    session.commit()