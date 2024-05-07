from flask import Flask
from flask_sqlalchemy import SQLAlchemy


# from website import create_app

def create_app():
    napp = Flask(__name__)
    napp.config['SQLALCHEMY_DATABASE_URI'] = 'mysql://root:dev@db/delivery'
    db = SQLAlchemy(napp)
    return napp


app = create_app()

if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0')
