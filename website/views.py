from flask import Blueprint, render_template
from flask_login import login_required, current_user

from . import db
from .auth import customer_required
from .models import BaseUser, Customer, Restaurant, MenuItem, OrderItem, Order

views = Blueprint('views', __name__)


@views.route('/')
@login_required
def home():
    return render_template("home.html", user=current_user)


@views.route('/customer/restaurants')
@login_required
@customer_required
def browse_restaurants():
    from flask import request
    from test_data import food_categories
    query = Restaurant.query

    # --- Filtering ---
    category = request.args.get('category')

    categories = db.session.query(Restaurant.category).distinct().with_entities(Restaurant.category).all()
    categories = [category[0] for category in categories]  # Extract strings from the tuples

    if category and category in categories:  # Filter only if a valid category is selected
        query = query.filter_by(category=category)

    search_query = request.args.get('search')
    if search_query:
        query = query.filter(Restaurant.name.ilike(f'%{search_query}%'))

    # (Add distance and rating filters here in future implementations)

    # --- Sorting ---
    sort_by = request.args.get('sort_by', 'name')  # Default sort by name
    if sort_by == 'rating':
        query = query.order_by(Restaurant.average_rating.desc())
    else:
        query = query.order_by(Restaurant.name)

    restaurants = query.all()
    # (Get unique categories as before)

    return render_template('browse_restaurants.html', restaurants=restaurants, categories=food_categories, selected_category=category,
                           user=current_user)


@views.route('/customer/restaurants/<int:restaurant_id>')
@login_required
@customer_required
def view_restaurant(restaurant_id):
    restaurant = Restaurant.query.get_or_404(restaurant_id)  # Get or return 404 if not found
    menu_items = MenuItem.query.filter_by(restaurant_id=restaurant_id).all()
    return render_template('restaurant_details.html', restaurant=restaurant, menu_items=menu_items,
                           user=current_user)
