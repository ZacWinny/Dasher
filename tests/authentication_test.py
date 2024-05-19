import pytest
import os
import sys
from flask import session
from flask_login import current_user
from website.models import Customer, Restaurant
from main import app
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
from website.auth import login, customer_required, restaurant_required, logout, email_exists
# White Box
correct_user, correct_pass = 'DunkinMacleod', 'aqWsshsgdiii222'
incorrect_user, incorrect_pass = 'Dunkin Macleod', 'ee22'

@pytest.fixture
def client():
    app.config['TESTING'] = True
    with app.test_client() as client:
        yield client


def test_login_customer(client):
    # test login with correct credentials
    response = client.post('/login', data=dict(email=correct_user, password=correct_pass, user_type='customer'))
    assert response.status_code == 200
    assert session['customer'] == 'customer'
    assert isinstance(current_user._get_current_object(), Customer)



# Black Box


