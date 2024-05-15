from functools import wraps
from flask import Blueprint, render_template, request, flash, redirect, url_for, abort
from .models import BaseUser, Customer, Restaurant
from . import db
from werkzeug.security import generate_password_hash, check_password_hash
from flask_login import login_user, login_required, logout_user, current_user

auth = Blueprint('auth', __name__)


@auth.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        email = request.form.get('email')
        password = request.form.get('password')

        user = db.session.query(BaseUser).filter_by(email=email).first()
        if user:
            if check_password_hash(user.password, password):
                flash('Logged in successfully.', category='success')
                login_user(user, remember=True)
                return redirect(url_for('views.home'))
            else:
                flash('Incorrect password, try again.', category='error')
        else:
            flash('Email does not exist.', category='error')

    return render_template("login.html", user=current_user)


def customer_required(func):
    @wraps(func)
    def decorated_view(*args, **kwargs):
        if not current_user.is_authenticated or not isinstance(current_user, Customer):
            abort(403)  # Forbidden access
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
                                    address=request.form.get('address'))
                db.session.add(new_user)
                db.session.commit()
            elif role == 'restaurant':
                new_user = Restaurant(email=email, password=password_hash, name=request.form.get('name'),
                                      category=request.form.get('category'), address=request.form.get('address'))
                db.session.add(new_user)
                db.session.commit()

            login_user(new_user, remember=True)
            flash('Account created.', category='success')
            return redirect(url_for('views.home'))  # Adjust if you have a different homepage

    return render_template('sign_up.html')
