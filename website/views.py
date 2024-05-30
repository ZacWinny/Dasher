from datetime import timedelta, datetime
import sqlalchemy
from sqlalchemy import func
from sqlalchemy.orm import joinedload
from flask import Blueprint, render_template, session, flash, redirect, url_for, request, abort
from flask_login import login_required, current_user
from werkzeug.utils import secure_filename
from . import db
from .auth import customer_required, restaurant_required
from .models import BaseUser, Customer, Restaurant, MenuItem, OrderItem, Order, Review
from flask_socketio import emit

views = Blueprint('views', __name__)


@views.route('/')
def home():
    from flask import request
    query = Restaurant.query

    # --- Filtering ---
    category = request.args.get('category')

    categories = db.session.query(Restaurant.category).distinct().with_entities(Restaurant.category).all()
    categories = [category[0] for category in categories]

    if category and category in categories:
        query = query.filter_by(category=category)

    search_query = request.args.get('search')
    if search_query:
        query = query.filter(Restaurant.name.ilike(f'%{search_query}%'))

    # --- Sorting ---
    sort_by = request.args.get('sort_by', 'name')
    if sort_by == 'rating':
        query = query.order_by(Restaurant.average_rating.desc())
    else:
        query = query.order_by(Restaurant.name)

    featured_restaurants = Restaurant.query.order_by(func.random()).limit(3).all()  # Select 3 random restaurants

    restaurants = query.all()

    return render_template('home.html', featured_restaurants=featured_restaurants)


@views.route('/customer/dashboard')
@login_required
@customer_required
def customer_dashboard():
    recent_orders = Order.query.filter_by(customer_id=current_user.customer_id).order_by(Order.created_at.desc()).limit(
        5).all()
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
    orders = Order.query.filter_by(customer_id=current_user.customer_id).all()
    return render_template('customer_orders.html', orders=orders)


@views.route('/order/<int:order_id>')
@login_required
@customer_required
def view_order(order_id):
    order = Order.query.get_or_404(order_id)

    # Authorization check (ensure the order belongs to the current user)
    if order.customer_id != current_user.customer_id:
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
    category_filter = request.args.get('category')
    search_query = request.args.get('search')

    categories = [row[0] for row in db.session.query(Restaurant.category).distinct().all()]  # Get unique categories

    # 1. Apply search filter
    if search_query and search_query.strip():
        query = query.filter(Restaurant.name.ilike(f'%{search_query}%'))

    # 2. Apply category filter
    if category_filter:
        query = query.filter_by(category=category_filter)

        # --- Sorting ---
    sort_by = request.args.get('sort_by', 'name')
    if sort_by == 'rating':
        query = query.order_by(Restaurant.average_rating.desc())
    else:
        query = query.order_by(Restaurant.name)

    restaurants = query.options(joinedload(Restaurant.menu_items)).all()

    for restaurant in restaurants:
        average_rating = 0
        # Filter reviews based on orders belonging to the restaurant
        reviews = Review.query.join(Order).filter(Order.restaurant_id == restaurant.restaurant_id).all()
        if reviews:
            total_rating = sum(review.rating for review in reviews)
            average_rating = total_rating / len(reviews)
        restaurant.average_rating = average_rating  # Add average_rating to restaurant object # Add average_rating to restaurant object

    # --- Check if any restaurants were found ---
    if not restaurants and category_filter:  # Check if no restaurants are found for the selected category
        flash('No restaurants found matching that category.', category='warning')
        restaurants = Restaurant.query.all()  # Display all restaurants if there were no filters
        category_filter = None  # Clear selected_category if no matching restaurants are found

    return render_template(
        'browse_restaurants.html',
        restaurants=restaurants,
        categories=food_categories,
        selected_category=category_filter,
        user=current_user
    )


@views.route('/customer/restaurants/<int:restaurant_id>')
@login_required
@customer_required
def view_restaurant(restaurant_id):
    restaurant = Restaurant.query.get_or_404(restaurant_id)

    # Fetch all orders for the restaurant
    orders = Order.query.filter_by(restaurant_id=restaurant_id).all()

    # Fetch all reviews for those orders
    order_ids = [order.id for order in orders]
    reviews = Review.query.filter(Review.order_id.in_(order_ids)).all()

    # Calculate the average rating
    if reviews:
        average_rating = sum(review.rating for review in reviews) / len(reviews)
    else:
        average_rating = 0

    menu_items = MenuItem.query.filter_by(restaurant_id=restaurant_id).all()
    return render_template(
        'restaurant_details.html',
        restaurant=restaurant,
        menu_items=menu_items,
        user=current_user,
        average_rating=average_rating
    )


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
            customer_id=current_user.customer_id,
            restaurant_id=cart_items[0][0].restaurant_id,
            items=order_items,  # Pass the list of order items
            total_price=round(total_price, 2),
            service_option="Membership" if current_user.membership else "Pay-on-Demand",
            status="Pending"
        )

        db.session.add(order)
        db.session.commit()

        emit('new_order', {'order_id': order.id}, room=f'restaurant_{restaurant_id}', namespace='/')

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

            # 3. Create and store the order
            try:
                # Create order items first
                order_items = []
                for menu_item, quantity, _ in cart_items:
                    order_item = OrderItem(order_id=None, menu_item_id=menu_item.id,
                                           quantity=quantity)  # order_id is None
                    db.session.add(order_item)
                    order_items.append(order_item)

                if current_user.membership:
                    total_price *= 0.9

                order = Order(
                    customer_id=current_user.customer_id,
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


@views.route('/submit_feedback/<int:order_id>', methods=['GET', 'POST'])
@login_required
@customer_required
def submit_feedback(order_id):
    order = Order.query.get_or_404(order_id)

    # Authoristion check (ensure the order belongs to the current user)
    if order.customer_id != current_user.customer_id:
        abort(403)  # Forbidden access

    if request.method == 'POST':
        rating = int(request.form.get('rating'))
        comment = request.form.get('comment')

        # Basic Validation (expand as needed)
        if rating < 1 or rating > 5:
            flash('Please enter a valid rating between 1 and 5.', 'error')
        else:
            review = Review(order_id=order_id, rating=rating, comment=comment)
            db.session.add(review)
            db.session.commit()
            flash('Thank you for your feedback!', 'success')
            return redirect(url_for('views.customer_orders'))  # Redirect to order history

    return render_template('submit_feedback.html', order=order)


@views.route('/restaurant/dashboard')
@login_required
# @restaurant_required
def restaurant_dashboard():
    print(session.get('user_type'))
    print(type(current_user))  # Add this line
    restaurant = Restaurant.query.get_or_404(current_user.restaurant_id)
    pending_orders = Order.query.filter_by(restaurant_id=restaurant.restaurant_id, status='Pending').all()
    return render_template('restaurant_dashboard.html', restaurant=restaurant, pending_orders=pending_orders)


@views.route('/restaurant/menu')
@login_required
@restaurant_required
def restaurant_menu():
    restaurant = Restaurant.query.get_or_404(current_user.restaurant_id)
    menu_items = MenuItem.query.filter_by(restaurant_id=restaurant.restaurant_id).all()
    return render_template('restaurant_menu.html', restaurant=restaurant, menu_items=menu_items)


@views.route('/restaurant/menu/add', methods=['GET', 'POST'])
@login_required
@restaurant_required
def add_menu_item():
    import os
    from main import app
    if request.method == 'POST':
        name = request.form.get('name')
        description = request.form.get('description')
        price = request.form.get('price')
        image = request.files.get('image')

        # 1. Form Validation
        if not name or not description or not price:
            flash('All fields are required.', category='error')
        elif not image:
            flash('Please select an image file.', category='error')
        else:
            # 2. Image Handling
            filename = secure_filename(image.filename)  # Use secure_filename for security
            image_path = os.path.join("images/", filename)
            image.save(os.path.join(app.config['UPLOAD_FOLDER'], filename))

            # 3. Create MenuItem and add to database
            try:
                new_item = MenuItem(name=name, description=description, price=price, image_path=image_path,
                                    restaurant_id=current_user.restaurant_id)
                db.session.add(new_item)
                db.session.commit()
                flash('Menu item added successfully!', category='success')
            except Exception as e:  # Add error handling (e.g., SQLAlchemy errors)
                db.session.rollback()
                flash(f'An error occurred: {e}', category='error')

        return redirect(url_for('views.restaurant_menu'))

    return render_template('add_menu_item.html')


@views.route('/restaurant/menu/edit/<int:item_id>', methods=['GET', 'POST'])
@login_required
@restaurant_required
def edit_menu_item(item_id):
    import os
    from main import app
    menu_item = MenuItem.query.get_or_404(item_id)
    if menu_item.restaurant_id != current_user.restaurant_id:
        abort(403)  # Ensure the restaurant owns the item

    if request.method == 'POST':
        name = request.form.get('name')
        description = request.form.get('description')
        price = request.form.get('price')
        image = request.files.get('image')

        # 1. Form Validation
        if not name or not description or not price:
            flash('All fields are required.', category='error')
            return render_template('edit_menu_item.html', menu_item=menu_item)  # Re-render form with errors

        # 2. Image Handling
        if image and image.filename != '':  # Check if a new image was uploaded
            filename = secure_filename(image.filename)
            image_path = os.path.join(app.config['UPLOAD_FOLDER'], filename)
            image.save(image_path)
            # Optionally, delete the old image if it exists:
            if menu_item.image_path:
                os.remove(os.path.join(app.config['UPLOAD_FOLDER'], menu_item.image_path))
        else:
            image_path = menu_item.image_path  # Keep existing image path if no new one is uploaded

        # 3. Update MenuItem
        menu_item.name = name
        menu_item.description = description
        menu_item.price = float(price)
        menu_item.image_path = image_path

        try:
            db.session.commit()
            flash('Menu item updated successfully!', category='success')
        except Exception as e:  # Add error handling (e.g., database errors)
            db.session.rollback()
            flash(f'An error occurred: {e}', category='error')

        return redirect(url_for('views.restaurant_menu'))

    return render_template('edit_menu_item.html', menu_item=menu_item)


@views.route('/restaurant/menu/delete/<int:item_id>', methods=['POST'])
@login_required
@restaurant_required
def delete_menu_item(item_id):
    menu_item = MenuItem.query.get_or_404(item_id)
    if menu_item.restaurant_id != current_user.restaurant_id:
        abort(403)  # Forbidden access

    try:
        db.session.delete(menu_item)
        db.session.commit()
        flash('Menu item deleted successfully!', category='success')
    except Exception as e:  # Catch potential errors
        db.session.rollback()
        flash(f'An error occurred while deleting the menu item: {e}', category='error')

    return redirect(url_for('views.restaurant_menu'))


@views.route('/restaurant/edit_profile', methods=['GET', 'POST'])
@login_required
@restaurant_required
def edit_restaurant_profile():
    restaurant = Restaurant.query.get(current_user.restaurant_id)
    if not restaurant:
        flash('Restaurant not found.', 'error')
        return redirect(url_for('views.restaurant_dashboard'))

    if request.method == 'POST':
        name = request.form.get('name')
        category = request.form.get('category')
        address = request.form.get('address')
        phone_number = request.form.get('phone_number')
        description = request.form.get('description')

        restaurant.name = name
        restaurant.category = category
        restaurant.address = address
        restaurant.phone_number = phone_number
        restaurant.description = description
        db.session.commit()

        flash('Profile updated successfully!', 'success')
        return redirect(url_for('views.restaurant_dashboard'))

    return render_template('edit_restaurant_profile.html', restaurant=restaurant)


@views.route('/restaurant/orders')
@login_required
@restaurant_required
def restaurant_orders():
    # Retrieve all orders for the restaurant
    restaurant = Restaurant.query.get(current_user.restaurant_id)
    orders = Order.query.filter_by(restaurant_id=restaurant.restaurant_id) \
        .order_by(Order.created_at.desc()) \
        .all()

    return render_template('restaurant_orders.html', orders=orders)


@views.route('/restaurant/order/<int:order_id>')
@login_required
@restaurant_required
def view_order_restaurant(order_id):
    order = Order.query.get_or_404(order_id)

    # Authorisation check (ensure the order belongs to the restaurant)
    if order.restaurant_id != current_user.restaurant_id:
        abort(403)  # Forbidden access

    # Fetch order items and associated menu items
    order_items = OrderItem.query.filter_by(order_id=order_id).all()

    return render_template(
        'restaurant_order_details.html',
        order=order,
        order_items=order_items,
    )


@views.route('/restaurant/orders/accept/<int:order_id>', methods=['POST'])
@login_required
@restaurant_required
def accept_order(order_id):
    order = Order.query.get_or_404(order_id)

    # Authorisation check (ensure the restaurant owns the order)
    if order.restaurant_id != current_user.restaurant_id:
        abort(403)  # Forbidden access

    order.status = 'Accepted'
    db.session.commit()
    flash('Order accepted successfully!', category='success')
    return redirect(url_for('views.restaurant_dashboard'))


@views.route('/restaurant/orders/reject/<int:order_id>', methods=['POST'])
@login_required
@restaurant_required
def reject_order(order_id):
    order = Order.query.get_or_404(order_id)

    # Authorisation check (ensure the restaurant owns the order)
    if order.restaurant_id != current_user.restaurant_id:
        abort(403)  # Forbidden access

    order.status = 'Rejected'
    db.session.commit()
    flash('Order rejected.', category='warning')
    return redirect(url_for('views.restaurant_dashboard'))


@views.route('/restaurant/orders/update_status/<int:order_id>', methods=['POST'])
@login_required
@restaurant_required
def update_order_status(order_id):
    order = Order.query.get_or_404(order_id)

    # Authorisation check (ensure the restaurant owns the order)
    if order.restaurant_id != current_user.restaurant_id:
        abort(403)  # Forbidden access

    new_status = request.form.get('new_status')
    if new_status in ['Accepted', 'In Preparation', 'Out for Delivery', 'Delivered', 'Cancelled', 'Complete']:
        order.status = new_status
        db.session.commit()
        flash('Order status updated successfully!', category='success')
    else:
        flash('Invalid order status.', category='error')

    return redirect(url_for('views.restaurant_dashboard'))  # Or redirect to order details page


@views.route('/restaurant/reports')
@login_required
@restaurant_required
def restaurant_reports():
    # Query for the restaurant's orders within a specific time frame
    start_date = request.args.get('start_date', default=datetime.utcnow() - timedelta(days=30),
                                  type=datetime.fromisoformat)
    end_date = request.args.get('end_date', default=datetime.utcnow(), type=datetime.fromisoformat)

    orders = Order.query.filter(Order.restaurant_id == current_user.restaurant_id,
                                Order.created_at >= start_date,
                                Order.created_at <= end_date).all()

    total_revenue = sum(order.total_price for order in orders)

    revenue_by_item = db.session.query(
        MenuItem.name,
        func.sum(OrderItem.quantity * MenuItem.price).label('revenue')
    ).join(OrderItem).join(Order) \
        .filter(Order.restaurant_id == current_user.restaurant_id,
                Order.created_at >= start_date,
                Order.created_at <= end_date) \
        .group_by(MenuItem.name) \
        .all()

    return render_template(
        'restaurant_reports.html',
        total_revenue=total_revenue,
        revenue_by_item=revenue_by_item,
        start_date=start_date,
        end_date=end_date
    )
