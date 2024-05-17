import sqlalchemy
from sqlalchemy.orm import joinedload
from flask import Blueprint, render_template, session, flash, redirect, url_for, request, abort
from flask_login import login_required, current_user

from . import db
from .auth import customer_required
from .models import BaseUser, Customer, Restaurant, MenuItem, OrderItem, Order

views = Blueprint('views', __name__)


@views.route('/')
@login_required
def home():
    print(current_user.type)  # Add this print statement for debugging
    return render_template("home.html", user=current_user)


@views.route('/customer/dashboard')
@login_required
@customer_required
def customer_dashboard():
    recent_orders = Order.query.filter_by(customer_id=current_user.id).order_by(Order.created_at.desc()).limit(5).all()
    return render_template('customer_dashboard.html', user=current_user, recent_orders=recent_orders)


@views.route('/customer/membership', methods=['GET', 'POST'])
@login_required
@customer_required
def membership_signup():
    if request.method == 'POST':
        membership_type = request.form.get('membership_type')

        # Basic Validation
        if membership_type not in ['monthly', 'annual']:
            flash('Invalid membership type selected.', category='error')
            return render_template('membership_signup.html')

            # Update customer's membership details
        current_user.membership = True
        current_user.membership_type = membership_type
        db.session.commit()

        flash('Congratulations! You are now a member.', category='success')
        return redirect(url_for('views.customer_dashboard'))

    return render_template('membership_signup.html')


@views.route('/customer/orders')
@login_required
@customer_required
def customer_orders():
    orders = Order.query.filter_by(customer_id=current_user.id).all()
    return render_template('customer_orders.html', orders=orders)


@views.route('/order/<int:order_id>')
@login_required
@customer_required
def view_order(order_id):
    order = Order.query.get_or_404(order_id)

    # Authorization check (ensure the order belongs to the current user)
    if order.customer_id != current_user.id:
        abort(403)  # Forbidden access

    # Fetch order items and eagerly load associated menu items
    order_items = OrderItem.query.options(joinedload(OrderItem.menu_item)).filter_by(order_id=order_id).all()

    return render_template('order_details.html', order=order, order_items=order_items, user=current_user)


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

    return render_template('browse_restaurants.html', restaurants=restaurants, categories=food_categories,
                           selected_category=category,
                           user=current_user)


@views.route('/customer/restaurants/<int:restaurant_id>')
@login_required
@customer_required
def view_restaurant(restaurant_id):
    restaurant = Restaurant.query.get_or_404(restaurant_id)  # Get or return 404 if not found
    menu_items = MenuItem.query.filter_by(restaurant_id=restaurant_id).all()
    return render_template('restaurant_details.html', restaurant=restaurant, menu_items=menu_items,
                           user=current_user)


@views.route('/create-order/<int:restaurant_id>', methods=['POST'])
@login_required
@customer_required
def create_order(restaurant_id):
    if request.method == 'POST':
        if 'cart' not in session or not session['cart']:
            flash('Your cart is empty.', category='error')
            return redirect(url_for('views.view_cart'))

        # 1. Get cart items and calculate total
        cart_items = []
        total_price = 0
        for menu_item_id, quantity in session['cart'].items():
            menu_item = MenuItem.query.get(menu_item_id)
            if menu_item:
                item_price = round(menu_item.price * quantity, 2)  # Round to 2 decimal places
                total_price += item_price
                cart_items.append((menu_item, quantity, item_price))

        # 2. Input Validation (add more checks as needed)
        if not cart_items:  # Double-check if cart is still empty
            flash('Your cart is empty.', category='error')
            return redirect(url_for('views.view_cart'))

        # 3. Create and store the order (assuming no payment for now)
        order_items = []
        for menu_item, quantity, _ in cart_items:
            order_item = OrderItem(menu_item_id=menu_item.id, quantity=quantity)
            db.session.add(order_item)
            order_items.append(order_item)

        order = Order(
            customer_id=current_user.id,
            restaurant_id=cart_items[0][0].restaurant_id,
            items=order_items,  # Pass the list of order items
            total_price=round(total_price, 2),
            service_option="Membership" if current_user.membership else "Pay-on-Demand",
            status="Pending"
        )

        db.session.add(order)
        db.session.commit()

        # Clear the cart after order placement
        session.pop('cart', None)

        # 4. Flash message and redirection
        flash('Order placed successfully!', 'success')
        return redirect(url_for('views.order_confirmation', order_id=order.id))

    # ... (GET request handling for displaying the checkout page is the same as before)


@views.route('/add_to_cart/<int:menu_item_id>', methods=['POST'])
@login_required
@customer_required
def add_to_cart(menu_item_id):
    if 'cart' not in session:
        session['cart'] = {}

    cart_key = f'{menu_item_id}'

    if cart_key not in session['cart']:
        session['cart'][cart_key] = 1
    else:
        session['cart'][cart_key] += 1

    session.modified = True

    # Get the menu item object to obtain the restaurant ID
    menu_item = MenuItem.query.get(menu_item_id)
    if not menu_item:
        flash("Invalid menu item.", category="error")  # Handle invalid item (optional)
        return redirect(url_for('views.browse_restaurants'))

    # Redirect back to the restaurant's page
    return redirect(url_for('views.view_restaurant', restaurant_id=menu_item.restaurant_id, user=current_user))


@views.route('/remove_from_cart/<int:menu_item_id>', methods=['POST'])
@login_required
@customer_required
def remove_from_cart(menu_item_id):
    if 'cart' in session:
        cart_key = f'{menu_item_id}'  # Use the same key format as in add_to_cart
        if cart_key in session['cart']:
            del session['cart'][cart_key]  # Delete using cart_key
            session.modified = True
        else:
            flash("Item not found in cart.", category="error")

    # Get the restaurant ID of the menu item you are trying to remove
    menu_item = MenuItem.query.get(menu_item_id)
    if not menu_item:
        flash("Invalid menu item.", category="error")
        return redirect(url_for("views.browse_restaurants"))  # Redirect to all restaurants if invalid

    # Redirect back to the restaurant page or cart
    return redirect(url_for('views.view_cart'))


@views.route('/cart')
@login_required
@customer_required
def view_cart():
    cart_items = []
    total_price = 0

    if 'cart' in session and session['cart']:
        for menu_item_id, quantity in session['cart'].items():
            menu_item = MenuItem.query.get(menu_item_id)
            if menu_item:
                item_price = menu_item.price * quantity
                total_price += item_price
                cart_items.append((menu_item, quantity, item_price))
    else:
        # Empty cart handling for GET request in view_cart route
        flash('Your cart is empty.', category='error')
    return render_template('cart.html', cart_items=cart_items, total_price=total_price, user=current_user)


@views.route('/checkout', methods=['GET', 'POST'])
@login_required
@customer_required
def checkout():
    if request.method == 'POST':
        if 'cart' in session and session['cart']:
            # 1. Get cart items and calculate total
            cart_items = []
            total_price = 0
            for menu_item_id, quantity in session['cart'].items():
                menu_item = MenuItem.query.get(menu_item_id)
                if menu_item:
                    item_price = menu_item.price * quantity
                    total_price += item_price
                    cart_items.append((menu_item, quantity, item_price))

            # 2. Input Validation
            if not cart_items:
                flash('Your cart is empty.', category='error')
                return redirect(url_for('views.view_cart'))

            # 3. Create and store the order (assuming no payment for now)
            try:
                # Create order items first
                order_items = []
                for menu_item, quantity, _ in cart_items:
                    order_item = OrderItem(order_id=None, menu_item_id=menu_item.id,
                                           quantity=quantity)  # order_id is None
                    db.session.add(order_item)
                    order_items.append(order_item)

                order = Order(
                    customer_id=current_user.id,
                    restaurant_id=cart_items[0][0].restaurant_id,
                    items=order_items,
                    total_price=total_price,
                    service_option="Membership" if current_user.membership else "Pay-on-Demand",
                    status="Pending"
                )
                db.session.add(order)
                db.session.flush()

                # Now the order has an ID, update the order items
                for order_item in order_items:
                    order_item.order_id = order.id

                db.session.commit()

                # Clear the cart after successful order placement
                session.pop('cart', None)

            except sqlalchemy.exc.IntegrityError as e:
                db.session.rollback()
                flash('An error occurred while placing your order. Please try again.', category='error')
                return redirect(url_for('views.checkout'))  # redirect back to checkout in case of errors

        # 4. Redirect after order creation (successful or not)
        return redirect(url_for('views.view_cart'))

    else:  # GET request
        cart_items = []
        total_price = 0
        if 'cart' in session and session['cart']:
            # Calculate the total price and prepare cart items (as before)
            for menu_item_id, quantity in session['cart'].items():
                menu_item = MenuItem.query.get(menu_item_id)
                if menu_item:
                    item_price = menu_item.price * quantity
                    total_price += item_price
                    cart_items.append((menu_item, quantity, item_price))
        else:
            flash('Your cart is empty.', category='error')

        return render_template('checkout.html', cart_items=cart_items, total_price=total_price, user=current_user)
