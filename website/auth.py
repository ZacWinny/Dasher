from functools import wraps
from flask import Blueprint, render_template, request, flash, redirect, url_for, abort, session
from .models import BaseUser, Customer, Restaurant, generate_restaurant_id
from . import db, latest_restaurant_id
from werkzeug.security import generate_password_hash, check_password_hash
from flask_login import login_user, login_required, logout_user, current_user

auth = Blueprint('auth', __name__)


def find_user_by_email(email):
    """Retrieves the user object (customer or restaurant) based on email."""
    return Customer.query.filter_by(email=email).first() or Restaurant.query.filter_by(email=email).first()


@auth.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        email = request.form.get('email')
        password = request.form.get('password')
        user_type = request.form.get('user_type')

        if user_type == 'customer':
            user = Customer.query.filter_by(email=email).first()
        elif user_type == 'restaurant':
            user = Restaurant.query.filter_by(email=email).first()
        else:
            # Handle invalid user type (optional)
            flash('Invalid user type.', category='error')
            return render_template("login.html")

        if user and check_password_hash(user.password, password):
            # Use nested if/elif to set user_id based on type
            if user_type == 'customer':
                user_id = user.customer_id
            elif user_type == 'restaurant':
                user_id = user.restaurant_id
            else:
                # Shouldn't reach here, but handle unexpected case (optional)
                user_id = None

            login_user(user, remember=True)# Pass user ID instead of user object
            session['user_type'] = user_type
            flash('Logged in successfully!', category='success')

            # Redirect based on user type
            if user_type == 'customer':
                return redirect(url_for('views.home'))
            elif user_type == 'restaurant':
                return redirect(url_for('views.restaurant_dashboard'))
        else:
            flash('Incorrect email or password.', category='error')
            return render_template("login.html")

    # Render login page for GET requests
    return render_template("login.html", user=None)



def customer_required(func):
    @wraps(func)
    def decorated_view(*args, **kwargs):
        if not current_user.is_authenticated or not isinstance(current_user, Customer):
            abort(403)
        return func(*args, **kwargs)

    return decorated_view


def restaurant_required(func):
    @wraps(func)
    def decorated_view(*args, **kwargs):
        if not current_user.is_authenticated or not isinstance(current_user, Restaurant):
            abort(403)
        return func(*args, **kwargs)

    return decorated_view


@auth.route('/logout')
@login_required
def logout():
    logout_user()
    return redirect(url_for('auth.login'))


def email_exists(email):
    customer = db.session.query(Customer).filter_by(email=email).first()
    if customer:
        return True

    restaurant = db.session.query(Restaurant).filter_by(email=email).first()
    if restaurant:
        return True

    return False




@auth.route('/sign-up', methods=['GET', 'POST'])
def sign_up():
    if request.method == 'POST':
        email = request.form.get('email')
        password1 = request.form.get('password1')
        password2 = request.form.get('password2')
        role = request.form.get('role')

        if email_exists(email):
            flash("Email already exists.", category="error")
        elif len(email) < 4:
            flash('Email must be greater than 3 characters.', category='error')
        elif len(password1) < 7:
            flash('Password must be at least 7 characters.', category='error')
        elif password1 != password2:
            flash('Passwords do not match.', category='error')
        elif role not in ['customer', 'restaurant']:
            flash('Invalid role selected.', category='error')
        else:
            password_hash = generate_password_hash(password1, method='pbkdf2:sha256')
            if role == 'customer':
                new_user = Customer(email=email, password=password_hash, name=request.form.get('name'),
                                    address=request.form.get('address'))  # Set type
                db.session.add(new_user)
                db.session.commit()
            elif role == 'restaurant':
                new_user = Restaurant(email=email, password=password_hash, name=request.form.get('name'),
                                      category=request.form.get('category'), address=request.form.get('address'), )  # Set type
                latest_restaurant_id = 99
                new_user.restaurant_id = latest_restaurant_id + 1
                latest_restaurant_id += 1
                db.session.add(new_user)
                db.session.commit()

            login_user(new_user, remember=True)
            session['user_type'] = role  # Set user type in session
            flash('Account created.', category='success')
            return redirect(url_for('views.home'))

    return render_template('sign_up.html')
